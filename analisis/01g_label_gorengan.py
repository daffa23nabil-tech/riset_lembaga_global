"""Label pengawasan BEI per saham per hari: UMA dan suspensi (bahan Gorengan Radar dan uji event).

Input : data/mentah/idx/uma.csv (Okt 2023-), suspensi.csv (Okt 2023-), harian_2025_2026.csv.gz (kalender bursa)
Output: data/olah/label_pengawasan.csv (ticker, date, uma, suspensi_was, suspensi_emiten, unsuspensi)
        data/olah/riwayat_pengawasan_event.csv (ticker, event, n_uma_250, n_susp_was_250, riwayat_uma,
        riwayat_suspensi)

Suspensi asal 'pengawasan_perdagangan' (surat Divisi Pengawasan Transaksi) umumnya cooling down setelah kenaikan
harga kumulatif signifikan, jadi dipakai sebagai label positif bersama UMA. Suspensi 'keterbukaan_emiten' (laporan
keuangan, biaya pencatatan, gagal bayar) tidak dihitung sebagai sinyal gorengan.
Label hanya untuk analisis agregat; skor per saham tidak dipublikasikan (etika proyek).
"""
import pandas as pd

import konfigurasi as k

DIR = k.DATA_MENTAH / "idx"
JENDELA_RIWAYAT = 250  # hari bursa sebelum event


def main():
    uma = pd.read_csv(DIR / "uma.csv", comment="#", parse_dates=["tanggal"])
    sus = pd.read_csv(DIR / "suspensi.csv", comment="#", parse_dates=["waktu"])
    # pengumuman setelah jam bursa (>= 16.00) baru berlaku di hari bursa berikutnya
    kal = pd.DatetimeIndex(sorted(pd.read_csv(DIR / "harian_2025_2026.csv.gz", usecols=["date"], parse_dates=["date"])["date"].unique()))
    kal_lama = pd.bdate_range("2023-10-01", kal[0] - pd.Timedelta(days=1))
    kal = kal_lama.append(kal)

    def ke_hari_bursa(t):
        i = kal.searchsorted(t.normalize() + (pd.Timedelta(days=1) if t.hour >= 16 else pd.Timedelta(0)))
        return kal[min(i, len(kal) - 1)]

    uma["date"] = uma["tanggal"].map(ke_hari_bursa)
    sus["date"] = sus["waktu"].map(ke_hari_bursa)
    lab = pd.concat([
        uma.assign(kolom="uma")[["ticker", "date", "kolom"]],
        sus[(sus["jenis"] == "SPT") & (sus["asal"] == "pengawasan_perdagangan")].assign(kolom="suspensi_was")[["ticker", "date", "kolom"]],
        sus[(sus["jenis"] == "SPT") & (sus["asal"] != "pengawasan_perdagangan")].assign(kolom="suspensi_emiten")[["ticker", "date", "kolom"]],
        sus[sus["jenis"] == "UPT"].assign(kolom="unsuspensi")[["ticker", "date", "kolom"]],
    ])
    lab = lab[lab["ticker"].astype(str).str.fullmatch(r"[A-Z]{4}")]  # buang baris gabungan seperti '>1 Kode'
    lab = lab.assign(n=1).pivot_table(index=["ticker", "date"], columns="kolom", values="n", aggfunc="sum", fill_value=0).reset_index()
    lab.to_csv(k.DATA_OLAH / "label_pengawasan.csv", index=False)

    baris = []
    for ev, c in k.EVENTS.items():
        t0 = kal.searchsorted(pd.Timestamp(c["hari0"]))
        lo = kal[max(t0 - JENDELA_RIWAYAT, 0)]
        x = lab[(lab["date"] >= lo) & (lab["date"] < kal[t0])].groupby("ticker")[["uma", "suspensi_was"]].sum()
        x = x.rename(columns={"uma": "n_uma_250", "suspensi_was": "n_susp_was_250"}).assign(event=ev).reset_index()
        baris.append(x)
    r = pd.concat(baris)
    r["riwayat_uma"] = ((r["n_uma_250"] + r["n_susp_was_250"]) > 0).astype(int)
    r["riwayat_suspensi"] = (r["n_susp_was_250"] > 0).astype(int)  # sinyal lebih keras: sampai di-cooling down
    r.to_csv(k.DATA_OLAH / "riwayat_pengawasan_event.csv", index=False)
    print(f"Label pengawasan: {int(lab['uma'].sum())} UMA, {int(lab['suspensi_was'].sum())} suspensi pengawasan, "
          f"{lab['ticker'].nunique()} saham; riwayat 250 hari per event: "
          + ", ".join(f"{e} {int(g['riwayat_uma'].sum())}/{int(g['riwayat_suspensi'].sum())}" for e, g in r.groupby("event", sort=False))
          + " (UMA atau suspensi / suspensi pengawasan)")


if __name__ == "__main__":
    main()
