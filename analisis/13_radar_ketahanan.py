"""Gorengan Radar, langkah 4: uji ketahanan (seed, prior pi) dan atribusi fitur.

A. Varian: Transformer BCE seed 0/1/2, Transformer nnPU (imbalanced) seed 0/1/2 dengan pi=0,01, serta nnPU seed 0
   dengan pi=0,005 dan 0,03. Model dan skor disimpan di data/olah/radar/varian/ (bisa dilanjutkan bila terputus).
B. Untuk tiap varian: AUC/AP label di uji 2026, dan koefisien skor radar pra-event terhadap CAR (E1, JPM, E2, rating)
   dibanding 38 hari crash biasa (sama dengan 12_radar_event.py).
C. Atribusi (BCE dan nnPU seed 0): permutation importance tiap fitur terhadap (i) AUC label dan (ii) koefisien E1 [0,+5]
   -- fitur apa yang membuat skor radar memprediksi siapa yang jatuh di E1. Plus profil: skor pra-E1 ~ karakteristik saham.

Output: hasil/lanjutan/{radar_ketahanan.csv, radar_atribusi.csv, radar_profil_e1.csv, ringkasan_radar_ketahanan.md}
"""
import importlib.util
import json
import warnings

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import torch
from sklearn.metrics import average_precision_score, roc_auc_score

import konfigurasi as k

warnings.filterwarnings("ignore")


