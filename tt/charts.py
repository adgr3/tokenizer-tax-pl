"""Krok 9: wykresy (PNG, 200 dpi) z results/tables/*.csv.

    python -m tt.charts
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from .common import CHARTS, RESULTS, languages  # noqa: E402

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.dpi": 100})
CMAP = "YlOrBr"
ORIGIN_COLORS = {"USA": "#4C72B0", "Chiny": "#C44E52", "UE": "#55A868", "Polska": "#DD8452", "inne": "#8172B3", None: "#999999"}
PL_RED = "#C0392B"
SOURCE_NOTE = "Pomiar: SIB-200 (test, 204 zdania), bloki ok. 6000 znaków, tokeny / słowa (podział po spacjach)."


def fmt(x, d=1):
    return "" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{d}f}".replace(".", ",")


def _labels(ids, long):
    lab = long.drop_duplicates("tokenizer").set_index("tokenizer")
    out = []
    for i in ids:
        r = lab.loc[i]
        name = r["label"]
        if isinstance(r.get("alias_label"), str) and r["alias_label"]:
            name += f"\n(= {r['alias_label']})"
        out.append(name)
    return out


def heatmap(mat: pd.DataFrame, col_labels, title, subtitle, path, split_at=None, highlight_cols=(), vmax=None):
    lang = {lang["code"]: lang["pl"] for lang in languages()}
    n_r, n_c = mat.shape
    fig_w = max(7, 1.0 + 0.62 * n_c)
    fig, ax = plt.subplots(figsize=(fig_w, 0.36 * n_r + 2.6))
    data = mat.to_numpy(dtype=float)
    vmax = vmax or max(6.0, np.nanmax(data))
    im = ax.imshow(data, cmap=CMAP, vmin=1.0, vmax=vmax, aspect="auto")
    for i in range(n_r):
        for j in range(n_c):
            v = data[i, j]
            if np.isnan(v):
                continue
            ax.text(j, i, fmt(v), ha="center", va="center", fontsize=7.5,
                    color="white" if v > vmax * 0.62 else "#222", fontweight="bold" if mat.index[i] == "pol_Latn" else None)
    ax.set_yticks(range(n_r), [lang.get(c, c) for c in mat.index])
    for t, c in zip(ax.get_yticklabels(), mat.index):
        if c == "pol_Latn":
            t.set_color(PL_RED)
            t.set_fontweight("bold")
    ax.set_xticks(range(n_c), col_labels, rotation=45, ha="left", fontsize=8)
    ax.xaxis.tick_top()
    for j, t in enumerate(ax.get_xticklabels()):
        if j in highlight_cols:
            t.set_color(PL_RED)
    if "pol_Latn" in list(mat.index):
        i = list(mat.index).index("pol_Latn")
        ax.add_patch(plt.Rectangle((-0.5, i - 0.5), n_c, 1, fill=False, lw=1.6, ec="#111"))
    if split_at:
        ax.axvline(split_at - 0.5, color="#111", lw=2)
    ax.set_xticks(np.arange(-0.5, n_c, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n_r, 1), minor=True)
    ax.grid(which="minor", color="white", lw=0.6)
    ax.tick_params(which="minor", length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02, label="tokeny na słowo (mniej = taniej)")
    fig.suptitle(title, x=0.02, ha="left", fontsize=15, fontweight="bold")
    fig.text(0.02, 0.945, subtitle, fontsize=9, color="#555")
    fig.text(0.02, 0.01, SOURCE_NOTE, fontsize=7.5, color="#777")
    fig.tight_layout(rect=(0, 0.025, 1, 0.93))
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main() -> int:
    t = RESULTS / "tables"
    CHARTS.mkdir(parents=True, exist_ok=True)
    long = pd.read_csv(t / "fertility_long.csv")
    lang_order = [lang["code"] for lang in languages()]
    made = []

    # 1. Replikacja: 6 tokenizerów z pracy + polskie modele (jak w poleceniu prowadzącego)
    rep = pd.read_csv(t / "replication.csv", index_col=0)
    pm = long.drop_duplicates("tokenizer").set_index("tokenizer")["polish_model"].fillna(False).astype(bool)
    paper = [c for c in rep.columns if not pm[c]]
    pol = [c for c in rep.columns if c not in paper]
    rep = rep[paper + pol]
    heatmap(rep, _labels(rep.columns, long), "Ile tokenów na jedno słowo?",
            "Replikacja arXiv 2605.24718 (lewa część) i polskie modele (prawa część)",
            CHARTS / "01_replikacja.png", split_at=len(paper), highlight_cols=range(len(paper), len(rep.columns)))
    made.append("01_replikacja.png")

    # 2. Wszystkie unikalne tokenizery LLM (+ API), języki i kolumny posortowane
    agg_tok = pd.read_csv(t / "agg_tokenizers.csv", index_col=0).sort_values("mean_25")
    agg_lang = pd.read_csv(t / "agg_languages.csv", index_col=0).sort_values("mean")
    wide = pd.read_csv(t / "fertility_wide.csv", index_col=0)
    allm = wide.reindex(index=agg_lang.index, columns=agg_tok.index)
    heatmap(allm, list(agg_tok["label"]), "Podatek tokenowy: wszystkie tokenizery",
            f"{allm.shape[1]} unikalnych tokenizerów LLM; języki od najtańszego, kolumny od najtańszego średnio",
            CHARTS / "02_wszystkie.png", highlight_cols=[i for i, g in enumerate(agg_tok["group"]) if g == "pl"])
    made.append("02_wszystkie.png")

    # 3. Agregat po językach: średnia i zakres po tokenizerach
    fig, ax = plt.subplots(figsize=(9, 7))
    al = agg_lang.sort_values("mean", ascending=False)
    y = np.arange(len(al))
    colors = [PL_RED if c == "pol_Latn" else "#C9873A" for c in al.index]
    ax.barh(y, al["mean"], color=colors, alpha=0.9)
    ax.errorbar(al["mean"], y, xerr=[al["mean"] - al["min"], al["max"] - al["mean"]], fmt="none", ecolor="#555", lw=0.8, capsize=2)
    ax.set_yticks(y, al["language_pl"])
    for i, (m, mx, tx) in enumerate(zip(al["mean"], al["max"], al["tax_vs_en_mean"])):
        ax.text(mx + 0.04, i, f"{fmt(m, 2)}  ({fmt(tx, 2)}× ang.)", va="center", fontsize=7.5, color="#333")
    ax.set_xlim(0, al["max"].max() * 1.32)
    ax.set_xlabel("tokeny na słowo: średnia po tokenizerach; kreska = najlepszy–najgorszy tokenizer")
    ax.set_title("Który język płaci najwięcej? Agregat po wszystkich tokenizerach", loc="left", fontweight="bold")
    fig.tight_layout()
    fig.savefig(CHARTS / "03_jezyki.png", dpi=200)
    plt.close(fig)
    made.append("03_jezyki.png")

    # 4. Rodziny językowe
    fam = pd.read_csv(t / "agg_families.csv", index_col=0).sort_values("tax_vs_en")
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.bar(fam.index, fam["tax_vs_en"], color=[PL_RED if f == "słowiańskie" else "#C9873A" for f in fam.index])
    for i, v in enumerate(fam["tax_vs_en"]):
        ax.text(i, v + 0.02, f"{fmt(v, 2)}×", ha="center", fontsize=8)
    ax.axhline(1, color="#555", lw=0.8, ls="--")
    ax.set_ylabel("ile razy więcej tokenów niż angielski")
    ax.set_title("Podatek tokenowy po rodzinach językowych (średnio)", loc="left", fontweight="bold")
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    fig.tight_layout()
    fig.savefig(CHARTS / "04_rodziny.png", dpi=200)
    plt.close(fig)
    made.append("04_rodziny.png")

    # 5. Ranking tokenizerów dla polskiego
    tok = agg_tok.sort_values("pl", ascending=False)
    fig, ax = plt.subplots(figsize=(8.5, 0.28 * len(tok) + 1.8))
    y = np.arange(len(tok))
    ax.barh(y, tok["pl"], color=[ORIGIN_COLORS.get(o, "#999") for o in tok["origin"]])
    ax.scatter(tok["en"], y, marker="|", s=120, color="#111", zorder=3, label="angielski (dla porównania)")
    ax.set_yticks(y, tok["label"], fontsize=8)
    for i, v in enumerate(tok["pl"]):
        ax.text(v + 0.03, i, fmt(v, 2), va="center", fontsize=7)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for k, c in ORIGIN_COLORS.items() if k and k in set(tok["origin"])]
    names = [k for k in ORIGIN_COLORS if k and k in set(tok["origin"])]
    ax.set_xlim(0, tok["pl"].max() * 1.12)
    ax.legend(handles + [ax.collections[-1]], names + ["angielski"], fontsize=8, loc="upper left",
              bbox_to_anchor=(1.01, 1), frameon=False)
    ax.set_xlabel("tokeny na polskie słowo (mniej = taniej i więcej tekstu w oknie)")
    ax.set_title("Który tokenizer najtaniej koduje polski?", loc="left", fontweight="bold")
    fig.tight_layout()
    fig.savefig(CHARTS / "05_ranking_polski.png", dpi=200)
    plt.close(fig)
    made.append("05_ranking_polski.png")

    # 6. Wielkość słownika vs polski
    vt = agg_tok.dropna(subset=["vocab_size"])
    if len(vt) >= 3:
        fig, ax = plt.subplots(figsize=(12, 8.5))
        ax.scatter(vt["vocab_size"], vt["pl"], c=[ORIGIN_COLORS.get(o, "#999") for o in vt["origin"]], s=40, zorder=3)
        ax.set_xscale("log")
        # punkty w tym samym miejscu (ten sam wynik, inny rozmiar słownika o kilka tokenów) → jeden podpis
        pts = {}
        for _, r in vt.iterrows():
            key = (round(np.log10(float(r["vocab_size"])), 2), round(float(r["pl"]), 2))
            pts.setdefault(key, [float(r["vocab_size"]), float(r["pl"]), []])[2].append(r["label"])
        fig.canvas.draw()
        placed = []
        for vx, vy, names in sorted(pts.values(), key=lambda p: (-p[1], p[0])):
            txt = " / ".join(names)
            # przesuwamy podpis w dół, aż nie nachodzi na wcześniejsze (prosty, deterministyczny „repel”)
            for dy in [2, -9, 11, -18, 20, -27, 29, -36]:
                t_ = ax.annotate(txt, (vx, vy), fontsize=7, xytext=(5, dy), textcoords="offset points")
                bb = t_.get_window_extent(renderer=fig.canvas.get_renderer()).expanded(1.02, 1.1)
                t_.remove()
                if not any(bb.overlaps(o) for o in placed):
                    placed.append(bb)
                    ax.annotate(txt, (vx, vy), fontsize=7, xytext=(5, dy), textcoords="offset points",
                                arrowprops=None if dy == 2 else {"arrowstyle": "-", "color": "#999", "lw": 0.5,
                                                                 "shrinkA": 0, "shrinkB": 3})
                    break
            else:
                placed.append(ax.annotate(txt, (vx, vy), fontsize=7, xytext=(5, 2), textcoords="offset points")
                              .get_window_extent(renderer=fig.canvas.get_renderer()))
        ax.set_xlabel("wielkość słownika tokenizera (skala log.)")
        ax.set_ylabel("tokeny na polskie słowo")
        ax.set_title("Czy większy słownik pomaga polskiemu?", loc="left", fontweight="bold")
        fig.tight_layout()
        fig.savefig(CHARTS / "06_slownik_vs_polski.png", dpi=200)
        plt.close(fig)
        made.append("06_slownik_vs_polski.png")

    # 7. Stabilność rankingu między językami
    sp = pd.read_csv(t / "spearman_languages.csv", index_col=0).reindex(index=lang_order, columns=lang_order)
    lang = {lang["code"]: lang["pl"] for lang in languages()}
    fig, ax = plt.subplots(figsize=(9, 8))
    im = ax.imshow(sp.to_numpy(dtype=float), cmap="RdYlGn", vmin=-1, vmax=1)
    ax.set_xticks(range(len(sp)), [lang[c] for c in sp.columns], rotation=90, fontsize=8)
    ax.set_yticks(range(len(sp)), [lang[c] for c in sp.index], fontsize=8)
    fig.colorbar(im, ax=ax, fraction=0.04, label="korelacja rang Spearmana")
    ax.set_title("Czy tokenizer dobry dla jednego języka jest dobry dla innego?", loc="left", fontweight="bold")
    fig.tight_layout()
    fig.savefig(CHARTS / "07_stabilnosc_rankingu.png", dpi=200)
    plt.close(fig)
    made.append("07_stabilnosc_rankingu.png")

    # 8. Polski na różnych rodzajach tekstu
    if (t / "polish_registers.csv").exists():
        reg = pd.read_csv(t / "polish_registers.csv", index_col=0)
        info = long.drop_duplicates("tokenizer").set_index("tokenizer")
        labels = info["label"]
        reg = reg[[info.loc[i, "group"] != "encoder" for i in reg.index]]
        reg = reg.sort_values("SIB-200 (wiadomości)")
        fig, ax = plt.subplots(figsize=(max(8, 0.5 * len(reg) + 3), 6.5))
        x = np.arange(len(reg))
        w = 0.8 / len(reg.columns)
        colors = plt.get_cmap("tab20").colors  # 13 rodzajów tekstu: paleta bez powtórzeń kolorów
        for k, col in enumerate(reg.columns):
            ax.bar(x + k * w, reg[col], width=w, label=col, color="#111" if col.startswith("SIB-200") else colors[k % 20])
        ax.set_xticks(x + 0.4 - w / 2, [labels.get(i, i) for i in reg.index], rotation=45, ha="right", fontsize=8)
        ax.set_xlim(-0.5, len(reg))
        ax.set_ylabel("tokeny na słowo")
        ax.legend(fontsize=8, ncol=7, loc="upper left", frameon=False)
        ax.set_ylim(0, reg.max().max() * 1.25)
        ax.set_title("Polski: czy ranking zależy od rodzaju tekstu?", loc="left", fontweight="bold")
        fig.tight_layout()
        fig.savefig(CHARTS / "08_polski_rodzaje_tekstu.png", dpi=200)
        plt.close(fig)
        made.append("08_polski_rodzaje_tekstu.png")

    # 9. NERGAL: enkodery — ile polskiego tekstu mieści okno 512 tokenów
    if (t / "nergal_encoders.csv").exists():
        enc = pd.read_csv(t / "nergal_encoders.csv").sort_values("pl_words_per_510")
        fig, ax = plt.subplots(figsize=(7.5, 0.5 * len(enc) + 1.8))
        ax.barh(enc["label"], enc["pl_words_per_510"], color=[PL_RED if i == "nergal" else "#C9873A" for i in enc["tokenizer"]])
        for i, (v, c) in enumerate(zip(enc["pl_words_per_510"], enc["pl_chars_per_510"])):
            ax.text(v + 2, i, f"{v:.0f} słów ≈ {c:.0f} znaków", va="center", fontsize=8)
        ax.set_xlabel("polskich słów w jednym oknie 512 tokenów")
        ax.set_title("NERGAL i inne enkodery: ile polskiego tekstu na okno", loc="left", fontweight="bold")
        fig.tight_layout()
        fig.savefig(CHARTS / "09_nergal_enkodery.png", dpi=200)
        plt.close(fig)
        made.append("09_nergal_enkodery.png")

    print("Wykresy:", ", ".join(made))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
