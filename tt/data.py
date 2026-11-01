"""Krok 1: pobranie SIB-200 (split testowy, 25 języków) i kontrola bloków.

    python -m tt.data
"""
from __future__ import annotations

from .common import BLOCK_CHARS, RESULTS, languages, sib_blocks, download_sib200, words_of, write_json


def main() -> int:
    codes = [lang["code"] for lang in languages()]
    download_sib200(codes)
    blocks = sib_blocks()
    summary = {}
    for code, bl in blocks.items():
        summary[code] = {"blocks": len(bl), "chars": sum(len(b) for b in bl), "words": sum(words_of(b) for b in bl),
                         "min_block_chars": min(len(b) for b in bl), "max_block_chars": max(len(b) for b in bl)}
        print(f"{code}: {len(bl)} bloków, {summary[code]['chars']} znaków, {summary[code]['words']} słów")
    write_json(RESULTS / "data_summary.json", {"block_chars": BLOCK_CHARS, "languages": summary})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
