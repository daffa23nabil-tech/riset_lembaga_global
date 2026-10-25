# Panduan Tarik Data Refinitiv di Kampus (satu file)

File: `data-refinitiv.xlsx`. Semua data ada di satu file, dan langkah ringkasnya ada di sheet **MULAI** paling depan. Perkiraan waktu 5–7 jam. Kalau waktu terbatas, cukup selesaikan 7 sheet bertanda **P1**, karena itu sudah cukup untuk brief Oktober.

## Langkah singkat
1. **Tes add-in.** Di sel kosong ketik `=TR(".JKSE","TR.PriceClose")`, lalu Enter. Harus keluar angka.
   - Kalau `#NAME?`, coba `=RDP.Data(".JKSE","TR.PriceClose")`. Kalau itu yang jalan: Ctrl+H → Find `=TR(` → Replace `=RDP.Data(` → Within: Workbook → Replace All.
2. **Cara refresh satu sheet:** klik tab sheet → menu **Formulas → Calculate Sheet** (atau Fn+Shift+F9). **Jangan** klik Calculate Now. Tunggu sampai sel berhenti loading, lalu **Ctrl+S**.
3. **Refresh sesuai urutan tab** (urutan tab sudah sama dengan urutan kerja):

| Urutan | Sheet | Prioritas | Cek setelah refresh |
|---|---|---|---|
| 1 | `tickers` | P1 | Kolom B berisi ±900+ kode `XXXX.JK`. Kalau kosong, tempel daftar kode di B2 ke bawah |
| 2 | `bench` | P1 | Tanggal dan angka sejak 2010; beberapa blok boleh kosong |
| 3–5 | `tr_pct_2025`, `px_last_2025`, `px_volume_2025` | P1 | Tiap blok berisi tanggal dan angka per saham |
| 6 | `static` | P1 | Nama, sektor, free float |
| 7 | `msci` | P1 | Daftar anggota per tanggal; bobot boleh kosong |
| 8–18 | `ftse`, `universe`, `ff_hist`, `sh_hist`, `kepemilikan_asing`, `rating_bank`, `total_aset`, `total_deposito`, `total_ekuitas` | P2 | Yang field-nya kosong di config akan error; biarkan saja |
| 19–24 | `tr_pct_2020` … `px_volume_2015` | P2 | Paling berat; boleh dilanjutkan di kunjungan lain |

## (Opsional) Melengkapi kode di sheet `config`
- **Baris 20 ke bawah (deret pasar):** isi RIC yang kosong (CDS, komoditas, BANK_*, ETF, GBI-EM) dari kotak pencarian Workspace. Kalau sebuah deret gagal, coba isian kolom **"Alternatif jika kosong"**.
- **B4:** RIC FTSE Indonesia.
- **Tabel data tambahan (di bawah tabel deret pasar):** field kepemilikan asing dan rating penerbit di kolom C.
- **Cara cepat mengecek satu kode:** `=TR("ID10YT=RR","TR.BidYield")` di sel kosong. Kalau keluar angka, kodenya benar.
- Tidak ketemu? Biarkan kosong, nanti dilewati.

## Kalau ada masalah
| Gejala | Solusi |
|---|---|
| Hasil TR hanya satu sel | Klik sel rumus → F2 → Enter |
| Bobot MSCI/FTSE kosong atau error 415 | Kampus mungkin tidak berlangganan bobot; daftar anggota tetap terpakai. Cadangan: `msci_manual.csv` dari situs MSCI/ETF EIDO |
| Excel lambat atau macet | Save, tutup, buka lagi, lanjutkan dari sheet berikutnya |
| Batas tarikan harian tercapai | Hentikan; lanjutkan besok, data yang sudah masuk tetap tersimpan |

## Sebelum pulang
- **Save.** File bisa berukuran ratusan MB, jadi bawa pulang lewat **flashdisk / Google Drive**, bukan email.
- Taruh di `10-riset-msci\data\mentah\data-refinitiv.xlsx`.
- Ekspor Scopus Q8–Q11 (query di `kajian-literatur-model.md`) ke `08-riset-literatur\scopus\`.

## Setelah pulang
```bash
cd "10-riset-msci/analisis"
python 01_baca_refinitiv.py
python 02_event_study.py
python 03_perbandingan_event.py
```
Pembaca otomatis menggabungkan ketiga periode saham, melewati sheet yang kosong, dan mengecek apakah tanggal `TR.TotalReturn` bergeser satu hari (kalau ya, dikoreksi dan dicetak PERINGATAN).
