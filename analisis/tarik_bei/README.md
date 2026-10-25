# Penarik data publik BEI

Skrip JavaScript untuk konsol browser. API publik idx.co.id hanya menjawab permintaan dari halaman idx.co.id sendiri,
jadi skrip ini dijalankan di tab browser biasa yang membuka idx.co.id (bukan dari Python/curl). Tidak ada login dan
tidak ada pengelakan CAPTCHA; bila situs menampilkan tantangan keamanan, selesaikan sendiri lalu ulangi.

Urutan: buka halaman idx.co.id → DevTools (F12) → Console → tempel `_unduh.js` → tempel skrip yang diinginkan.

| Skrip | Keluaran | Lalu |
|---|---|---|
| `ringkasan_saham.js` | dump teks per hari bursa | `python analisis/00_urai_dump_idx.py --periode 2020\|2023\|2025 <dump>` |
| `ihsg.js` | `ihsg.csv` | simpan ke `data/mentah/idx/` |
| `uma_suspensi.js` | `uma.csv`, `suspensi.csv` | simpan ke `data/mentah/idx/` |
| `xbrl_bank.js` | 96 berkas `<KODE>_<tahun>_<periode>.zip` | simpan ke `data/mentah/idx/laporan_keuangan/` |

Pakai jeda antarpermintaan (sudah ada di skrip) supaya tidak membebani server BEI.
