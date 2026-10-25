"""Membaca workbook hasil template Refinitiv (rumus TR) menjadi tabel di data/olah/.

Pemakaian: python 01_baca_refinitiv.py [file.xlsx ...]
Tanpa argumen: membaca data/mentah/data-refinitiv.xlsx (satu file hasil template).
Workbook harus sudah berisi nilai (simpan setelah semua TR() selesai, atau Paste Values).

Output inti (dipakai 02/03): harga.csv.gz, bench.csv, static.csv, msci.csv.
Output tambahan: konstituen_ihsg.csv, msci_hist.csv, ftse_hist.csv, static_hist.csv, tambahan_<nama>.csv.
"""
import re
import sys

import pandas as pd

import konfigurasi as k
import olah

R = k.REF


def baca_blok(df: pd.DataFrame, c: int, nama: list) -> pd.DataFrame:
    """Ambil satu blok hasil TR() mulai kolom c: Instrument + kolom `nama` (posisional).

    Baris header, pesan error, dan sel kosong dibuang: yang disimpan hanya baris yang
    instrumennya berupa RIC (mengandung titik atau '=') dan punya minimal satu nilai.
    """
    if c >= df.shape[1]:
        return pd.DataFrame(columns=["Instrument"] + nama)
    b = df.iloc[1:, c:c + 1 + len(nama)].copy()
    b.columns = ["Instrument"] + nama[: b.shape[1] - 1]
    b = b.reindex(columns=["Instrument"] + nama)  # blok di tepi sheet bisa lebih sempit
    inst = b["Instrument"].where(b["Instrument"].astype(str).str.strip() != "")
    b["Instrument"] = inst.ffill()  # TR kadang hanya menulis instrumen di baris pertama tiap saham
    b = b[b["Instrument"].astype(str).str.contains(r"[.=]", regex=True, na=False)]
    return b.dropna(subset=nama[:1], how="all")


def baca_sheet_blok(df, lebar, nama):
    potongan = [baca_blok(df, c, nama) for c in range(0, df.shape[1], lebar)]
    potongan = [p for p in potongan if len(p)]
    return pd.concat(potongan, ignore_index=True) if potongan else pd.DataFrame(columns=["Instrument"] + nama)


def deret(df, nama_nilai):
    d = baca_sheet_blok(df, R["lebar_blok"], ["date", nama_nilai])
    d["date"] = olah.ke_tanggal(d["date"])
    d[nama_nilai] = pd.to_numeric(d[nama_nilai], errors="coerce")
    return d.dropna(subset=["date"])


def baca_tumpuk(df, dengan_bobot=False):
    """Sheet snapshot bertumpuk: baris 'snapshot <tgl>' lalu hasil TR (Instrument, RIC[, bobot[, nama]]).

    Untuk indeks MSCI, Refinitiv bisa mengembalikan RIC 'NULL' tetapi tetap memberi bobot dan nama;
    baris seperti itu disimpan dengan ticker kosong dan nama, lalu dicocokkan lewat nama perusahaan.
    """
    baris, snap = [], None
    for row in df.itertuples(index=False):
        a = str(row[0]) if pd.notna(row[0]) else ""
        if a.startswith("snapshot "):
            snap = a.removeprefix("snapshot ").strip()
            continue
        if not snap or not a.startswith("."):
            continue  # baris header / 'Updated at' / kosong
        ric = row[1] if len(row) > 1 else None
        ric = ric if isinstance(ric, str) and "." in ric else None
        nama = row[3] if len(row) > 3 and isinstance(row[3], str) and row[3] != "NULL" else None
        if ric is None and nama is None:
            continue
        bobot = pd.to_numeric(row[2], errors="coerce") if dengan_bobot and len(row) > 2 else None
        baris.append({"snapshot": snap, "ticker": k.kode(ric) if ric else None, "bobot": bobot, "nama": nama})
    kol = ["snapshot", "ticker"] + (["bobot", "nama"] if dengan_bobot else [])
    return pd.DataFrame(baris, columns=["snapshot", "ticker", "bobot", "nama"])[kol].drop_duplicates()


def _norm(nama):
    s = re.sub(r"[^a-z0-9 ]", " ", str(nama).lower())
    s = re.sub(r"\b(pt|tbk|persero|perseroan|terbuka|company|co|ltd)\b", " ", s)
    return " ".join(s.split())


