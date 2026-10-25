"""Gorengan Radar, langkah 6: autoencoder sebagai pembanding TANPA label.

Autoencoder dilatih merekonstruksi jendela 30 hari (10 fitur harian + 8 fitur statis) di periode latih, tanpa
melihat label UMA/suspensi sama sekali. Skor anomali = galat rekonstruksi fitur harian (MSE). Bila skor ini juga
memprediksi kerugian E1, berarti "keanehan pola perdagangan" sendiri -- bukan tiruan label BEI -- yang dihukum.
Dua arsitektur: MLP pada jendela yang diratakan, dan GRU (urutan). Masing-masing seed 0 dan 1.
Evaluasi: AUC/AP terhadap label di uji 2026; koefisien skor pra-event (sama dengan 13) dan uji run-up (14) untuk E1.

Output: data/olah/radar/varian/ae_*.pt dan *_skor.npy; hasil/lanjutan/{radar_autoencoder.csv, ringkasan_radar_autoencoder.md}
"""
import importlib.util
import time
import warnings

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import average_precision_score, roc_auc_score
from torch import nn

import konfigurasi as k

warnings.filterwarnings("ignore")
torch.set_num_threads(12)


def _modul(nama, file):
    spec = importlib.util.spec_from_file_location(nama, k.ROOT / "analisis" / file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


rk = _modul("rk", "13_radar_ketahanan.py")
ru = _modul("ru", "14_radar_runup.py")
pl = _modul("pl", "04_placebo_permutasi.py")
rm = rk.rm
OUT = k.HASIL / "lanjutan"


class AEMLP(nn.Module):
    def __init__(self, f, s, L, z=16):
        super().__init__()
        n = L * f + s
        self.enc = nn.Sequential(nn.Linear(n, 128), nn.GELU(), nn.Linear(128, z))
        self.dec = nn.Sequential(nn.Linear(z, 128), nn.GELU(), nn.Linear(128, L * f))
        self.L, self.f = L, f

    def forward(self, x, s):
        h = self.enc(torch.cat([x.flatten(1), s], 1))
        return self.dec(h).view(-1, self.L, self.f)


class AEGRU(nn.Module):
    def __init__(self, f, s, L, d=48, z=16):
        super().__init__()
        self.enc = nn.GRU(f, d, batch_first=True)
        self.ke_z = nn.Linear(d + s, z)
        self.dari_z = nn.Linear(z, d)
        self.dec = nn.GRU(f, d, batch_first=True)
        self.keluar = nn.Linear(d, f)
        self.L, self.f = L, f

    def forward(self, x, s):
        _, h = self.enc(x)
        z = self.ke_z(torch.cat([h[-1], s], 1))
        h0 = self.dari_z(z)[None]
        # decoder: teacher forcing digeser satu langkah (input = hari sebelumnya, hari pertama = nol)
        masuk = torch.cat([torch.zeros_like(x[:, :1]), x[:, :-1]], 1)
        o, _ = self.dec(masuk, h0)
        return self.keluar(o)


def latih(kelas, d, L, seed, epoch=4, langkah=300, bs=2048):
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    tr = d["idx"][d["bagian"] == 0]  # SEMUA jendela latih; label tidak dipakai
    m = kelas(d["X"].shape[1], d["S"].shape[1], L)
    opt = torch.optim.AdamW(m.parameters(), lr=1e-3, weight_decay=1e-5)
    for ep in range(epoch):
        t0, tot = time.time(), 0.0
        m.train()
        for _ in range(langkah):
            x, s = rm.jendela(d, L, rng.choice(tr, bs))
            x, s = torch.from_numpy(x), torch.from_numpy(s)
            loss = ((m(x, s) - x) ** 2).mean()
            opt.zero_grad()
            loss.backward()
            opt.step()
            tot += loss.item()
        print(f"{kelas.__name__} seed {seed} epoch {ep + 1}: mse {tot / langkah:.4f} ({time.time() - t0:.0f} dtk)", flush=True)
    return m


@torch.no_grad()
def galat(m, d, L, idx, bs=8192):
    m.eval()
    out = []
    for i in range(0, len(idx), bs):
        x, s = rm.jendela(d, L, idx[i:i + bs])
        x = torch.from_numpy(x)
        out.append(((m(x, torch.from_numpy(s)) - x) ** 2).mean((1, 2)).numpy())
    return np.concatenate(out)


def md(df, fmt="{:.3f}"):
    kol = df.columns.tolist()
    b = ["| " + " | ".join(kol) + " |", "|" + "---|" * len(kol)]
    for _, r in df.iterrows():
        b.append("| " + " | ".join(fmt.format(v) if isinstance(v, float) else str(v) for v in r) + " |")
    return "\n".join(b)


def main():
    d, cfg = rm.muat()
    L = cfg["L"]
    idx, bag, y = d["idx"], d["bagian"], d["y"]
    te = idx[bag == 2]
    vt = np.r_[idx[bag == 1], te]
    tgl_vt, tk_vt = d["tanggal"][vt], d["ticker"][vt]
    rk.VAR.mkdir(parents=True, exist_ok=True)
    skor = {}
    for kelas, nm in [(AEMLP, "ae_mlp"), (AEGRU, "ae_gru")]:
        for seed in [0, 1]:
            nama = f"{nm}_s{seed}"
            f = rk.VAR / f"{nama}_skor.npy"
            if not f.exists():
                m = latih(kelas, d, L, seed)
                torch.save(m.state_dict(), rk.VAR / f"{nama}.pt")
                np.save(f, galat(m, d, L, vt))
            skor[nama] = np.load(f)
    # pembanding: ensembel Transformer berlabel
    z = lambda a: (a - a.mean()) / a.std()
    trans = np.mean([z(np.load(rk.VAR / f"{n}_skor.npy")) for n, *_ in rk.VARIAN], axis=0)
    data = pl.siapkan()
    ev, plac = rk.siapkan_sampel(data)
    r = data[0]
    ev_r = {e: ru.tambah_runup(s, r, k.EVENTS[e]["hari0"]) for e, s in ev.items()}
    plac_r = {t: ru.tambah_runup(s, r, t) for t, s in plac.items()}
    baris = []
    for nama, s in list(skor.items()) + [("transformer_ensembel", trans)]:
        lbl = {"skor": nama, "auc_uji": roc_auc_score(y[te], s[-len(te):]), "ap_uji": average_precision_score(y[te], s[-len(te):]),
               "korelasi_dg_transformer": np.corrcoef(s, trans)[0, 1]}
        for r_ in rk.uji_event(s, tgl_vt, tk_vt, ev, plac):
            baris.append({**lbl, **r_})
        # run-up fleksibel untuk E1 [0,+5] (14, S2)
        pk = [ru.koef(ru.siapkan(ps, rk.rata_pra(s, tgl_vt, tk_vt, t)), "car_0_5", "S2 + run-up fleksibel")[0] for t, ps in plac_r.items()]
        b, p, _ = ru.koef(ru.siapkan(ev_r["E1"], rk.rata_pra(s, tgl_vt, tk_vt, k.EVENTS["E1"]["hari0"])), "car_0_5", "S2 + run-up fleksibel")
        baris.append({**lbl, "sel": "E1 car_0_5 + run-up fleksibel", "koef": b, "p": p,
                      "p_placebo": ((np.array(pk) <= b).sum() + 1) / (len(pk) + 1)})
        print("selesai:", nama, flush=True)
    h = pd.DataFrame(baris)
    h.to_csv(OUT / "radar_autoencoder.csv", index=False)
    ring = h.drop_duplicates("skor")[["skor", "auc_uji", "ap_uji", "korelasi_dg_transformer"]]
    tab = h.pivot_table(index="skor", columns="sel", values="koef").round(2).astype(str) + " (" + \
        h.pivot_table(index="skor", columns="sel", values="p_placebo").round(3).astype(str) + ")"
    print(ring.round(3).to_string(index=False))
    print(tab.to_string())
    teks = ["# Autoencoder (tanpa label) vs Transformer berlabel", "",
            "Skor autoencoder = galat rekonstruksi jendela 30 hari; dilatih tanpa label. Basis positif uji 2026 = "
            f"{y[te].mean() * 100:.2f}%.", "", "## Akurasi terhadap label BEI (uji 2026)", "", md(ring.round(3)), "",
            "## Koefisien skor pra-event (pp per SD) dan p placebo (38 hari crash biasa; minimum 0,026)", "",
            md(tab.reset_index())]
    (OUT / "ringkasan_radar_autoencoder.md").write_text("\n".join(teks), encoding="utf-8")


if __name__ == "__main__":
    main()
