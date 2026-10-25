// Fungsi bantu bersama: simpan teks atau biner sebagai berkas unduhan di browser.
window.unduh = (nama, isi, tipe = 'text/plain') => {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(isi instanceof Blob ? isi : new Blob([isi], { type: tipe }));
  a.download = nama;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
};
