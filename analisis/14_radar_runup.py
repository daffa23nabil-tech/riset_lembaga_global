"""Gorengan Radar, langkah 5: apakah sinyal radar di E1 sekadar pembalikan setelah kenaikan tajam (run-up reversal)?

Skor radar tinggi berkorelasi dengan return pra-event (+0,4 SD). Bila radar hanya menangkap "saham yang sudah naik
akan turun", efeknya harus hilang setelah run-up dikendalikan secara fleksibel. Spesifikasi (CAR ~ radar_z + ppk +
kontrol 08, HC3), masing-masing dibanding 38 hari crash biasa:
  S1 dasar (return pra-event linear, seperti 12/13)
  S2 + run-up fleksibel: desil return pra-event (FE), return 5 dan 20 hari terakhir, return harian maksimum 20 hari (MAX)
  S3 radar ortogonal: radar_z dibersihkan dari semua ukuran run-up (residual), lalu dipakai di S2
  S4 interaksi radar_z x run-up (z): apakah efek radar hanya ada di saham yang sudah naik?
  S5 subsampel saham TANPA run-up (return pra-event <= median)
Skor: nnPU seed 0, BCE seed 0, dan rata-rata 8 varian Transformer (ensembel).

Output: hasil/lanjutan/{radar_runup.csv, ringkasan_radar_runup.md}
"""
import importlib.util
import warnings

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

import konfigurasi as k

warnings.filterwarnings("ignore")


