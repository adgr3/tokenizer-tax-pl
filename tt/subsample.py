"""Krok 4: ile bloków na język wystarczy przy pomiarze przez API (żeby nie płacić za wszystkie).

Na tokenizerach policzonych lokalnie porównuje wynik z k bloków (rozłożonych równomiernie) z wynikiem ze
wszystkich bloków. Wybiera najmniejsze k, przy którym błąd jest pomijalny.

    python -m tt.subsample
"""
from __future__ import annotations

from .common import RESULTS, read_json, select_blocks, write_json

MAX_ABS = 0.03    # maks. |różnica| tokenów na słowo, dowolny tokenizer i język
MEAN_ABS = 0.01   # średnia |różnica|


def main() -> int:
    results = [read_json(p) for p in sorted((RESULTS / "local").glob("*.json"))]
    if not results:
        print("Brak wyników lokalnych — najpierw python -m tt.measure_local")
        return 1
    n_min = min(len(lang["blocks"]) for r in results for lang in r["languages"].values())
    table = []
    for k in range(1, n_min + 1):
        errs = []
        for r in results:
            for lang in r["languages"].values():
                bl = lang["blocks"]
                idx = select_blocks(len(bl), k)
                sub = sum(bl[i]["tokens"] / bl[i]["words"] for i in idx) / len(idx)
                errs.append(abs(sub - lang["fertility"]))
        table.append({"k": k, "mean_abs": sum(errs) / len(errs), "max_abs": max(errs), "n": len(errs)})
        print(f"k={k}: średnia {table[-1]['mean_abs']:.4f}, maks. {table[-1]['max_abs']:.4f}")
    good = [t for t in table if t["max_abs"] <= MAX_ABS and t["mean_abs"] <= MEAN_ABS]
    k_api = good[0]["k"] if good else n_min
    k1 = table[0]
    plan = {"k_aihubmix": k_api, "k_openrouter": 1, "thresholds": {"max_abs": MAX_ABS, "mean_abs": MEAN_ABS},
            "error_k1": k1, "table": table, "n_tokenizers": len(results)}
    write_json(RESULTS / "subsample.json", plan)
    print(f"\nAIHubMix: {k_api} bloków na język. OpenRouter (limit dzienny): 1 blok, błąd średnio "
          f"{k1['mean_abs']:.4f}, maks. {k1['max_abs']:.4f} — oznaczony w raporcie jako mniej dokładny.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
