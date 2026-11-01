"""Krok 7 (opcjonalny, ale zalecany): polski na różnych rodzajach tekstu (polish-dynaword).

Pyta: czy ranking tokenizerów dla polskiego zmienia się z rodzajem tekstu (prawo, encyklopedia, literatura,
mowa sejmowa…)? Teksty pobierane strumieniowo i zapisywane tylko lokalnie (data/polish/, nie publikujemy ich).

    python -m tt.polish --sample       # pobierz próbki tekstów według config/polish_sources.yaml
    python -m tt.polish                # policz tokenizery (unikalne LLM + polskie modele + enkodery)
"""
from __future__ import annotations

import argparse
import json

from .backends import load_tokenizer
from .common import DATA, RESULTS, fertility_stats, load_yaml, make_blocks, read_json, words_of, write_json


def sample() -> int:
    cfg = load_yaml("polish_sources.yaml")
    if not cfg.get("sources"):
        print("Uzupełnij config/polish_sources.yaml (sources) po obejrzeniu zbioru.")
        return 1
    from datasets import load_dataset
    want = {s["value"]: s["label"] for s in cfg["sources"]}
    got = {v: [] for v in want}
    size = {v: 0 for v in want}
    # Źródło z polem data_files czytamy z jego własnego pliku (zbiór ma osobny parquet na źródło); reszta ze strumienia całości.
    streams = [(s["data_files"], {s["value"]}) for s in cfg["sources"] if s.get("data_files")]
    rest = {s["value"] for s in cfg["sources"] if not s.get("data_files")}
    if rest:
        streams.append((None, rest))
    for data_files, values in streams:
        ds = load_dataset(cfg["dataset"], data_files=data_files, split=cfg["split"], streaming=True)
        for n, row in enumerate(ds):
            src = row.get(cfg["source_field"])
            if src in values and size[src] < cfg["chars_per_source"]:
                text = str(row.get(cfg["text_field"]) or "")[: cfg["max_chars_per_doc"]]
                if text.strip():
                    got[src].append(text)
                    size[src] += len(text)
            if all(size[v] >= cfg["chars_per_source"] for v in values) or n >= cfg["max_rows_scanned"]:
                break
    out = DATA / "polish"
    out.mkdir(parents=True, exist_ok=True)
    for v, texts in got.items():
        with open(out / f"{v}.jsonl", "w", encoding="utf-8") as f:
            for t in texts:
                f.write(json.dumps({"text": t}, ensure_ascii=False) + "\n")
        print(f"{want[v]}: {len(texts)} dokumentów, {size[v]} znaków")
    return 0


def measure(config: str = "tokenizers.yaml") -> int:
    cfg = load_yaml("polish_sources.yaml")
    regs = {}
    for s in cfg.get("sources", []):
        path = DATA / "polish" / f"{s['value']}.jsonl"
        if not path.exists():
            continue
        lines = []
        for line in path.read_text(encoding="utf-8").splitlines():
            lines += [x for x in json.loads(line)["text"].split("\n") if x.strip()]
        regs[s["value"]] = {"label": s["label"], "blocks": make_blocks(lines)}
    if not regs:
        print("Brak próbek — najpierw python -m tt.polish --sample")
        return 1
    specs = {s["id"]: s for s in load_yaml(config)["tokenizers"]}
    measured = [read_json(p) for p in sorted((RESULTS / "local").glob("*.json"))]
    seen = set()
    for res in measured:
        # jeden pomiar na tokenizer (odcisk), ale polskie modele i enkodery zawsze
        if res["fingerprint"] in seen and not (res.get("polish_model") or res.get("group") == "encoder"):
            continue
        seen.add(res["fingerprint"])
        target = RESULTS / "polish" / f"{res['id']}.json"
        if target.exists():
            continue
        if res["id"] not in specs:
            continue
        tok, _ = load_tokenizer(specs[res["id"]])
        out = {}
        for key, reg in regs.items():
            rows = [{"chars": len(b), "words": words_of(b), "tokens": tok.count(b)} for b in reg["blocks"]]
            out[key] = {"label": reg["label"], **fertility_stats(rows)}
        write_json(target, {"id": res["id"], "label": res["label"], "registers": out})
        print(f"+ {res['id']}: " + ", ".join(f"{v['label']} {v['fertility']:.2f}" for v in out.values()))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", action="store_true")
    ap.add_argument("--config", default="tokenizers.yaml")
    args = ap.parse_args(argv)
    return sample() if args.sample else measure(args.config)


if __name__ == "__main__":
    raise SystemExit(main())