def isi_ticker_dari_nama(hist, static):
    """Isi ticker kosong (RIC 'NULL') dengan mencocokkan nama konstituen ke nama perusahaan di static."""
    if hist.empty or "nama" not in hist or hist["ticker"].notna().all():
        return hist
    peta = {_norm(n): t for t, n in zip(static["ticker"], static["NAME"]) if pd.notna(n)}
    kosong = hist["ticker"].isna()
    hist.loc[kosong, "ticker"] = hist.loc[kosong, "nama"].map(lambda n: peta.get(_norm(n)))
    gagal = hist["ticker"].isna().sum()
    if gagal:
        print(f"  {gagal} baris konstituen tidak cocok namanya; cek manual: "
              + ", ".join(hist.loc[hist['ticker'].isna(), 'nama'].dropna().unique()[:8]))
    return hist


def baca_pasar(sh, out):
    bench = None
    for b, (kolom, ric, field, _) in enumerate(R["bench"]):
        d = baca_blok(sh["bench"], b * R["lebar_blok"], ["date", kolom])
        d["date"] = olah.ke_tanggal(d["date"])
        d[kolom] = pd.to_numeric(d[kolom], errors="coerce")
        d = d.dropna(subset=["date"]).drop(columns="Instrument").drop_duplicates("date")
        if len(d) < 100:
            print(f"  PERINGATAN: {kolom} ({ric or 'RIC kosong'}, {field}) kosong atau pendek ({len(d)} hari).")
        bench = d if bench is None else bench.merge(d, on="date", how="outer")
    if bench["JCI"].notna().sum() < 100:
        raise SystemExit("Sheet bench: IHSG kosong atau terlalu pendek. Cek RIC IHSG di sheet config.")
    out["bench"] = bench.dropna(subset=["JCI"])

    nama_st = list(R["field_statis"].values())
    st = baca_sheet_blok(sh["static"], len(nama_st) + 2, nama_st)
    st.insert(0, "ticker", st.pop("Instrument").map(k.kode))
    st["EQY_FREE_FLOAT_PCT"] = pd.to_numeric(st["EQY_FREE_FLOAT_PCT"], errors="coerce")
    st["EQY_SH_OUT"] = pd.to_numeric(st["EQY_SH_OUT"], errors="coerce") / 1e6  # -> juta lembar
    out["static"] = st

    ff, so = deret(sh["ff_hist"], "free_float"), deret(sh["sh_hist"], "sh_out_juta")
    so["sh_out_juta"] /= 1e6
    hist = ff.merge(so, on=["Instrument", "date"], how="outer")
    hist.insert(0, "ticker", hist.pop("Instrument").map(k.kode))
    out["static_hist"] = hist

    out["konstituen_ihsg"] = baca_tumpuk(sh["universe"])
    out["msci_hist"] = isi_ticker_dari_nama(baca_tumpuk(sh["msci"], dengan_bobot=True), st)
    out["ftse_hist"] = isi_ticker_dari_nama(baca_tumpuk(sh["ftse"], dengan_bobot=True), st)
    for nama, _, _ in R["tambahan"]:
        if nama in sh:
            t = deret(sh[nama], "nilai")
            t.insert(0, "ticker", t.pop("Instrument").map(k.kode))
            out[f"tambahan_{nama}"] = t


def selaraskan_tr(g: pd.DataFrame) -> pd.DataFrame:
    """Cek apakah tanggal TR.TotalReturn sejajar dengan perubahan harga penutupan.

    Forum LSEG menyebut TR.TotalReturn bisa melaporkan return hari bursa sebelumnya. Salah geser satu
    hari akan merusak event study, jadi korelasi dengan perubahan harga dicek di geser -1, 0, +1 dan
    tr_pct digeser ke posisi dengan korelasi tertinggi.
    """
    g = g.sort_values(["ticker", "date"]).copy()
    dp = g.groupby("ticker")["px_last"].transform(lambda s: s.ffill().pct_change(fill_method=None)) * 100
    tr = pd.to_numeric(g["tr_pct"], errors="coerce")
    kor = {lag: dp.corr(g.assign(t=tr).groupby("ticker")["t"].shift(lag)) for lag in (-1, 0, 1)}
    terbaik = max(kor, key=lambda x: (kor[x] if pd.notna(kor[x]) else -9))
    print("  cek tanggal TR.TotalReturn: korelasi dengan perubahan harga " +
          ", ".join(f"geser {lag:+d} = {v:.3f}" for lag, v in kor.items()))
    if terbaik != 0 and kor[terbaik] > (kor[0] if pd.notna(kor[0]) else -9) + 0.05:
        print(f"  PERINGATAN: TR.TotalReturn tergeser; digeser {terbaik:+d} hari agar sejajar dengan harga.")
        g["tr_pct"] = g.assign(t=tr).groupby("ticker")["t"].shift(terbaik)
    return g


