"""Gorengan Radar, langkah 2: Transformer + nnPU vs pembanding, dievaluasi out-of-time.

Input : data/olah/radar/radar.npz (10_radar_data.py)
Model : (a) regresi logistik dan (b) gradient boosting pada ringkasan jendela (pembanding klasik);
        (c) Transformer encoder pada urutan 30 hari, loss BCE (berlabel = positif, sisanya negatif);
        (d) Transformer yang sama dengan loss nnPU (Kiryo dkk. 2017): sisanya diperlakukan sebagai TIDAK BERLABEL
            dengan prior pi (porsi positif tersembunyi), karena BEI tidak menandai semua saham gorengan.
Evaluasi di periode uji 2026 (tidak pernah dilihat saat latih/pemilihan): ROC-AUC, average precision (AP),
presisi di 1% skor tertinggi per hari, dan AUC di dalam tiap tersil ukuran (supaya model tidak sekadar
menebak "saham kecil").
Output: data/olah/radar/skor.csv.gz (skor validasi+uji, hanya untuk analisis agregat; tidak dipublikasikan),
        hasil/lanjutan/radar_evaluasi.csv, radar_kurva_latih.csv, ringkasan_radar.md
"""
import json
import sys
import time

import numpy as np
import pandas as pd
import torch
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from torch import nn

import konfigurasi as k

DIR = k.DATA_OLAH / "radar"
OUT = k.HASIL / "lanjutan"
torch.set_num_threads(12)
PI = 0.01  # prior positif tersembunyi di antara yang tidak berlabel


def muat():
    d = np.load(DIR / "radar.npz", allow_pickle=True)
    cfg = json.load(open(DIR / "fitur.json"))
    return d, cfg


def jendela(d, L, idx):
    w = idx[:, None] - (L - 1) + np.arange(L)
    return d["X"][w], d["S"][idx]


def ringkasan(X, S):
    """Fitur tangan untuk pembanding klasik: hari terakhir + agregat 5/20 hari."""
    r = X[:, :, 0]
    return np.c_[X[:, -1, :], X[:, -5:, :].mean(1), X[:, -20:, :].mean(1), X[:, -5:, :].max(1),
                 r[:, -5:].sum(1), r[:, -20:].sum(1), r[:, -20:].std(1), S]


class Radar(nn.Module):
    def __init__(self, f, s, L, d=48, kepala=4, lapis=2):
        super().__init__()
        self.masuk = nn.Linear(f, d)
        self.posisi = nn.Parameter(torch.zeros(1, L, d))
        self.statis = nn.Linear(s, d)
        lap = nn.TransformerEncoderLayer(d, kepala, dim_feedforward=2 * d, dropout=0.1, batch_first=True)
        self.enkoder = nn.TransformerEncoder(lap, lapis)
        self.kepala = nn.Sequential(nn.LayerNorm(2 * d), nn.Linear(2 * d, d), nn.GELU(), nn.Linear(d, 1))

    def forward(self, x, s):
        h = self.enkoder(self.masuk(x) + self.posisi + self.statis(s)[:, None, :])
        return self.kepala(torch.cat([h[:, -1], h.mean(1)], 1)).squeeze(1)


def loss_nnpu(z, y, pi, beta=0.0, gamma=1.0):
    """nnPU untuk data tidak seimbang (Su, Chen & Xu 2021): risiko positif dan negatif diberi bobot 0,5 masing-masing.

    nnPU biasa (Kiryo dkk. 2017) memberi bobot pi pada risiko positif; dengan pi ~1% sinyal positif nyaris hilang
    (versi pertama model ini macet di AUC 0,68). Koreksi non-negatif tetap dipakai pada risiko negatif.
    """
    sig = lambda v: torch.sigmoid(-v)  # loss sigmoid l(z, +1) = sigmoid(-z)
    p, u = y == 1, y == 0
    risiko_p = sig(z[p]).mean() if p.any() else z.new_zeros(())
    risiko_p_neg = sig(-z[p]).mean() if p.any() else z.new_zeros(())
    risiko_u_neg = sig(-z[u]).mean()
    neg = (risiko_u_neg - pi * risiko_p_neg) / (1 - pi)
    if neg < -beta:  # koreksi non-negatif: risiko negatif tidak boleh di bawah nol
        return -gamma * 0.5 * neg
    return 0.5 * risiko_p + 0.5 * neg


