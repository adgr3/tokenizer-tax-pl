"""Krok 8: analiza w agregacie (prośba prowadzącego: „więcej tokenizerów i analiza w agregacie vs języki”).

Wejście: results/local/*.json, results/apisum/*.json, results/polish/*.json (opcjonalnie).
Wyjście: results/tables/*.csv i results/summary.json — jedyne źródło liczb dla raportu.

Zasady:
  * jeden tokenizer = jedna kolumna w agregatach; modele dzielące tokenizer (ten sam odcisk) to aliasy;
  * polskie modele z polecenia prowadzącego zostają w tabeli replikacji nawet jako aliasy (z dopiskiem „= X”);
  * enkodery (NERGAL/XLM-R, HerBERT…) poza agregatem LLM, w osobnej tabeli;
  * model z API = alias tokenizera lokalnego, gdy na tych samych blokach różni się o ≤ 0,01 tok./słowo w każdym języku.

    python -m tt.analyze [--config tokenizers.yaml]
"""
from __future__ import annotations

import argparse
import math

import numpy as np
import pandas as pd

from .common import RESULTS, languages, load_yaml, read_json, write_json

API_ALIAS_TOL = 0.01
LLM_GROUPS = ("global", "eu", "pl", "api")


def load_results(config: str) -> list[dict]:
    order = [s["id"] for s in load_yaml(config)["tokenizers"]]
    local = {r["id"]: r for r in (read_json(p) for p in (RESULTS / "local").glob("*.json"))}
    ordered = [local[i] for i in order if i in local] + [r for i, r in local.items() if i not in order]
    api = [read_json(p) for p in sorted((RESULTS / "apisum").glob("*.json"))]
    return ordered + api


def assign_aliases(results: list[dict]) -> None:
    first_by_fp = {}
    for r in results:
        r["alias_of"] = None
        if r["method"] != "local":
            continue
        fp = r["fingerprint"]
        if fp in first_by_fp:
            r["alias_of"] = first_by_fp[fp]
        else:
            first_by_fp[fp] = r["id"]
    canon_local = [r for r in results if r["method"] == "local" and not r["alias_of"] and r["group"] != "encoder"]
    for r in results:
        if r["method"] == "local":
            continue
        best = None
        for c in canon_local:
            diffs = []
            for code, lang in r["languages"].items():
                cl = c["languages"].get(code)
                if not cl:
                    continue
                idx = [b["block"] for b in lang["blocks"]]
                sub = [cl["blocks"][i]["tokens"] / cl["blocks"][i]["words"] for i in idx if i < len(cl["blocks"])]
                if sub:
                    diffs.append(abs(lang["fertility"] - sum(sub) / len(sub)))
            if diffs and max(diffs) <= API_ALIAS_TOL and (best is None or max(diffs) < best[1]):
                best = (c["id"], max(diffs))
        if best:
            r["alias_of"] = best[0]


def long_table(results: list[dict]) -> pd.DataFrame:
    meta = {lang["code"]: lang for lang in languages()}
    labels = {r["id"]: r["label"] for r in results}
    rows = []
    for r in results:
        for code, lang in r["languages"].items():
            if lang.get("fertility") is None:
                continue
            m = meta[code]
            chars = sum(b["chars"] for b in lang["blocks"])
            byts = sum(b.get("bytes", b["chars"]) for b in lang["blocks"])
            toks = sum(b["tokens"] for b in lang["blocks"])
            rows.append({
                "tokenizer": r["id"], "label": r["label"], "method": r["method"], "group": r["group"],
                "origin": r.get("origin"), "vocab_size": r.get("vocab_size"), "polish_model": r.get("polish_model"),
                "bench_ref": r.get("bench_ref"), "alias_of": r.get("alias_of"),
                "alias_label": labels.get(r.get("alias_of")) if r.get("alias_of") else None,
                "repo_used": r.get("repo_used"), "input_usd_per_m": r.get("input_usd_per_m"),
                "language": code, "language_pl": m["pl"], "language_en": m["name_en"], "family": m["family"],
                "script": m["script"], "fertility": lang["fertility"], "se": lang.get("se"),
                "n_blocks": lang.get("n_blocks"), "chars_per_token": chars / toks if toks else None,
                "bytes_per_token": byts / toks if toks else None})
    return pd.DataFrame(rows)


