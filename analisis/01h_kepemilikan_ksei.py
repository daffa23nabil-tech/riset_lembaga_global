"""Kepemilikan saham bulanan per tipe dan klasifikasi investor (KSEI, dirilis BEI).

Input : data/mentah/idx/kepemilikan/*-tipe.xlsx        (posisi akhir bulan: 9 tipe x <5% / >=5%; lokal/asing mulai Jan 2026,
                                                        asal = "total" untuk Nov-Des 2025)
        data/mentah/idx/kepemilikan/*-klasifikasi.xlsx (posisi akhir bulan: ±39 klasifikasi; lokal/asing mulai Sep 2026)
Output: data/olah/kepemilikan_tipe.csv.gz         (date, ticker, asal, tipe, saham_lt5, saham_ge5, saham)
        data/olah/kepemilikan_klasifikasi.csv.gz  (date, ticker, asal, klasifikasi, saham)
        data/olah/kepemilikan_total.csv.gz        (date, ticker, saham_tercatat, scripless)

Tipe investor KSEI: CP korporasi, FD yayasan, IB lembaga keuangan, ID individu, IS asuransi, MF reksa dana,
OT lainnya, PF dana pensiun, SC perusahaan efek.
"""
import re

import pandas as pd

import konfigurasi as k

DIR = k.DATA_MENTAH / "idx" / "kepemilikan"
TIPE = ["CP", "FD", "IB", "ID", "IS", "MF", "OT", "PF", "SC"]


def baris_data(df):
    """Indeks baris pertama yang kolom 0-nya berupa tanggal."""
    tgl = pd.to_datetime(df.iloc[:, 0], errors="coerce")
    return int(tgl.notna().idxmax()), tgl


def baca_tipe(f):
    df = pd.read_excel(f, header=None)
    mulai, tgl = baris_data(df)
    x = df.iloc[mulai:].reset_index(drop=True)
    x = x[pd.to_datetime(x[0], errors="coerce").notna()]
    # format 2026: lokal dan asing terpisah (40 kolom); format 2025: total per tipe saja (22 kolom)
    daftar_asal = ["lokal", "asing"] if df.shape[1] >= 3 + 4 * len(TIPE) + 1 else ["total"]
    total = pd.DataFrame({"date": pd.to_datetime(x[0]), "ticker": x[1].astype(str).str.strip(),
                          "saham_tercatat": pd.to_numeric(x[2], errors="coerce"),
                          "scripless": pd.to_numeric(x[3 + 2 * len(daftar_asal) * len(TIPE)], errors="coerce")})
    baris = []
    for a, asal in enumerate(daftar_asal):
        for t, tipe in enumerate(TIPE):
            c = 3 + a * 2 * len(TIPE) + 2 * t
            lt5 = pd.to_numeric(x[c], errors="coerce").fillna(0)
            ge5 = pd.to_numeric(x[c + 1], errors="coerce").fillna(0)
            baris.append(pd.DataFrame({"date": total["date"], "ticker": total["ticker"], "asal": asal, "tipe": tipe,
                                       "saham_lt5": lt5.values, "saham_ge5": ge5.values, "saham": (lt5 + ge5).values}))
    return pd.concat(baris, ignore_index=True), total


def baca_klasifikasi(f):
    df = pd.read_excel(f, header=None)
    kepala = int(df.index[df.iloc[:, 0].astype(str).str.strip().str.upper() == "DATE"][0])
    nama = [re.sub(r"\s+", "_", c) if c.upper() in ("SHARE CODE", "ISSUER NAME") else c
            for c in df.iloc[kepala].astype(str).str.strip().tolist()]
    x = df.iloc[kepala + 1:].copy()
    x.columns = nama
    x = x[pd.to_datetime(x["DATE"], errors="coerce").notna()]
    kol = [c for c in nama if c not in ("DATE", "SHARE_CODE", "ISSUER_NAME") and not c.lower().startswith("total") and c != "nan"]
    panjang = x.melt(id_vars=["DATE", "SHARE_CODE"], value_vars=kol, var_name="kolom", value_name="saham")
    # Mar-Agu 2026: klasifikasi tanpa pemisahan lokal/asing; mulai Sep 2026: Local_<klasifikasi> / Foreign_<klasifikasi>
    pisah = panjang["kolom"].str.match(r"^(Local|Foreign)_")
    panjang["asal"] = "total"
    panjang.loc[pisah, "asal"] = panjang.loc[pisah, "kolom"].str.startswith("Local").map({True: "lokal", False: "asing"})
    panjang["klasifikasi"] = panjang["kolom"].where(~pisah, panjang["kolom"].str.split("_", n=1).str[1]).str.strip().str.title()
    panjang["saham"] = pd.to_numeric(panjang["saham"], errors="coerce").fillna(0)
    return pd.DataFrame({"date": pd.to_datetime(panjang["DATE"]), "ticker": panjang["SHARE_CODE"].astype(str).str.strip(),
                         "asal": panjang["asal"], "klasifikasi": panjang["klasifikasi"], "saham": panjang["saham"]})


def main():
    tipe, total = zip(*[baca_tipe(f) for f in sorted(DIR.glob("*-tipe.xlsx"))])
    tipe = pd.concat(tipe).drop_duplicates(["date", "ticker", "asal", "tipe"])
    total = pd.concat(total).drop_duplicates(["date", "ticker"])
    kl = pd.concat([baca_klasifikasi(f) for f in sorted(DIR.glob("*-klasifikasi.xlsx"))]).drop_duplicates(["date", "ticker", "asal", "klasifikasi"])
    tipe.to_csv(k.DATA_OLAH / "kepemilikan_tipe.csv.gz", index=False)
    total.to_csv(k.DATA_OLAH / "kepemilikan_total.csv.gz", index=False)
    kl.to_csv(k.DATA_OLAH / "kepemilikan_klasifikasi.csv.gz", index=False)
    # cek: jumlah semua tipe = total scripless
    cek = tipe.groupby(["date", "ticker"])["saham"].sum().to_frame().join(total.set_index(["date", "ticker"])["scripless"])
    beda = ((cek["saham"] - cek["scripless"]).abs() > 1).mean()
    print(f"Kepemilikan KSEI: tipe {tipe['date'].nunique()} bulan ({tipe['date'].min():%Y-%m-%d} s.d. {tipe['date'].max():%Y-%m-%d}), "
          f"{tipe['ticker'].nunique()} saham; klasifikasi {kl['date'].nunique()} bulan, {kl['klasifikasi'].nunique()} klasifikasi; "
          f"selisih jumlah tipe vs total scripless: {beda:.1%} baris")


if __name__ == "__main__":
    main()