def _modul(nama, file):
    spec = importlib.util.spec_from_file_location(nama, k.ROOT / "analisis" / file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


rk = _modul("rk", "13_radar_ketahanan.py")
pl = _modul("pl", "04_placebo_permutasi.py")
gor = _modul("gor", "08_gorengan_event.py")
OUT = k.HASIL / "lanjutan"
RUNUP = ["ret5", "ret20", "max20"]
SEL = [("E1", "car_0_5"), ("E1", "car_0_1"), ("JPM", "car_0_1")]


def tambah_runup(s, r, tgl):
    """Return 5/20 hari terakhir dan return harian maksimum 20 hari sebelum tgl (dalam %)."""
    t0 = int(np.searchsorted(r.index, pd.Timestamp(tgl)))
    w20 = r.iloc[t0 - 20:t0].reindex(columns=s.index)
    return s.assign(ret5=w20.iloc[-5:].sum().values * 100, ret20=w20.sum().values * 100,
                    max20=w20.max().values * 100)


def siapkan(s, radar):
    s = s.assign(radar=radar.reindex(s.index)).dropna(
        subset=["radar", "log_mcap", "beta_jci", "log_amihud", "free_float", "ret_pre"] + RUNUP)
    s = s.assign(radar_z=(s["radar"] - s["radar"].mean()) / s["radar"].std())
    for c in RUNUP + ["ret_pre"]:
        w = s[c].clip(s[c].quantile(0.01), s[c].quantile(0.99))
        s[c + "_z"] = (w - w.mean()) / w.std()
    s["desil_pra"] = pd.qcut(s["ret_pre"], 10, labels=False, duplicates="drop")
    run = " + ".join(c + "_z" for c in RUNUP)
    s["radar_orto"] = smf.ols(f"radar_z ~ ret_pre_z + {run} + C(desil_pra)", data=s).fit().resid
    s["radar_orto"] = s["radar_orto"] / s["radar_orto"].std()
    s["runup_z"] = s[["ret_pre_z", "ret20_z", "max20_z"]].mean(1)
    return s


def koef(s, y, spes):
    s = s.dropna(subset=[y])
    run = " + ".join(c + "_z" for c in RUNUP)
    if spes == "S1 dasar":
        f, v = f"{y} ~ radar_z + ppk + {gor.KONTROL}", "radar_z"
    elif spes == "S2 + run-up fleksibel":
        f, v = f"{y} ~ radar_z + ppk + {gor.KONTROL} + {run} + C(desil_pra)", "radar_z"
    elif spes == "S3 radar ortogonal":
        f, v = f"{y} ~ radar_orto + ppk + {gor.KONTROL} + {run} + C(desil_pra)", "radar_orto"
    elif spes == "S4 interaksi (radar x run-up)":
        f, v = f"{y} ~ radar_z * runup_z + ppk + {gor.KONTROL} + {run}", "radar_z:runup_z"
    elif spes == "S4 efek utama saat run-up = 0":
        f, v = f"{y} ~ radar_z * runup_z + ppk + {gor.KONTROL} + {run}", "radar_z"
    else:  # S5
        s = s[s["ret_pre"] <= s["ret_pre"].median()]
        f, v = f"{y} ~ radar_z + ppk + {gor.KONTROL}", "radar_z"
    m = smf.ols(f, data=s).fit(cov_type="HC3")
    return m.params[v], m.pvalues[v], int(m.nobs)


SPES = ["S1 dasar", "S2 + run-up fleksibel", "S3 radar ortogonal", "S4 interaksi (radar x run-up)",
        "S4 efek utama saat run-up = 0", "S5 tanpa run-up (<= median)"]


def md(df, fmt="{:.3f}"):
    kol = df.columns.tolist()
    b = ["| " + " | ".join(kol) + " |", "|" + "---|" * len(kol)]
    for _, r in df.iterrows():
        b.append("| " + " | ".join(fmt.format(v) if isinstance(v, float) else str(v) for v in r) + " |")
    return "\n".join(b)


def main():
    d, cfg = rk.rm.muat()
    idx, bag = d["idx"], d["bagian"]
    vt = np.r_[idx[bag == 1], idx[bag == 2]]
    tgl_vt, tk_vt = d["tanggal"][vt], d["ticker"][vt]
    skor = {n: np.load(rk.VAR / f"{n}_skor.npy") for n, *_ in rk.VARIAN}
    z = lambda a: (a - a.mean()) / a.std()
    skor_pakai = {"nnpu_s0": skor["nnpu_s0"], "bce_s0": skor["bce_s0"],
                  "ensembel_8": np.mean([z(v) for v in skor.values()], axis=0)}
    data = pl.siapkan()
    r = data[0]
    ev, plac = rk.siapkan_sampel(data)
    ev = {e: tambah_runup(s, r, k.EVENTS[e]["hari0"]) for e, s in ev.items()}
    plac = {t: tambah_runup(s, r, t) for t, s in plac.items()}
    baris = []
    for nama, sk in skor_pakai.items():
        pk = {}
        for t, s in plac.items():
            ss = siapkan(s, rk.rata_pra(sk, tgl_vt, tk_vt, t))
            for y in sorted({y for _, y in SEL}):  # satu kali per dependen (E1 dan JPM sama-sama car_0_1)
                for sp in SPES:
                    pk.setdefault((y, sp), []).append(koef(ss, y, sp)[0])
        for e, y in SEL:
            ss = siapkan(ev[e], rk.rata_pra(sk, tgl_vt, tk_vt, k.EVENTS[e]["hari0"]))
            for sp in SPES:
                b, p, n = koef(ss, y, sp)
                dist = np.array(pk[(y, sp)])
                baris.append({"skor": nama, "sel": f"{e} {y}", "spesifikasi": sp, "koef": b, "p": p, "n": n,
                              "p_placebo": ((dist <= b).sum() + 1) / (len(dist) + 1)})
        print("selesai:", nama, flush=True)
    h = pd.DataFrame(baris)
    h.to_csv(OUT / "radar_runup.csv", index=False)
    print(h.round(3).to_string(index=False))
    teks = ["# Apakah sinyal radar sekadar run-up reversal?", "",
            "Koefisien = pp CAR per SD skor radar (S4 interaksi: per SD radar x SD run-up). p_placebo = porsi 38 hari crash "
            "biasa dengan koefisien <= event (minimum 0,026). Run-up = return pra-event (hari -60 s.d. -2), return 5 dan 20 hari "
            "terakhir, dan return harian maksimum 20 hari.", "", md(h.round(3))]
    (OUT / "ringkasan_radar_runup.md").write_text("\n".join(teks), encoding="utf-8")


if __name__ == "__main__":
    main()