def _modul(nama, file):
    spec = importlib.util.spec_from_file_location(nama, k.ROOT / "analisis" / file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


rm = _modul("rm", "11_radar_model.py")
es = _modul("es", "02_event_study.py")
pl = _modul("pl", "04_placebo_permutasi.py")
gor = _modul("gor", "08_gorengan_event.py")
DIR = k.DATA_OLAH / "radar"
VAR = DIR / "varian"
OUT = k.HASIL / "lanjutan"
VARIAN = [  # nama, jenis, seed, pi, epoch
    ("bce_s0", "bce", 0, None, None), ("bce_s1", "bce", 1, None, 3), ("bce_s2", "bce", 2, None, 3),
    ("nnpu_s0", "nnpu", 0, 0.01, None), ("nnpu_s1", "nnpu", 1, 0.01, 5), ("nnpu_s2", "nnpu", 2, 0.01, 5),
    ("nnpu_pi005_s0", "nnpu", 0, 0.005, 5), ("nnpu_pi03_s0", "nnpu", 0, 0.03, 5),
]
SEL = [("E1", "car_0", False), ("E1", "car_0_1", False), ("E1", "car_0_5", False), ("E1", "car_0_5", True),
       ("JPM", "car_0_1", False), ("JPM", "car_0_1", True), ("E2", "car_0_1", False), ("E2", "car_0_5", False),
       ("MDY", "car_0_5", False), ("FCH", "car_0_5", False)]


# ================================================================ A. latih varian
def model_varian(d, L, nama, jenis, seed, pi, epoch):
    VAR.mkdir(parents=True, exist_ok=True)
    berkas = VAR / f"{nama}.pt"
    m = rm.Radar(d["X"].shape[1], d["S"].shape[1], L)
    if berkas.exists():
        m.load_state_dict(torch.load(berkas))
    elif epoch is None:  # seed 0 sudah dilatih di 11
        m.load_state_dict(torch.load(DIR / f"transformer_{jenis}.pt"))
        torch.save(m.state_dict(), berkas)
    else:
        m, kurva = rm.latih_transformer(d, L, jenis, seed=seed, epoch=epoch, langkah=200, pi=pi, val_n=40_000)
        torch.save(m.state_dict(), berkas)
        pd.DataFrame(kurva).assign(varian=nama).to_csv(VAR / f"{nama}_kurva.csv", index=False)
    return m


def skor_varian(m, d, L, nama, vt):
    f = VAR / f"{nama}_skor.npy"
    if not f.exists():
        np.save(f, rm.prediksi(m, d, L, vt))
    return np.load(f)


# ================================================================ B. uji event
def siapkan_sampel(data):
    """Sampel event (8) dan placebo (hari crash biasa >= Agu 2025), dibangun SEKALI untuk semua varian."""
    r, px, vol, rb, static, msci, kal = data
    ev = {e: g.set_index("ticker") for e, g in gor.sampel(data).groupby("event")}
    lab = pd.read_csv(k.DATA_OLAH / "label_pengawasan.csv", parse_dates=["date"])
    notasi = pd.read_csv(k.DATA_OLAH / "notasi_harian.csv.gz", parse_dates=["date"], usecols=["date", "ticker", "ppk"])
    hist = pd.read_csv(k.DATA_OLAH / "msci_proksi_hist.csv")
    plac = {}
    for i, _ in gor.hari_buruk(rb, kal):
        tgl = kal[i]
        if tgl < pd.Timestamp("2025-08-01"):
            continue
        snap = hist.loc[pd.to_datetime(hist["snapshot"]) <= tgl, "snapshot"].max()
        m = pd.DataFrame({"ticker": hist.loc[hist["snapshot"] == snap, "ticker"], "bobot": 1.0, "event": "PL"})
        s, _ = es.bangun_sampel("PL", {"hari0": f"{tgl:%Y-%m-%d}"}, r, px, vol, rb, static, m, None)
        s = s[s["vol_0"].fillna(0) > 0]
        w = lab[(lab["date"] >= kal[i - 250]) & (lab["date"] < tgl)].groupby("ticker")["suspensi_was"].sum()
        s["riwayat_suspensi"] = (w.reindex(s.index).fillna(0) > 0).astype(int)
        seb = notasi[notasi["date"] < tgl]
        s["ppk"] = seb[seb["date"] == seb["date"].max()].set_index("ticker")["ppk"].reindex(s.index).fillna(0)
        plac[f"{tgl:%Y-%m-%d}"] = s
    return ev, plac


def rata_pra(skor_ser, tgl_arr, tk_arr, tgl, n=20):
    hari = np.unique(tgl_arr[tgl_arr < tgl])[-n:]
    m = np.isin(tgl_arr, hari)
    return pd.Series(skor_ser[m]).groupby(tk_arr[m]).mean()


def koef_radar(s, radar, y, bei):
    s = s.assign(radar=radar.reindex(s.index)).dropna(subset=["radar", y, "log_mcap", "beta_jci", "log_amihud", "free_float", "ret_pre"])
    s = s.assign(radar_z=(s["radar"] - s["radar"].mean()) / s["radar"].std())
    m = smf.ols(f"{y} ~ radar_z + ppk {'+ riwayat_suspensi' if bei else ''} + {gor.KONTROL}", data=s).fit(cov_type="HC3")
    return m.params["radar_z"], m.pvalues["radar_z"]


def uji_event(skor, tgl_vt, tk_vt, ev, plac):
    baris = []
    pk = {}
    for t, s in plac.items():
        rad = rata_pra(skor, tgl_vt, tk_vt, t)
        for y in ["car_0", "car_0_1", "car_0_5"]:
            for bei in [False, True]:
                if not s[y].isna().all():
                    pk.setdefault((y, bei), []).append(koef_radar(s, rad, y, bei)[0])
    for e, y, bei in SEL:
        rad = rata_pra(skor, tgl_vt, tk_vt, k.EVENTS[e]["hari0"])
        b, p = koef_radar(ev[e], rad, y, bei)
        dist = np.array(pk[(y, bei)])
        baris.append({"sel": f"{e} {y}{' +BEI' if bei else ''}", "koef": b, "p": p,
                      "p_placebo": ((dist <= b).sum() + 1) / (len(dist) + 1)})
    return baris


# ================================================================ C. atribusi
@torch.no_grad()
def skor_permutasi(m, d, L, idx, f_harian=None, f_statis=None, seed=0):
    rng = np.random.default_rng(seed)
    out = []
    for i in range(0, len(idx), 8192):
        x, s = rm.jendela(d, L, idx[i:i + 8192])
        if f_harian is not None:
            x[:, :, f_harian] = x[rng.permutation(len(x)), :, f_harian]
        if f_statis is not None:
            s[:, f_statis] = s[rng.permutation(len(s)), f_statis]
        m.eval()
        out.append(m(torch.from_numpy(x), torch.from_numpy(s)).numpy())
    return np.concatenate(out)


def atribusi(m, nama, d, L, cfg, ev):
    idx, bag, y, tgl, tk = d["idx"], d["bagian"], d["y"], d["tanggal"], d["ticker"]
    te = idx[bag == 2]
    sub = np.sort(np.random.default_rng(1).choice(te, 40_000, replace=False))
    e1 = k.EVENTS["E1"]["hari0"]
    hari = np.unique(tgl[idx][tgl[idx] < e1])[-20:]
    pra = idx[np.isin(tgl[idx], hari)]
    dasar_auc = roc_auc_score(y[sub], skor_permutasi(m, d, L, sub))
    dasar_e1 = koef_radar(ev["E1"], pd.Series(skor_permutasi(m, d, L, pra)).groupby(tk[pra]).mean(), "car_0_5", False)[0]
    baris = []
    fitur = [("harian", j, n) for j, n in enumerate(cfg["harian"])] + [("statis", j, n) for j, n in enumerate(cfg["statis"])]
    for jenis, j, n in fitur:
        kw = {"f_harian": j} if jenis == "harian" else {"f_statis": j}
        auc = roc_auc_score(y[sub], skor_permutasi(m, d, L, sub, **kw))
        b = koef_radar(ev["E1"], pd.Series(skor_permutasi(m, d, L, pra, **kw)).groupby(tk[pra]).mean(), "car_0_5", False)[0]
        baris.append({"model": nama, "fitur": n, "jenis": jenis, "turun_auc": dasar_auc - auc,
                      "koef_e1_tanpa_fitur": b, "perubahan_koef_e1": b - dasar_e1})
        print(baris[-1], flush=True)
    return pd.DataFrame(baris), dasar_auc, dasar_e1


def profil(skor, tgl_vt, tk_vt, ev):
    """Skor pra-E1 dijelaskan oleh karakteristik saham apa? (deskriptif)"""
    s = ev["E1"].assign(radar=rata_pra(skor, tgl_vt, tk_vt, k.EVENTS["E1"]["hari0"]).reindex(ev["E1"].index)).dropna(
        subset=["radar", "log_mcap", "log_amihud", "free_float", "beta_jci", "ret_pre"])
    s = s.assign(radar_z=(s["radar"] - s["radar"].mean()) / s["radar"].std(), harga_log=np.log(s["px_pre"]))
    kol = ["log_mcap", "log_amihud", "free_float", "beta_jci", "ret_pre", "harga_log", "ppk", "riwayat_suspensi", "bank"]
    z = s[kol].apply(lambda c: (c - c.mean()) / c.std())
    m = smf.ols("radar_z ~ " + " + ".join(kol), data=z.assign(radar_z=s["radar_z"])).fit(cov_type="HC3")
    return pd.DataFrame({"karakteristik": kol, "koef_per_sd": [m.params[c] for c in kol], "p": [m.pvalues[c] for c in kol]}), m.rsquared


def md(df, fmt="{:.3f}"):
    kol = df.columns.tolist()
    b = ["| " + " | ".join(kol) + " |", "|" + "---|" * len(kol)]
    for _, r in df.iterrows():
        b.append("| " + " | ".join(fmt.format(v) if isinstance(v, float) else str(v) for v in r) + " |")
    return "\n".join(b)


def main():
    d, cfg = rm.muat()
    L = cfg["L"]
    idx, bag, y = d["idx"], d["bagian"], d["y"]
    va, te = idx[bag == 1], idx[bag == 2]
    vt = np.r_[va, te]
    tgl_vt, tk_vt = d["tanggal"][vt], d["ticker"][vt]
    model, skor = {}, {}
    for nama, jenis, seed, pi, epoch in VARIAN:
        model[nama] = model_varian(d, L, nama, jenis, seed, pi, epoch)
        skor[nama] = skor_varian(model[nama], d, L, nama, vt)
        print("siap:", nama, flush=True)
    lama = pd.read_csv(DIR / "skor.csv.gz")
    for n in ["gradient_boosting", "logistik"]:
        skor[n] = lama[f"skor_{n}"].to_numpy()
    data = pl.siapkan()
    ev, plac = siapkan_sampel(data)
    baris = []
    nte = len(te)
    for nama, s in skor.items():
        lbl = {"varian": nama, "auc_uji": roc_auc_score(y[te], s[-nte:]), "ap_uji": average_precision_score(y[te], s[-nte:])}
        for r_ in uji_event(s, tgl_vt, tk_vt, ev, plac):
            baris.append({**lbl, **r_})
        print("event:", nama, flush=True)
    kt = pd.DataFrame(baris)
    kt.to_csv(OUT / "radar_ketahanan.csv", index=False)
    atr, prof = [], []
    for nama in ["bce_s0", "nnpu_s0"]:
        a, auc0, e10 = atribusi(model[nama], nama, d, L, cfg, ev)
        atr.append(a.assign(auc_dasar=auc0, koef_e1_dasar=e10))
        p, r2 = profil(skor[nama], tgl_vt, tk_vt, ev)
        prof.append(p.assign(model=nama, r2=r2))
    atr, prof = pd.concat(atr), pd.concat(prof)
    atr.to_csv(OUT / "radar_atribusi.csv", index=False)
    prof.to_csv(OUT / "radar_profil_e1.csv", index=False)
    pv = kt.pivot_table(index="varian", columns="sel", values="koef")
    pp = kt.pivot_table(index="varian", columns="sel", values="p_placebo")
    tabel = (pv.round(2).astype(str) + " (" + pp.round(3).astype(str) + ")").reset_index()
    auc = kt.drop_duplicates("varian")[["varian", "auc_uji", "ap_uji"]]
    print(tabel.to_string(index=False))
    teks = ["# Gorengan Radar: uji ketahanan", "",
            "## Akurasi label (uji 2026)", "", md(auc.round(3)), "",
            "## Koefisien skor radar pra-event (pp per SD) dan p placebo (38 hari crash biasa; minimum 0,026)", "",
            md(tabel), "",
            "## Atribusi: permutasi fitur (turun AUC label; perubahan koefisien E1 [0,+5], positif = sinyal E1 melemah)", "",
            md(atr[["model", "fitur", "jenis", "turun_auc", "perubahan_koef_e1"]].round(3)), "",
            "## Profil skor pra-E1 (radar_z ~ karakteristik terstandar)", "", md(prof.round(3))]
    (OUT / "ringkasan_radar_ketahanan.md").write_text("\n".join(teks), encoding="utf-8")


if __name__ == "__main__":
    main()
