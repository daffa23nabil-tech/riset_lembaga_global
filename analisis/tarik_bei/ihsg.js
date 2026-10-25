// Penutupan IHSG (COMPOSITE) per tanggal -> data/mentah/idx/ihsg.csv (untuk hari setelah data Refinitiv berakhir).
// Jalankan di konsol browser pada halaman idx.co.id. Tempel _unduh.js dulu.
const TANGGAL = ['20261016', '20261019', '20261020', '20261021', '20261022', '20261023'];
(async () => {
  const baris = ['date,JCI'];
  for (const d of TANGGAL) {
    const j = await (await fetch(`/primary/TradingSummary/GetIndexSummary?length=9999&start=0&date=${d}`, { headers: { Accept: 'application/json' } })).json();
    const c = (j.data || []).find((x) => x.IndexCode === 'COMPOSITE');
    if (c) baris.push(`${d.slice(0, 4)}-${d.slice(4, 6)}-${d.slice(6)},${c.Close}`);
  }
  unduh('ihsg.csv', baris.join('\n'));
})();
