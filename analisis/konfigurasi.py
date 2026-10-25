"""Konfigurasi bersama: path, tanggal event, dan tata letak workbook Refinitiv."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_MENTAH = ROOT / "data" / "mentah"
DATA_OLAH = ROOT / "data" / "olah"
HASIL = ROOT / "hasil"

# Keputusan lembaga global soal Indonesia (dicek ke berita/rilis 18 Okt 2026; lihat docs/desain-lembaga-global.md).
# hari0 = hari bursa BEI pertama yang bisa bereaksi. snapshot_msci hanya untuk event MSCI
# (event dengan regresi lintas saham di 02_event_study.py). plasebo = keputusan tanpa perubahan.
EVENTS = {
    "E1": {"hari0": "2026-01-28", "snapshot_msci": "20260127", "lembaga": "MSCI", "jenis": "Indeks saham",
           "label": "Free float + pembekuan rebalancing (27 Jan 2026)"},
    "MDY": {"hari0": "2026-02-06", "lembaga": "Moody's", "jenis": "Rating",
            "label": "Baa2, outlook stabil -> negatif (5 Feb 2026)"},
    "FTSE1": {"hari0": "2026-02-10", "lembaga": "FTSE Russell", "jenis": "Indeks saham",
              "label": "Tunda review Maret (notice 9 Feb 2026)",
              "catatan": "Satu sumber menyebut penundaan pertama 29 Jan (hari +1 E1). Reaksi kecil, sudah diantisipasi."},
    "FCH": {"hari0": "2026-03-04", "lembaga": "Fitch", "jenis": "Rating",
            "label": "BBB, outlook stabil -> negatif (rilis 3 Mar 2026)",
            "catatan": "Hari yang sama dengan eskalasi konflik Timur Tengah."},
    "JPM": {"hari0": "2026-04-23", "lembaga": "J.P. Morgan", "jenis": "Indeks obligasi",
            "label": "GBI-EM: batas bobot 10% -> 9% + anggota baru (22 Apr 2026)",
            "catatan": "Batas 9% sudah bocor Sep 2025; tanggal pengumuman formal belum dicek ke rilis JPM."},
    "SP": {"hari0": "2026-07-13", "lembaga": "S&P", "jenis": "Rating", "plasebo": True,
           "label": "Afirmasi BBB stabil (13 Jul 2026)",
           "catatan": "Jam rilis belum pasti; jendela [0,+1] menangkap kedua kemungkinan."},
    "FTSE2": {"hari0": "2026-10-07", "lembaga": "FTSE Russell", "jenis": "Indeks saham", "plasebo": True,
              "label": "Tetap Secondary Emerging, tidak masuk Watch List (6 Okt 2026, setelah tutup AS)"},
    "E2": {"hari0": "2026-10-16", "snapshot_msci": "20261015", "lembaga": "MSCI", "jenis": "Indeks saham",
           "label": "Konsultasi reklasifikasi ke Standalone (15 Okt 2026)"},
}
EVENTS_MSCI = {e: c for e, c in EVENTS.items() if "snapshot_msci" in c}

# Jendela relatif terhadap hari-0, dalam hari bursa IHSG.
JENDELA_ESTIMASI = (-250, -30)
JENDELA_PRA = (-60, -2)  # momentum dan likuiditas sebelum event
JENDELA_CAR = {
    "car_0": (0, 0),
    "car_0_1": (0, 1),
    "car_m1_1": (-1, 1),
    "car_0_5": (0, 5),
    "car_2_20": (2, 20),   # pembalikan jangka pendek
    "car_2_60": (2, 60),   # pembalikan jangka menengah
}

# Tata letak workbook (dipakai bersama oleh template, data dummy, dan parser).
START_DATE = "20250101"
N_SLOT = 1000  # slot saham per sheet harga; JCI berisi ±950 saham
SHEET_HARGA = {"px_last": "PX_LAST", "px_volume": "PX_VOLUME", "tri": "TOT_RETURN_INDEX_GROSS_DVDS"}
BENCHMARK = ["JCI Index", "MXEF Index", "JAKFIN Index", "USDIDR Curncy", "GTIDR10Y Govt"]
# Nama kolom standar di data/olah/bench.csv (dari kode Bloomberg).
NAMA_BENCH = {"GTIDR10Y": "SBN10Y"}
FIELD_STATIS = ["NAME", "GICS_SECTOR_NAME", "GICS_INDUSTRY_NAME", "EQY_FREE_FLOAT_PCT", "EQY_SH_OUT"]
MSCI_INDEKS = "MXID Index"
# Kolom awal blok BDS keanggotaan MSCI per event di sheet "msci" (1-based): E1 di A:B, E2 di D:E.
MSCI_KOLOM = {"E1": 1, "E2": 4}


# Tata letak workbook Refinitiv (template TR() + pembacanya). Data dipecah 4 workbook supaya Excel
# tidak macet: 1 pasar + konstituen + statis + tambahan, lalu 3 workbook saham per periode.
# Blok TR() deret waktu diletakkan berdampingan; kolom pertama blok selalu Instrument (RH=IN).
# Blok snapshot (konstituen) ditumpuk ke bawah dengan baris label "snapshot YYYY-MM-DD".
_EM = [("TH", ".SETI", "TH10YT=RR", "THB="), ("MY", ".KLSE", "MY10YT=RR", "MYR="),
       ("PH", ".PSI", "PH10YT=RR", "PHP="), ("IN", ".NSEI", "IN10YT=RR", "INR="),
       ("BR", ".BVSP", "BR10YT=RR", "BRL="), ("MX", ".MXX", "MX10YT=RR", "MXN="),
       ("TR", ".XU100", "TR10YT=RR", "TRY="), ("ZA", ".JTOPI", "ZA10YT=RR", "ZAR="),
       ("KR", ".KS11", "KR10YT=RR", "KRW="), ("TW", ".TWII", "TW10YT=RR", "TWD="),
       ("VN", ".VNI", "VN10YT=RR", "VND="), ("PL", ".WIG20", "PL10YT=RR", "PLN="),
       ("CL", ".SPIPSA", "CL10YT=RR", "CLP=")]
REF = {
    "akhir": "2026-12-31",  # tanggal di masa depan aman: TR mengembalikan data sampai hari terakhir
    "pasar_mulai": "2010-01-01",
    # Pola RIC MSCI: .dMI<negara>00000<P=harga|N=net return><mata uang>. ".dMIEF00000NUS" (MSCI EM net USD)
    # tercantum di halaman benchmark ETF; varian Indonesia belum terverifikasi.
    "ric_msci_id": ".dMIID00000NUS",
    "ric_ftse_id": "",  # RIC indeks FTSE Indonesia dicari dulu di Workspace, lalu isi di sheet config
    # Deret pasar: (nama kolom standar, RIC, field, alternatif jika kosong). Bisa diganti di sheet config.
    # Yield memakai TR.BidYield (contoh resmi forum LSEG untuk RIC =RR); TR.MidYield sering kosong.
    "bench": [("JCI", ".JKSE", "TR.PriceClose", ""),
              ("MXEF", ".dMIEF00000NUS", "TR.PriceClose", "RIC .dMIEF00000PUS"),
              ("SBN10Y", "ID10YT=RR", "TR.BidYield", "field TR.MidYield"),
              ("USDIDR", "IDR=", "TR.MidPrice", "field TR.BidPrice"),
              ("MXID", ".dMIID00000NUS", "TR.PriceClose", "RIC .dMIID00000PUS / .dMIID00000PID"),
              ("CDS5Y", "", "TR.MidSpread", "cari 'Indonesia CDS 5Y'; field TR.BidSpread / TR.PriceClose"),
              ("VIX", ".VIX", "TR.PriceClose", ""),
              ("COAL", "", "TR.PriceClose", "cari 'Newcastle coal futures'"),
              ("CPO", "", "TR.PriceClose", "cari 'Crude palm oil futures Bursa Malaysia'"),
              ("NICKEL", "", "TR.PriceClose", "cari 'LME nickel 3 month'")]
             + [(f"EQ_{c}", eq, "TR.PriceClose", "") for c, eq, _, _ in _EM]
             + [(f"Y10_{c}", y, "TR.BidYield", "field TR.MidYield") for c, _, y, _ in _EM]
             + [(f"FX_{c}", fx, "TR.MidPrice", "field TR.BidPrice") for c, _, _, fx in _EM]
             # Indeks sektor keuangan/bank: donor synthetic control versi saham bank. RIC berisi dugaan
             # yang umum dipakai; yang kosong dicari di Workspace (misalnya "MSCI Thailand Financials").
             + [("BANK_ID", "", "TR.PriceClose", "cari 'IDX Sector Financials' atau 'MSCI Indonesia Financials'"),
                ("BANK_EM", "", "TR.PriceClose", "cari 'MSCI Emerging Markets Financials'")]
             + [(f"BANK_{c}", ric, "TR.PriceClose", f"cari 'MSCI {nama} Financials' atau indeks bank lokal")
                for c, nama, ric in [("TH", "Thailand", ".SETBANK"), ("MY", "Malaysia", ""), ("PH", "Philippines", ""),
                                     ("IN", "India", ".NSEBANK"), ("BR", "Brazil", ".IFNC"), ("MX", "Mexico", ""),
                                     ("TR", "Turkey", ".XBANK"), ("ZA", "South Africa", ""), ("KR", "Korea", ""),
                                     ("TW", "Taiwan", ""), ("VN", "Vietnam", ""), ("PL", "Poland", ""), ("CL", "Chile", "")]]
             # Dana pasif pengikut indeks dan bobot Indonesia di indeks obligasi (RIC/field dicari dulu).
             + [("ETF_EIDO_AUM", "", "", "cari ETF iShares MSCI Indonesia (EIDO); field total net assets"),
                ("ETF_EEM_AUM", "", "", "cari ETF iShares MSCI Emerging Markets (EEM); field total net assets"),
                ("ETF_VWO_AUM", "", "", "cari ETF Vanguard FTSE Emerging Markets (VWO); field total net assets"),
                ("ETF_EMLC_AUM", "", "", "cari ETF VanEck J.P. Morgan EM Local Currency Bond (EMLC); total net assets"),
                ("GBIEM_ID_BOBOT", "", "", "cari indeks J.P. Morgan GBI-EM Global Diversified; bobot Indonesia (sering berlisensi)")],
    # Satu file Excel: data/mentah/data-refinitiv.xlsx. Data saham dipecah per periode menjadi sheet
    # <field>_<tahun mulai>. Total return ditarik di SEMUA periode supaya stock split dan dividen tidak
    # terbaca sebagai lonjakan return palsu.
    "nama_file": "data-refinitiv",
    "periode_saham": [("2025", "2025-01-01", "2026-12-31"), ("2020", "2020-01-01", "2024-12-31"),
                      ("2015", "2015-01-01", "2019-12-31")],
    "statis_mulai": "2015-01-01",
    # Data tambahan per saham (kuartalan): field dicek/diisi di sheet config sebelum refresh.
    # Field fundamental bank adalah dugaan awal; cek di Data Item Browser.
    "tambahan": [("kepemilikan_asing", "", "SDate=2015-01-01 EDate=2026-12-31 Frq=CQ CH=Fd RH=IN"),
                 ("rating_bank", "", "SDate=2015-01-01 EDate=2026-12-31 CH=Fd RH=IN"),
                 ("total_aset", "TR.TotalAssetsReported", "SDate=2015-01-01 EDate=2026-12-31 Frq=CQ CH=Fd RH=IN"),
                 ("total_deposito", "TR.TotalDeposits", "SDate=2015-01-01 EDate=2026-12-31 Frq=CQ CH=Fd RH=IN"),
                 ("total_ekuitas", "TR.TotalEquity", "SDate=2015-01-01 EDate=2026-12-31 Frq=CQ CH=Fd RH=IN")],
    "n_universe": 1500,
    "batch": 25,
    "lebar_blok": 4,  # Instrument, Date, nilai, kolom kosong
    "jarak_snapshot_ihsg": 1100,  # baris per blok snapshot konstituen IHSG
    "jarak_snapshot_indeks": 80,  # baris per blok snapshot MSCI/FTSE Indonesia
    "sheet_harga": {"px_last": "TR.PriceClose", "px_volume": "TR.Volume", "tr_pct": "TR.TotalReturn"},
    "field_statis": {"TR.CommonName": "NAME", "TR.GICSSector": "GICS_SECTOR_NAME",
                     "TR.GICSIndustry": "GICS_INDUSTRY_NAME", "TR.FreeFloatPct": "EQY_FREE_FLOAT_PCT",
                     "TR.SharesOutstanding": "EQY_SH_OUT"},
    "batch_statis": 200,
    "batch_statis_hist": 50,
}


def tanggal_snapshot(sampai="2026-10-19"):
    """Hari kerja terakhir Feb/Mei/Agu/Nov 2015 s.d. `sampai` (bulan review indeks) + snapshot event."""
    import pandas as pd
    ujung = pd.date_range("2015-01-01", sampai, freq="BME")
    review = [d for d in ujung if d.month in (2, 5, 8, 11)]
    event = [pd.Timestamp(f"{c['snapshot_msci'][:4]}-{c['snapshot_msci'][4:6]}-{c['snapshot_msci'][6:]}")
             for c in EVENTS_MSCI.values()]
    event += [pd.Timestamp("2026-02-06"), pd.Timestamp("2026-10-06")]  # sebelum event FTSE
    return sorted({d.strftime("%Y-%m-%d") for d in review + event})


def kode(ticker) -> str:
    """'BBCA IJ Equity' / 'BBCA IJ' / 'BBCA.JK' / 'bbca' -> 'BBCA'."""
    return str(ticker).strip().split()[0].split(".")[0].upper()
