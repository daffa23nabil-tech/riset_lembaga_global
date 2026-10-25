// Pengumuman UMA dan suspensi BEI (Okt 2023-sekarang) -> data/mentah/idx/uma.csv dan suspensi.csv.
// Jalankan di konsol browser pada halaman idx.co.id. Tempel _unduh.js dulu.
const q = (v) => '"' + String(v ?? '').replace(/"/g, '""') + '"';
(async () => {
  const uma = (await (await fetch('/primary/NewsAnnouncement/GetUma?indexFrom=1&dateFrom=&dateTo=&lang=id&pageSize=9999', { headers: { Accept: 'application/json' } })).json()).Results || [];
  unduh('uma.csv', ['tanggal,ticker,no_pengumuman', ...uma.map((x) => [x.UMADate.slice(0, 10), (x.CompanyID || '').trim(), q(x.AnnouncementNo)].join(','))].join('\n'));
  const sus = (await (await fetch('/primary/NewsAnnouncement/GetSuspension?indexFrom=1&dateFrom=&dateTo=&pageSize=9999&lang=id&type=', { headers: { Accept: 'application/json' } })).json()).Results || [];
  // asal: surat Divisi Pengawasan Transaksi (berkas *WAS_*) = cooling down perdagangan; From_EREP = kewajiban emiten
  const asal = (x) => { const p = x.Data_Download || ''; return /WAS_|WAS-|_WAS/i.test(p) ? 'pengawasan_perdagangan' : (/From_EREP/i.test(p) ? 'keterbukaan_emiten' : (/Exchange/i.test(p) ? 'bursa_lain' : 'lain')); };
  unduh('suspensi.csv', ['waktu,jenis,ticker,asal,judul', ...sus.map((x) => [x.Date, x.Info_Type, (x.Kode || '').trim(), asal(x), q((x.Judul || '').replace(/[\t\n\r]+/g, ' ').trim())].join(','))].join('\n'));
  console.log(`UMA ${uma.length}, suspensi ${sus.length}`);
})();
