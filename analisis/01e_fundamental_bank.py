"""Mengolah laporan keuangan XBRL bank (instance.zip dari idx.co.id) menjadi variabel fundamental per bank.

Input : data/mentah/idx/laporan_keuangan/<KODE>_<tahun>_<periode>.zip  (audit = Des 2025, tw2 = Jun 2026)
Output: data/olah/fundamental_bank.csv  (satu baris per bank per periode)

Variabel (rasio dalam %):
  aset_rp, ekuitas_rp, modal_aset   = ekuitas / aset
  dpk_rp                            = giro + tabungan + deposito (pihak ketiga + berelasi; syariah: + dana syirkah temporer)
  ldr                               = kredit (atau pembiayaan) / DPK
  surat_berharga_aset               = surat berharga (+ obligasi pemerintah bila dilaporkan terpisah) / aset
                                      -> proksi eksposur SBN (mayoritas surat berharga bank Indonesia adalah SBN)
  pendanaan_wholesale               = (pinjaman + obligasi/sukuk diterbitkan + pinjaman subordinasi) / (aset - ekuitas)
  repo_aset                         = surat berharga dijual dengan janji dibeli kembali / aset (melonjak di H1 2026)
  casa                              = (giro + tabungan) / DPK
"""
import re
import zipfile
import xml.etree.ElementTree as ET

import pandas as pd

import konfigurasi as k

DIR = k.DATA_MENTAH / "idx" / "laporan_keuangan"
TANGGAL = {"audit": "2025-12-31", "tw2": "2026-06-30"}


def baca_xbrl(path, tanggal):
    root = ET.fromstring(zipfile.ZipFile(path).read("instance.xbrl"))
    ctx = {}
    for c in root.iter():
        if c.tag.endswith("}context"):
            inst = [e.text for e in c.iter() if e.tag.endswith("instant")]
            dims = [e for e in c.iter() if e.tag.endswith("explicitMember")]
            ctx[c.get("id")] = (inst[0] if inst else None, len(dims))
    nilai = {}
    for e in root:
        t = (e.text or "").strip()
        if e.get("contextRef") and re.fullmatch(r"-?\d+(\.\d+)?", t):
            c = ctx.get(e.get("contextRef"))
            if c and c[0] == tanggal and c[1] == 0:
                nilai[e.tag.split("}")[1]] = float(t)
    return nilai


def jumlah(v, pola):
    return sum(x for n, x in v.items() if re.search(pola, n) and not n.startswith("Allowance"))


def keluarga(v, total, *komponen):
    """Pakai pos total bila ada; kalau tidak, jumlahkan komponennya (hindari hitung ganda)."""
    return v[total] if total in v else sum(v.get(c, 0) for c in komponen)


def variabel(v):
    aset = v.get("Assets", float("nan"))
    ekuitas = v.get("Equity", float("nan"))
    liab = aset - ekuitas  # bank syariah mencatat dana syirkah temporer di luar 'Liabilities'

    giro = jumlah(v, r"^CurrentAccounts(ThirdParties|RelatedParties)$|^WadiahDemandDeposits|^DemandDepositsWadiah")
    tabungan = jumlah(v, r"^Savings(ThirdParties|RelatedParties)$|^WadiahSavings|^SavingsWadiah")
    deposito = jumlah(v, r"^TimeDeposits(ThirdParties|RelatedParties)$")
    syirkah = jumlah(v, r"^TemporarySyirkahFunds|^TemporarySyirkah.*(Savings|Deposits)")
    dpk = giro + tabungan + deposito + syirkah
    kredit = jumlah(v, r"^Loans(ThirdParties|RelatedParties)$|^(Murabahah|Mudharabah|Musyarakah|Ijarah|Istishna|Qardh).*(ThirdParties|RelatedParties|Receivables|Financing)$|^Financing")
    obligasi_pem = v.get("GovernmentBonds", 0)
    sb = keluarga(v, "MarketableSecurities", "MarketableSecuritiesThirdParties", "MarketableSecuritiesRelatedParties") + obligasi_pem
    wholesale = (keluarga(v, "Borrowings", "BorrowingsThirdParties", "BorrowingsRelatedParties")
                 + keluarga(v, "BondsPayable", "LongTermBondsPayable", "CurrentMaturitiesOfBondsPayable")
                 + keluarga(v, "SubordinatedLoans", "SubordinatedLoansThirdParties", "SubordinatedLoansRelatedParties")
                 + v.get("SubordinatedBonds", 0) + v.get("OthersSecuritiesIssued", 0)
                 + keluarga(v, "Sukuk", "MudharabahSukuk", "SubordinatedMudharabahSukuk"))
    repo = v.get("SecuritiesSoldWithRepurchaseAgreement", 0)
    return {"aset_rp": aset, "ekuitas_rp": ekuitas, "dpk_rp": dpk, "kredit_rp": kredit, "surat_berharga_rp": sb,
            "modal_aset": ekuitas / aset * 100 if aset else None,
            "ldr": kredit / dpk * 100 if dpk else None,
            "surat_berharga_aset": sb / aset * 100 if aset else None,
            "obligasi_pemerintah_aset": obligasi_pem / aset * 100 if "GovernmentBonds" in v else None,
            "pendanaan_wholesale": wholesale / liab * 100 if liab else None,
            "repo_aset": repo / aset * 100 if aset else None,
            "casa": (giro + tabungan) / dpk * 100 if dpk else None,
            "n_pos": len(v)}


def main():
    baris = []
    for f in sorted(DIR.glob("*.zip")):
        kode, tahun, periode = f.stem.split("_")
        try:
            v = baca_xbrl(f, TANGGAL[periode])
        except Exception as e:  # noqa: BLE001
            print(f"  gagal {f.name}: {e}")
            continue
        if not v:
            print(f"  {f.name}: tidak ada pos pada {TANGGAL[periode]}")
            continue
        baris.append({"ticker": kode, "periode": TANGGAL[periode], **variabel(v)})
    df = pd.DataFrame(baris)
    df.to_csv(k.DATA_OLAH / "fundamental_bank.csv", index=False)
    print(f"Fundamental bank: {df['ticker'].nunique()} bank, {len(df)} baris")
    print(df.groupby("periode")[["modal_aset", "ldr", "surat_berharga_aset", "pendanaan_wholesale", "repo_aset", "casa"]].median().round(1).to_string())
    return df


if __name__ == "__main__":
    main()
