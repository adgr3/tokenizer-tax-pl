"""Krok 2: pomiar lokalny — tokeny na słowo dla każdego tokenizera z config/tokenizers.yaml.

    python -m tt.measure_local                 # wszystkie (pomija już policzone)
    python -m tt.measure_local --only qwen3 slayer1b --force
    python -m tt.measure_local --config tokenizers_test.yaml   # inna lista (np. testy)
"""
from __future__ import annotations

import argparse
import time
from datetime import datetime, timezone

from .backends import load_tokenizer
from .common import RESULTS, load_yaml, read_json, sib_blocks, words_of, write_json, fertility_stats


def measure(spec: dict, blocks: dict[str, list[str]]) -> dict:
    tok, used = load_tokenizer(spec)
    t0 = time.time()
    langs = {}
    for code, bl in blocks.items():
        rows = [{"chars": len(b), "bytes": len(b.encode("utf-8")), "words": words_of(b), "tokens": tok.count(b)} for b in bl]
        langs[code] = {"blocks": rows, **fertility_stats(rows)}
    return {
        "id": spec["id"], "label": spec["label"], "method": "local", "kind": spec["kind"], "repo_used": used,
        "group": spec.get("group"), "origin": spec.get("origin"), "polish_model": bool(spec.get("polish_model")),
        "bench_ref": bool(spec.get("bench_ref")), "calibration": spec.get("calibration"),
        "vocab_size": tok.vocab_size, "fingerprint": tok.fingerprint, "meta": tok.meta,
        "seconds": round(time.time() - t0, 1), "measured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "languages": langs,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="tokenizers.yaml")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)

    specs = load_yaml(args.config)["tokenizers"]
    if args.only:
        specs = [s for s in specs if s["id"] in args.only]
    blocks = sib_blocks()
    out_dir = RESULTS / "local"
    skipped_path = RESULTS / "skipped.json"
    skipped = read_json(skipped_path) if skipped_path.exists() else {}
    ok = 0
    for spec in specs:
        target = out_dir / f"{spec['id']}.json"
        if target.exists() and not args.force:
            print(f"= {spec['id']}: już policzony")
            ok += 1
            continue
        try:
            res = measure(spec, blocks)
        except Exception as exc:  # noqa: BLE001
            skipped[spec["id"]] = {"label": spec["label"], "repo": spec["repo"], "reason": str(exc)[:600]}
            write_json(skipped_path, skipped)
            print(f"! {spec['id']}: POMINIĘTY — {str(exc)[:200]}")
            continue
        skipped.pop(spec["id"], None)
        write_json(skipped_path, skipped)
        write_json(target, res)
        ok += 1
        pl = res["languages"].get("pol_Latn", {}).get("fertility")
        en = res["languages"].get("eng_Latn", {}).get("fertility")
        print(f"+ {spec['id']}: słownik {res['vocab_size']}, EN {en:.3f}, PL {pl:.3f}, {res['seconds']} s, z {res['repo_used']}")
    print(f"\nGotowe: {ok}/{len(specs)}; pominięte: {len(skipped)} (results/skipped.json)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
