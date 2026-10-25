"""Proksi keanggotaan MSCI Indonesia saat Refinitiv mengembalikan 'NULL' untuk kode konstituen.

Refinitiv memberi bobot konstituen MSCI tetapi tidak kodenya. MSCI memilih anggota menurut kapitalisasi
free float, dan bobot sebanding dengan kapitalisasi itu. Jadi untuk tiap snapshot event:
  N  = jumlah baris bobot di sheet msci;
  proksi anggota = N saham dengan kapitalisasi free float terbesar sehari sebelum event;
  validasi = korelasi bobot asli (diurutkan) dengan porsi kapitalisasi proksi (diurutkan).
Hasil ditulis ke data/olah/msci.csv (dipakai 02_event_study.py) dan dilaporkan validasinya.
SEMENTARA: ganti dengan data nama konstituen (TR.IndexConstituentName) setelah tarikan berikutnya.
"""
import numpy as np
import pandas as pd

import konfigurasi as k

FILE = k.DATA_MENTAH / f"{k.REF['nama_file']}.xlsx"


def bobot_per_snapshot():
    m = pd.read_excel(FILE, sheet_name="msci", header=None)
    out, snap = {}, None
    for row in m.itertuples(index=False):
        a = str(row[0]) if pd.notna(row[0]) else ""
        if a.startswith("snapshot "):
            snap = a.removeprefix("snapshot ").strip()
            out[snap] = []
        elif snap and pd.notna(row[2]):
            w = pd.to_numeric(row[2], errors="coerce")
            if pd.notna(w):
                out[snap].append(float(w))
    return out


def main():
    bobot = bobot_per_snapshot()
    harga = pd.read_csv(k.DATA_OLAH / "harga.csv.gz", parse_dates=["date"])
    static = pd.read_csv(k.DATA_OLAH / "static.csv").set_index("ticker")
    px = harga.pivot_table(index="date", columns="ticker", values="px_last").sort_index().ffill()

    eido_path = k.DATA_MENTAH / "eido_holdings_20261021.csv"
    eido = pd.read_csv(eido_path, comment="#")["ticker"] if eido_path.exists() else None
    n_terkini = len(bobot.get(max(bobot), [])) if bobot else 0  # jumlah anggota snapshot terakhir

    baris, laporan = [], []
    for ev, c in k.EVENTS_MSCI.items():
        t = f"{c['snapshot_msci'][:4]}-{c['snapshot_msci'][4:6]}-{c['snapshot_msci'][6:]}"
        w = sorted(bobot.get(t, []), reverse=True)
        if not w:
            laporan.append(f"- {ev}: tidak ada bobot untuk snapshot {t}")
            continue
        p = px.loc[:pd.Timestamp(t)].iloc[-1]
        ff = static["EQY_FREE_FLOAT_PCT"].reindex(p.index)
        ff_path = k.DATA_OLAH / "ff_event.csv"  # free float BEI per tanggal, lebih tepat dari angka terkini
        if ff_path.exists():
            ffe = pd.read_csv(ff_path)
            ff = ffe[ffe["event"] == ev].set_index("ticker")["free_float"].reindex(p.index).fillna(ff)
        ffcap = (p * static["EQY_SH_OUT"].reindex(p.index) * ff / 100).dropna()
        if eido is not None:
            # Anggota terkini = n teratas holding EIDO (indeks dibekukan sejak Jan 2026, jadi tidak ada penambahan).
            # Snapshot lebih awal = anggota terkini + saham terbesar yang kini TIDAK ada di EIDO (sudah dikeluarkan MSCI).
            inti = [t for t in eido.head(n_terkini) if t in ffcap.index]
            sisa = ffcap.drop(index=[t for t in ffcap.index if t in set(eido) ], errors="ignore").sort_values(ascending=False)
            pilih = inti + list(sisa.index[: max(len(w) - len(inti), 0)])
            top = ffcap.reindex(pilih).sort_values(ascending=False)
        else:
            top = ffcap.sort_values(ascending=False).head(len(w))
        porsi = (top / top.sum() * 100).to_numpy()
        kor = np.corrcoef(np.array(w), porsi)[0, 1]
        mae = np.mean(np.abs(np.array(w) - porsi))
        laporan.append(f"- {ev} (snapshot {t}): {len(w)} anggota; korelasi bobot asli vs proksi (urut) = {kor:.3f}; "
                       f"selisih rata-rata {mae:.2f} poin persen; bobot terbesar asli {w[0]:.1f}% vs proksi {porsi[0]:.1f}% ({top.index[0]})")
        for tk, wp in zip(top.index, porsi):
            baris.append({"ticker": tk, "bobot": wp, "event": ev})
    msci = pd.DataFrame(baris)
    msci.to_csv(k.DATA_OLAH / "msci.csv", index=False)
    msci.to_csv(k.DATA_OLAH / "msci_proksi.csv", index=False)
    print("Proksi keanggotaan MSCI (SEMENTARA):")
    print("\n".join(laporan))
    for ev in msci["event"].unique():
        print(f"  {ev}: " + ", ".join(msci.loc[msci["event"] == ev, "ticker"]))


if __name__ == "__main__":
    main()
