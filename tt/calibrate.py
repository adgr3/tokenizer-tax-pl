"""Krok 3: kalibracja — czy liczymy tak samo jak autor pracy arXiv 2605.24718.

Porównuje nasze wyniki dla tokenizerów z polem `calibration` z danymi autora
(overthelex/tokenizer-fertility-map, źródło SIB-200). Autor wykresu z kursu uzyskał średnio 0,007, maks. 0,049.

    python -m tt.calibrate
"""
from __future__ import annotations

import argparse
from pathlib import Path

from .common import RESULTS, languages, read_json, write_json

REF_REPO = "overthelex/tokenizer-fertility-map"
PASS_MEAN = 0.02
PASS_MAX = 0.08


def load_reference(path: str | None):
    import pandas as pd
    if path:
        return pd.read_csv(path) if path.endswith(".csv") else pd.read_parquet(path)
    from huggingface_hub import HfApi, hf_hub_download
    files = HfApi().list_repo_files(REF_REPO, repo_type="dataset")
    data = [f for f in files if f.endswith((".parquet", ".csv"))]
    if not data:  # zapasowo: automatyczna konwersja
        files = HfApi().list_repo_files(REF_REPO, repo_type="dataset", revision="refs/convert/parquet")
        data = [f for f in files if f.endswith(".parquet")]
        rev = "refs/convert/parquet"
    else:
        rev = None
    frames = []
    for f in data:
        p = hf_hub_download(REF_REPO, f, repo_type="dataset", revision=rev)
        df = pd.read_csv(p) if f.endswith(".csv") else pd.read_parquet(p)
        if {"model", "language", "fertility"} <= set(df.columns):
            frames.append(df)
    if not frames:
        raise RuntimeError(f"Nie znalazłem kolumn model/language/fertility w {REF_REPO}: {data}")
    return pd.concat(frames, ignore_index=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reference", help="lokalny plik csv/parquet zamiast pobierania (testy)")
    args = ap.parse_args(argv)

    ref = load_reference(args.reference)
    if "source" in ref.columns:
        sib = ref[ref["source"].astype(str).str.contains("SIB", case=False, na=False)]
        ref = sib if len(sib) else ref
    name_to_code = {lang["name_en"]: lang["code"] for lang in languages()}

    rows, per_tok = [], {}
    for path in sorted((RESULTS / "local").glob("*.json")):
        res = read_json(path)
        name = res.get("calibration")
        if not name:
            continue
        sub = ref[ref["model"] == name]
        if sub.empty:
            print(f"! {res['id']}: brak „{name}” w danych autora")
            continue
        diffs = []
        for _, r in sub.iterrows():
            code = name_to_code.get(str(r["language"]))
            if not code or r["fertility"] != r["fertility"]:
                continue
            ours = res["languages"][code]["fertility"]
            d = ours - float(r["fertility"])
            diffs.append(abs(d))
            rows.append({"tokenizer": res["id"], "model_ref": name, "language": code, "ours": round(ours, 4),
                         "ref": float(r["fertility"]), "diff": round(d, 4)})
        if diffs:
            per_tok[res["id"]] = {"n": len(diffs), "mean_abs": sum(diffs) / len(diffs), "max_abs": max(diffs)}
    if not rows:
        print("Brak danych do kalibracji — najpierw python -m tt.measure_local")
        return 1
    all_abs = [abs(r["diff"]) for r in rows]
    summary = {"n": len(all_abs), "mean_abs": sum(all_abs) / len(all_abs), "max_abs": max(all_abs),
               "pass_mean": PASS_MEAN, "pass_max": PASS_MAX, "per_tokenizer": per_tok}
    summary["passed"] = summary["mean_abs"] <= PASS_MEAN and summary["max_abs"] <= PASS_MAX
    write_json(RESULTS / "calibration.json", {"summary": summary, "rows": rows})
    print(f"Kalibracja: {summary['n']} par, średnia |różnica| {summary['mean_abs']:.4f}, maks. {summary['max_abs']:.4f} "
          f"→ {'ZALICZONA' if summary['passed'] else 'NIEZALICZONA'} (progi {PASS_MEAN} / {PASS_MAX})")
    for k, v in per_tok.items():
        print(f"  {k}: n={v['n']} średnia {v['mean_abs']:.4f} maks. {v['max_abs']:.4f}")
    return 0 if summary["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