def latih_transformer(d, L, jenis, seed=0, epoch=12, langkah=250, bs=1024, pi=None, val_n=None):
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    idx, bag, y = d["idx"], d["bagian"], d["y"]
    tr, va = idx[bag == 0], idx[bag == 1]
    if val_n:  # subsampel validasi tetap (lebih cepat untuk banyak varian)
        va = np.sort(np.random.default_rng(99).choice(va, val_n, replace=False))
    pi = PI if pi is None else pi
    pos, neg = tr[y[tr] == 1], tr[y[tr] == 0]
    m = Radar(d["X"].shape[1], d["S"].shape[1], L)
    opt = torch.optim.AdamW(m.parameters(), lr=1e-3, weight_decay=1e-4)
    bce = nn.BCEWithLogitsLoss()
    terbaik, kurva, simpan = -1, [], None
    for ep in range(epoch):
        m.train()
        t0 = time.time()
        for _ in range(langkah):
            b = np.r_[rng.choice(pos, bs // 4), rng.choice(neg, bs - bs // 4)]  # 25% positif per batch
            x, s = jendela(d, L, b)
            z = m(torch.from_numpy(x), torch.from_numpy(s))
            yy = torch.from_numpy(y[b])
            loss = bce(z, yy) if jenis == "bce" else loss_nnpu(z, yy, pi)
            opt.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(m.parameters(), 1.0)
            opt.step()
        sk = prediksi(m, d, L, va)
        ap = average_precision_score(y[va], sk)
        kurva.append({"model": f"transformer_{jenis}", "seed": seed, "epoch": ep + 1, "ap_validasi": ap,
                      "auc_validasi": roc_auc_score(y[va], sk), "detik": time.time() - t0})
        print(kurva[-1], flush=True)
        if ap > terbaik:
            terbaik, simpan = ap, {k_: v.clone() for k_, v in m.state_dict().items()}
    m.load_state_dict(simpan)
    return m, kurva


@torch.no_grad()
def prediksi(m, d, L, idx, bs=8192):
    m.eval()
    out = []
    for i in range(0, len(idx), bs):
        x, s = jendela(d, L, idx[i:i + bs])
        out.append(m(torch.from_numpy(x), torch.from_numpy(s)).numpy())
    return np.concatenate(out)


def evaluasi(nama, skor, y, tgl, mcap):
    df = pd.DataFrame({"s": skor, "y": y, "t": tgl, "m": mcap})
    top = df.groupby("t", group_keys=False).apply(lambda g: g.nlargest(max(1, len(g) // 100), "s"))
    df["tersil"] = pd.qcut(df["m"], 3, labels=["kecil", "menengah", "besar"])
    hasil = {"model": nama, "roc_auc": roc_auc_score(y, skor), "ap": average_precision_score(y, skor),
             "presisi_top1pct": top["y"].mean(), "lift_top1pct": top["y"].mean() / y.mean(), "basis_positif": y.mean()}
    for t_, g in df.groupby("tersil", observed=True):
        hasil[f"auc_{t_}"] = roc_auc_score(g["y"], g["s"]) if g["y"].nunique() > 1 else np.nan
    return hasil


def md(df, fmt="{:.3f}"):
    kol = df.columns.tolist()
    b = ["| " + " | ".join(kol) + " |", "|" + "---|" * len(kol)]
    for _, r in df.iterrows():
        b.append("| " + " | ".join(fmt.format(v) if isinstance(v, float) else str(v) for v in r) + " |")
    return "\n".join(b)


def main():
    d, cfg = muat()
    L = cfg["L"]
    idx, bag, y = d["idx"], d["bagian"], d["y"]
    tr, va, te = idx[bag == 0], idx[bag == 1], idx[bag == 2]
    tgl, mcap = d["tanggal"], d["mcap"]
    hasil, skor_semua = [], {}
    rng = np.random.default_rng(0)
    # pembanding klasik: latih pada semua positif + 150 ribu sampel tidak berlabel
    sub = np.r_[tr[y[tr] == 1], rng.choice(tr[y[tr] == 0], 150_000, replace=False)]
    Ztr = ringkasan(*jendela(d, L, sub))
    vt = np.r_[va, te]
    Zvt = np.concatenate([ringkasan(*jendela(d, L, vt[i:i + 50_000])) for i in range(0, len(vt), 50_000)])
    for nama, model in [("logistik", LogisticRegression(max_iter=2000, C=0.5)),
                        ("gradient_boosting", HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, random_state=0))]:
        model.fit(Ztr, y[sub])
        skor_semua[nama] = model.predict_proba(Zvt)[:, 1]
        print(nama, "selesai", flush=True)
    kurva = []
    for jenis in ["bce", "nnpu"]:
        berkas = DIR / f"transformer_{jenis}.pt"
        if berkas.exists() and "--latih-ulang" not in sys.argv:  # pakai model yang sudah dilatih
            m = Radar(d["X"].shape[1], d["S"].shape[1], L)
            m.load_state_dict(torch.load(berkas))
        else:
            m, kv = latih_transformer(d, L, jenis, epoch=6)
            kurva += kv
        skor_semua[f"transformer_{jenis}"] = prediksi(m, d, L, vt)
        torch.save(m.state_dict(), DIR / f"transformer_{jenis}.pt")
    nte = len(te)
    for nama, s in skor_semua.items():
        hasil.append(evaluasi(nama, s[len(va):], y[te], tgl[te], mcap[te]))
    ev = pd.DataFrame(hasil)
    ev.to_csv(OUT / "radar_evaluasi.csv", index=False)
    if kurva:
        pd.DataFrame(kurva).to_csv(OUT / f"radar_kurva_latih_{'_'.join(sorted({r_['model'] for r_ in kurva}))}.csv", index=False)
    skor = pd.DataFrame({"ticker": d["ticker"][vt], "tanggal": tgl[vt], "bagian": np.where(np.arange(len(vt)) < len(va), "validasi", "uji"),
                         "y": y[vt], **{f"skor_{n}": s for n, s in skor_semua.items()}})
    skor.to_csv(DIR / "skor.csv.gz", index=False)
    print(ev.round(3).to_string(index=False))
    teks = ["# Gorengan Radar v0 (deep learning)", "",
            f"Sampel: jendela {L} hari bursa per saham-hari; label = UMA/suspensi pengawasan BEI dalam 1-{cfg['H']} hari ke depan. "
            f"Latih s.d. {cfg['batas']['latih']}, validasi s.d. {cfg['batas']['validasi']} (pemilihan epoch), uji 2026 "
            f"({nte:,} jendela, positif {y[te].mean() * 100:.2f}%). nnPU prior pi = {PI}.", "",
            "## Evaluasi out-of-time (periode uji 2026)", "", md(ev.round(3)), "",
            "Catatan: label BEI tidak lengkap, jadi presisi terhadap label adalah batas bawah. AUC per tersil ukuran menunjukkan "
            "apakah model membedakan saham di dalam kelompok ukuran yang sama, bukan sekadar menebak saham kecil.", "",
            "Skor per saham disimpan lokal untuk analisis agregat dan tidak dipublikasikan."]
    (OUT / "ringkasan_radar.md").write_text("\n".join(teks), encoding="utf-8")


if __name__ == "__main__":
    main()