def vocab_bucket(v) -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "nieznany (API)"
    v = float(v)
    if v <= 64_000:
        return "≤ 64 tys."
    if v <= 160_000:
        return "64–160 tys."
    if v <= 210_000:
        return "160–210 tys."
    return "> 210 tys."


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="tokenizers.yaml")
    args = ap.parse_args(argv)

    results = load_results(args.config)
    if not results:
        print("Brak wyników.")
        return 1
    assign_aliases(results)
    df = long_table(results)
    tables = RESULTS / "tables"
    tables.mkdir(parents=True, exist_ok=True)
    df.to_csv(tables / "fertility_long.csv", index=False, encoding="utf-8")

    lang_order = [lang["code"] for lang in languages()]
    wide = df.pivot_table(index="language", columns="tokenizer", values="fertility").reindex(lang_order)
    wide.to_csv(tables / "fertility_wide.csv", encoding="utf-8")

    uniq = df[df["group"].isin(LLM_GROUPS) & df["alias_of"].isna()]
    U = uniq.pivot_table(index="language", columns="tokenizer", values="fertility").reindex(lang_order)
    en = U.loc["eng_Latn"]
    ratio = U.divide(en, axis=1)
    lang_meta = {lang["code"]: lang for lang in languages()}

    # --- agregat po językach
    agg_lang = pd.DataFrame({
        "language_pl": [lang_meta[c]["pl"] for c in U.index], "family": [lang_meta[c]["family"] for c in U.index],
        "script": [lang_meta[c]["script"] for c in U.index],
        "mean": U.mean(axis=1), "median": U.median(axis=1), "sd": U.std(axis=1), "min": U.min(axis=1),
        "min_tokenizer": U.idxmin(axis=1), "max": U.max(axis=1), "max_tokenizer": U.idxmax(axis=1),
        "tax_vs_en_mean": ratio.mean(axis=1), "n_tokenizers": U.notna().sum(axis=1)}, index=U.index)
    agg_lang["rank"] = agg_lang["mean"].rank(method="min").astype(int)
    agg_lang.to_csv(tables / "agg_languages.csv", encoding="utf-8")

    # --- agregat po rodzinach i pismach
    long_u = uniq.copy()
    long_u["tax_vs_en"] = long_u.apply(lambda r: r["fertility"] / en.get(r["tokenizer"], float("nan")), axis=1)
    agg_fam = long_u.groupby("family").agg(mean=("fertility", "mean"), tax_vs_en=("tax_vs_en", "mean"),
                                           languages=("language", "nunique")).sort_values("mean")
    agg_fam.to_csv(tables / "agg_families.csv", encoding="utf-8")
    agg_script = long_u.groupby("script").agg(mean=("fertility", "mean"), tax_vs_en=("tax_vs_en", "mean"),
                                              languages=("language", "nunique")).sort_values("mean")
    agg_script.to_csv(tables / "agg_scripts.csv", encoding="utf-8")

    # --- agregat po tokenizerach
    info = uniq.drop_duplicates("tokenizer").set_index("tokenizer")
    non_en = ratio.drop(index="eng_Latn")
    agg_tok = pd.DataFrame({
        "label": info["label"], "group": info["group"], "origin": info["origin"], "method": info["method"],
        "vocab_size": info["vocab_size"], "mean_25": U.mean(axis=0), "en": U.loc["eng_Latn"], "pl": U.loc["pol_Latn"],
        "pl_vs_en": ratio.loc["pol_Latn"], "worst_language": non_en.idxmax(axis=0), "worst_vs_en": non_en.max(axis=0),
        "cv_25": U.std(axis=0) / U.mean(axis=0),
        "pl_words_per_4096": 4096 / U.loc["pol_Latn"], "en_words_per_4096": 4096 / U.loc["eng_Latn"],
        "input_usd_per_m": info["input_usd_per_m"]})
    agg_tok["pl_rank"] = agg_tok["pl"].rank(method="min").astype(int)
    agg_tok["mean_rank"] = agg_tok["mean_25"].rank(method="min").astype(int)
    agg_tok["usd_per_1000_pl_words"] = agg_tok["pl"] * 1000 * agg_tok["input_usd_per_m"] / 1e6
    agg_tok["vocab_bucket"] = agg_tok["vocab_size"].map(vocab_bucket)
    pl_bpt = uniq[uniq["language"] == "pol_Latn"].set_index("tokenizer")["bytes_per_token"]
    agg_tok["pl_bytes_per_token"] = pl_bpt
    agg_tok = agg_tok.sort_values("pl")
    agg_tok.to_csv(tables / "agg_tokenizers.csv", encoding="utf-8")

    # --- grupy tokenizerów
    agg_origin = agg_tok.groupby("origin").agg(n=("label", "count"), pl=("pl", "mean"), mean_25=("mean_25", "mean"),
                                               pl_vs_en=("pl_vs_en", "mean")).sort_values("pl")
    agg_origin.to_csv(tables / "agg_origin.csv", encoding="utf-8")
    agg_vocab = agg_tok.groupby("vocab_bucket").agg(n=("label", "count"), pl=("pl", "mean"), mean_25=("mean_25", "mean"),
                                                    pl_vs_en=("pl_vs_en", "mean")).sort_values("pl")
    agg_vocab.to_csv(tables / "agg_vocab.csv", encoding="utf-8")

    # --- stabilność rankingu między językami (Spearman po tokenizerach)
    rank_corr = U.T.corr(method="spearman")
    rank_corr.to_csv(tables / "spearman_languages.csv", encoding="utf-8")
    off = rank_corr.where(~np.eye(len(rank_corr), dtype=bool))
    pl_corr = off.loc["pol_Latn"].drop("pol_Latn")

    # --- słownik vs polski
    vt = agg_tok.dropna(subset=["vocab_size"])
    vocab_rho = vt["vocab_size"].astype(float).corr(vt["pl"], method="spearman") if len(vt) >= 4 else None
    vocab_rho_en = vt["vocab_size"].astype(float).corr(vt["en"], method="spearman") if len(vt) >= 4 else None

    # --- replikacja (6 z pracy + polskie modele), z aliasami
    rep_ids = [r["id"] for r in results if r.get("calibration")] + \
              [r["id"] for r in results if r.get("polish_model") and not r.get("calibration")]
    rep = df[df["tokenizer"].isin(rep_ids)].pivot_table(index="language", columns="tokenizer", values="fertility")
    rep = rep.reindex(index=lang_order, columns=[i for i in rep_ids if i in rep.columns])
    rep.to_csv(tables / "replication.csv", encoding="utf-8")

    # --- Bench Team: Slayer + 5 modeli odniesienia + Pythia
    bench = df[(df["bench_ref"] == True) & df["language"].isin(["eng_Latn", "pol_Latn"])]  # noqa: E712
    bench_t = bench.pivot_table(index=["tokenizer", "label"], columns="language",
                                values=["fertility", "bytes_per_token", "chars_per_token"])
    if len(bench_t):
        bench_t.columns = [f"{a}_{b}" for a, b in bench_t.columns]
        bench_t = bench_t.reset_index()
        slayer = bench_t[bench_t["tokenizer"] == "slayer1b"]
        if len(slayer):
            s_pl = float(slayer["fertility_pol_Latn"].iloc[0])
            bench_t["tokens_vs_slayer_pl"] = bench_t["fertility_pol_Latn"] / s_pl
        bench_t.to_csv(tables / "bench_team.csv", index=False, encoding="utf-8")

    # --- NERGAL: enkodery
    enc = df[(df["group"] == "encoder") & (df["language"] == "pol_Latn")].copy()
    if len(enc):
        enc["pl_words_per_510"] = 510 / enc["fertility"]
        enc["pl_chars_per_510"] = 510 * enc["chars_per_token"]
        base = enc[enc["tokenizer"] == "nergal"]
        if len(base):
            enc["tokens_vs_nergal"] = enc["fertility"] / float(base["fertility"].iloc[0])
        enc[["tokenizer", "label", "alias_label", "vocab_size", "fertility", "chars_per_token", "pl_words_per_510",
             "pl_chars_per_510"] + (["tokens_vs_nergal"] if "tokens_vs_nergal" in enc else [])].sort_values("fertility") \
            .to_csv(tables / "nergal_encoders.csv", index=False, encoding="utf-8")

    # --- polskie rejestry
    reg_files = sorted((RESULTS / "polish").glob("*.json"))
    reg_summary = None
    if reg_files:
        rows = []
        for p in reg_files:
            r = read_json(p)
            for key, v in r["registers"].items():
                rows.append({"tokenizer": r["id"], "label": r["label"], "register": v["label"], "fertility": v["fertility"]})
        regdf = pd.DataFrame(rows)
        regw = regdf.pivot_table(index="tokenizer", columns="register", values="fertility")
        groups = df.drop_duplicates("tokenizer").set_index("tokenizer")["group"]
        regw = regw[[groups.get(i) != "encoder" for i in regw.index]]
        sib_pl = wide.loc["pol_Latn"]
        regw["SIB-200 (wiadomości)"] = sib_pl.reindex(regw.index)
        regw.to_csv(tables / "polish_registers.csv", encoding="utf-8")
        reg_corr = regw.corr(method="spearman")["SIB-200 (wiadomości)"].drop("SIB-200 (wiadomości)")
        reg_summary = {"n_tokenizers": int(len(regw)), "spearman_vs_sib": reg_corr.round(3).to_dict(),
                       "register_means": regw.mean().round(3).to_dict()}

    calib = read_json(RESULTS / "calibration.json")["summary"] if (RESULTS / "calibration.json").exists() else None
    spend = read_json(RESULTS / "api" / "spend.json") if (RESULTS / "api" / "spend.json").exists() else None
    skipped = read_json(RESULTS / "skipped.json") if (RESULTS / "skipped.json").exists() else {}
    aliases = {r["id"]: r["alias_of"] for r in results if r.get("alias_of")}
    pl = agg_lang.loc["pol_Latn"]
    summary = {
        "n_tokenizers_measured": len(results), "n_unique_llm": int(U.shape[1]),
        "n_local": sum(1 for r in results if r["method"] == "local"), "n_api": sum(1 for r in results if r["method"] != "local"),
        "n_encoders": int(df[df["group"] == "encoder"]["tokenizer"].nunique()),
        "aliases": aliases, "skipped": {k: v["reason"][:160] for k, v in skipped.items()},
        "calibration": calib, "api_spend": spend,
        "polish": {"mean": round(float(pl["mean"]), 3), "rank_of_25": int(pl["rank"]),
                   "tax_vs_en": round(float(pl["tax_vs_en_mean"]), 3), "min": round(float(pl["min"]), 3),
                   "min_tokenizer": pl["min_tokenizer"], "max": round(float(pl["max"]), 3), "max_tokenizer": pl["max_tokenizer"],
                   "spearman_with_other_languages_mean": round(float(pl_corr.mean()), 3),
                   "most_similar_language_ranking": pl_corr.idxmax(), "least_similar_language_ranking": pl_corr.idxmin()},
        "languages_best": agg_lang.sort_values("mean").head(3)[["language_pl", "mean"]].round(3).to_dict("records"),
        "languages_worst": agg_lang.sort_values("mean").tail(3)[["language_pl", "mean"]].round(3).to_dict("records"),
        "families": agg_fam["mean"].round(3).to_dict(), "scripts": agg_script["mean"].round(3).to_dict(),
        "tokenizers_best_pl": agg_tok.head(5)[["label", "pl", "pl_vs_en"]].round(3).to_dict("records"),
        "tokenizers_worst_pl": agg_tok.tail(5)[["label", "pl", "pl_vs_en"]].round(3).to_dict("records"),
        "origin": agg_origin[["n", "pl", "pl_vs_en"]].round(3).to_dict("index"),
        "vocab": agg_vocab[["n", "pl", "pl_vs_en"]].round(3).to_dict("index"),
        "vocab_vs_pl_spearman": None if vocab_rho is None else round(float(vocab_rho), 3),
        "vocab_vs_en_spearman": None if vocab_rho_en is None else round(float(vocab_rho_en), 3),
        "mean_rank_correlation_between_languages": round(float(off.stack().mean()), 3),
        "polish_registers": reg_summary,
    }
    write_json(RESULTS / "summary.json", summary)
    print(f"Tokenizery: {summary['n_tokenizers_measured']} zmierzonych, {summary['n_unique_llm']} unikalnych LLM, "
          f"{summary['n_encoders']} enkoderów, aliasy: {len(aliases)}")
    print(f"Polski: średnio {summary['polish']['mean']} tok./słowo, miejsce {summary['polish']['rank_of_25']}/25, "
          f"{summary['polish']['tax_vs_en']}× angielski")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
