"""Gorengan Radar, langkah 3: apakah skor radar SEBELUM event memprediksi siapa yang membayar?

Skor radar (11_radar_model.py, dilatih s.d. Jun 2025) dirata-rata 20 hari bursa sebelum tiap event -> radar_z
(terstandar lintas saham). Semua event 2026 ada di periode uji, jadi skornya out-of-sample.
Per event: CAR ~ radar_z [+ riwayat_suspensi] + ppk + kontrol (08), HC3.
  - koefisien radar_z negatif = saham yang "terlihat seperti gorengan" menurut model jatuh lebih dalam;
  - versi + riwayat_suspensi menguji apakah radar menambah informasi di luar label BEI.
Placebo: koefisien yang sama di hari crash biasa Agu 2025-Sep 2026 (skor validasi/uji).

Output: hasil/lanjutan/{radar_event.csv, radar_event_placebo.csv}, tambahan di ringkasan_radar.md
"""
import importlib.util
import sys
import warnings

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

import konfigurasi as k

warnings.filterwarnings("ignore")
MODEL = sys.argv[1] if len(sys.argv) > 1 else "transformer_nnpu"
JENDELA_SKOR = 20


def _modul(nama, file):
    spec = importlib.util.spec_from_file_location(nama, k.ROOT / "analisis" / file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


es = _modul("es", "02_event_study.py")
pl = _modul("pl", "04_placebo_permutasi.py")
gor = _modul("gor", "08_gorengan_event.py")
OUT = k.HASIL / "lanjutan"


def skor_sebelum(skor, tgl):
    hari = sorted(skor.loc[skor["tanggal"] < tgl, "tanggal"].unique())[-JENDELA_SKOR:]
    s = skor[skor["tanggal"].isin(hari)].groupby("ticker")[f"skor_{MODEL}"].mean()
    return s


def koef(s, y, dengan_bei):
    s = s.dropna(subset=[y, "radar_z", "log_mcap", "beta_jci", "log_amihud", "free_float", "ret_pre"])
    rumus = f"{y} ~ radar_z + ppk {'+ riwayat_suspensi' if dengan_bei else ''} + {gor.KONTROL}"
    m = smf.ols(rumus, data=s).fit(cov_type="HC3")
    return m.params["radar_z"], m.pvalues["radar_z"], int(m.nobs)


def pasang(s, skor, tgl):
    sk = skor_sebelum(skor, tgl).reindex(s.index)
    s = s.assign(radar=sk).dropna(subset=["radar"])
    return s.assign(radar_z=(s["radar"] - s["radar"].mean()) / s["radar"].std())


def main():
    skor = pd.read_csv(k.DATA_OLAH / "radar" / "skor.csv.gz")
    data = pl.siapkan()
    d = gor.sampel(data)
    baris = []
    for ev in k.EVENTS:
        s = pasang(d[d["event"] == ev].set_index("ticker"), skor, k.EVENTS[ev]["hari0"])
        for y in gor.Y:
            if s[y].isna().all():
                continue
            for bei in [False, True]:
                b, p, n = koef(s, y, bei)
                baris.append({"event": ev, "y": y, "kontrol_label_bei": bei, "koef_radar_z": b, "p": p, "n": n})
    hasil = pd.DataFrame(baris)
    # placebo hari crash biasa dengan skor tersedia
    r, px, vol, rb, static, msci, kal = data
    lab = pd.read_csv(k.DATA_OLAH / "label_pengawasan.csv", parse_dates=["date"])
    notasi = pd.read_csv(k.DATA_OLAH / "notasi_harian.csv.gz", parse_dates=["date"], usecols=["date", "ticker", "ppk"])
    hist = pd.read_csv(k.DATA_OLAH / "msci_proksi_hist.csv")
    pk = []
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
        s = pasang(s, skor, f"{tgl:%Y-%m-%d}")
        for y in gor.Y:
            if s[y].isna().all():
                continue
            for bei in [False, True]:
                pk.append({"tanggal": tgl, "y": y, "kontrol_label_bei": bei, "koef": koef(s, y, bei)[0]})
    pk = pd.DataFrame(pk)
    hasil["p_placebo"] = [((pk.loc[(pk["y"] == r_.y) & (pk["kontrol_label_bei"] == r_.kontrol_label_bei), "koef"] <= r_.koef_radar_z).sum() + 1)
                          / (((pk["y"] == r_.y) & (pk["kontrol_label_bei"] == r_.kontrol_label_bei)).sum() + 1)
                          for r_ in hasil.itertuples()]
    hasil.to_csv(OUT / f"radar_event_{MODEL}.csv", index=False)
    pk.to_csv(OUT / f"radar_event_placebo_{MODEL}.csv", index=False)
    print(f"placebo: {pk['tanggal'].nunique()} hari")
    print(hasil.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
