// Laporan keuangan XBRL (instance.zip) 49 bank: Des 2025 (audit) dan Jun 2026 (TW2)
// -> data/mentah/idx/laporan_keuangan/<KODE>_<tahun>_<periode>.zip, dibaca analisis/01e_fundamental_bank.py.
// Jalankan di konsol browser pada halaman idx.co.id. Tempel _unduh.js dulu. Browser akan meminta izin banyak unduhan.
const BANK = 'AGRO AGRS AMAR ARTO BABP BACA BANK BBCA BBHI BBKP BBMD BBNI BBRI BBSI BBTN BBYB BCIC BDMN BEKS BGTG BINA BJBR BJTM BKSW BMAS BMRI BNBA BNGA BNII BNLI BRIS BSIM BSWD BTPN BTPS BVIC DNAR INPC MASB MAYA MCOR MEGA NISP NOBU PNBN PNBS SDRA SUPA VICO'.split(' ');
(async () => {
  const tanpa = [];
  for (const b of BANK) for (const [th, per] of [['2025', 'audit'], ['2026', 'tw2']]) {
    let j = null;
    try { j = await (await fetch(`/primary/ListedCompany/GetFinancialReport?indexFrom=1&pageSize=12&year=${th}&reportType=rdf&EmitenType=s&periode=${per}&kodeEmiten=${b}&SortColumn=KodeEmiten&SortOrder=asc`, { headers: { Accept: 'application/json' } })).json(); } catch (e) {}
    const att = ((j && j.Results && j.Results[0] && j.Results[0].Attachments) || []).find((a) => a.File_Name === 'instance.zip');
    if (!att) { tanpa.push(`${b} ${th} ${per}`); continue; }
    unduh(`${b}_${th}_${per}.zip`, await (await fetch(att.File_Path)).blob());
    await new Promise((z) => setTimeout(z, 300));
  }
  console.log('Tidak tersedia:', tanpa);
})();