def msci_event(msci_hist):
    """Keanggotaan MSCI untuk event regresi (02): dari msci_manual.csv atau snapshot di msci_hist."""
    manual = k.DATA_MENTAH / "msci_manual.csv"
    if manual.exists():
        m = pd.read_csv(manual)[["ticker", "bobot", "event"]]
        m["ticker"] = m["ticker"].map(k.kode)
        return m, "msci_manual.csv"
    blok = []
    for ev, c in k.EVENTS_MSCI.items():
        t = f"{c['snapshot_msci'][:4]}-{c['snapshot_msci'][4:6]}-{c['snapshot_msci'][6:]}"
        b = msci_hist[(msci_hist["snapshot"] == t) & msci_hist["ticker"].notna()][["ticker", "bobot"]].copy()
        b["event"] = ev
        blok.append(b)
    return pd.concat(blok, ignore_index=True), "sheet msci"


def main(paths):
    """Membaca satu file (data-refinitiv.xlsx) atau beberapa file; sheet saham bernama <field> atau <field>_<tahun>."""
    out, harga = {}, []
    pola = re.compile(r"^(tr_pct|px_last|px_volume)(?:_(\d{4}))?$")
    for p in paths:
        sh = pd.read_excel(p, sheet_name=None, header=None)
        print(f"{p.name}: {len(sh)} sheet")
        if "bench" in sh:
            baca_pasar(sh, out)
        periode = {}
        for nama in sh:
            m = pola.match(nama)
            if m:
                periode.setdefault(m.group(2) or p.stem, []).append((m.group(1), nama))
        for suf, daftar in sorted(periode.items()):
            gabung = None
            for field, nama in daftar:
                d = deret(sh[nama], field)
                d["ticker"] = d.pop("Instrument").map(k.kode)
                d = d.drop_duplicates(["ticker", "date"])
                print(f"  {nama:16s}: {d['ticker'].nunique()} saham, {len(d):,} baris")
                if len(d):
                    gabung = d if gabung is None else gabung.merge(d, on=["ticker", "date"], how="outer")
            if gabung is None:
                print(f"  periode {suf}: kosong, dilewati")
                continue
            if {"tr_pct", "px_last"} <= set(gabung.columns):
                gabung = selaraskan_tr(gabung)
            harga.append(gabung)
    if "bench" not in out or not harga:
        raise SystemExit("Butuh sheet bench (pasar) dan minimal satu periode sheet saham yang terisi.")

    harga = pd.concat(harga, ignore_index=True).drop_duplicates(["ticker", "date"], keep="first")
    for c in R["sheet_harga"]:
        if c not in harga:
            harga[c] = pd.NA
    msci, sumber = msci_event(out["msci_hist"])

    print()
    olah.tulis(harga, out["bench"], out["static"], msci, sumber)
    for nama in ["konstituen_ihsg", "msci_hist", "ftse_hist", "static_hist"] + [f"tambahan_{n}" for n, _, _ in R["tambahan"]]:
        if nama in out:
            out[nama].to_csv(k.DATA_OLAH / f"{nama}.csv", index=False)
            print(f"{nama}: {len(out[nama]):,} baris")
    if (k.DATA_MENTAH / "idx" / "ringkasan_saham.csv").exists():
        import importlib.util as iu
        sp = iu.spec_from_file_location("tambah_idx", k.ROOT / "analisis" / "01c_tambah_idx.py")
        md = iu.module_from_spec(sp)
        sp.loader.exec_module(md)
        md.main()
    if msci.empty:
        print("\nKeanggotaan MSCI tidak tersedia dari kode/nama; memakai PROKSI kapitalisasi free float (sementara).")
        import importlib.util
        spec = importlib.util.spec_from_file_location("msci_proksi", k.ROOT / "analisis" / "01b_msci_proksi.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.main()


if __name__ == "__main__":
    utama = k.DATA_MENTAH / f"{R['nama_file']}.xlsx"
    paths = [k.Path(a) for a in sys.argv[1:]] or ([utama] if utama.exists() else sorted(k.DATA_MENTAH.glob("[1-4]-*.xlsx")))
    main(paths)
