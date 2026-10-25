// Ringkasan Saham BEI per hari bursa -> berkas dump untuk analisis/00_urai_dump_idx.py.
// Jalankan di konsol browser pada halaman https://www.idx.co.id/id/data-pasar/ringkasan-perdagangan/ringkasan-saham/
// (permintaan harus dari domain idx.co.id). Tempel _unduh.js dulu.
// LENGKAP = true -> 16 kolom (periode 2023/2025: + OHLC, frekuensi, tradeable, nego, remarks); false -> 9 kolom (periode 2020).
const MULAI = '2025-01-01', AKHIR = '2026-10-23', LENGKAP = true;
(async () => {
  const hasil = [];
  const d = new Date(MULAI + 'T00:00:00Z'), e = new Date(AKHIR + 'T00:00:00Z');
  for (; d <= e; d.setUTCDate(d.getUTCDate() + 1)) {
    if ([0, 6].includes(d.getUTCDay())) continue;
    const s = d.toISOString().slice(0, 10).replace(/-/g, '');
    let j = null;
    for (let i = 0; i < 3 && !j; i++) {
      try { j = await (await fetch(`/primary/TradingSummary/GetStockSummary?length=9999&start=0&date=${s}`, { headers: { Accept: 'application/json' } })).json(); }
      catch (err) { await new Promise((z) => setTimeout(z, 2000)); }
    }
    const data = (j && j.data) || [];
    if (!data.length) continue; // hari libur
    const baris = data.map((x) => (LENGKAP
      ? [x.StockCode, x.Close, x.Previous, x.OpenPrice, x.High, x.Low, x.Volume, x.Value, x.Frequency, x.ForeignBuy, x.ForeignSell, x.ListedShares, x.TradebleShares, x.WeightForIndex, x.NonRegularVolume, (x.Remarks || '').trim()]
      : [x.StockCode, x.Close, x.Previous, x.Volume, x.Value, x.ForeignBuy, x.ForeignSell, x.ListedShares, x.WeightForIndex]).join(','));
    hasil.push(s + '\n' + baris.join('\n'));
    console.log(s, data.length);
    await new Promise((z) => setTimeout(z, 100));
  }
  unduh(`ringkasan_saham_${MULAI}_${AKHIR}.txt`, hasil.join('\n#\n'));
})();
// Lalu: python analisis/00_urai_dump_idx.py --periode 2025 ringkasan_saham_2025-01-01_2026-10-23.txt
