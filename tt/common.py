"""Wspólne funkcje: ścieżki, konfiguracja, dane SIB-200, bloki ~6000 znaków, tokeny na słowo."""
from __future__ import annotations

import json
import math
import os
import random
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
# TT_WORKDIR / TT_CONFIG pozwalają uruchomić testy w osobnym katalogu, bez ruszania prawdziwych wyników.
WORK = Path(os.environ.get("TT_WORKDIR", ROOT))
CONFIG = Path(os.environ.get("TT_CONFIG", ROOT / "config"))
DATA = WORK / "data"
RESULTS = WORK / "results"
CHARTS = WORK / "charts"

BLOCK_CHARS = 6000          # jak u autora wykresu i w arXiv 2605.24718
MIN_LAST_BLOCK = 1000       # krótszy ostatni blok doklejamy do poprzedniego
SIB_REPO = "Davlan/sib200"
SIB_SPLIT = "test"
SIB_EXPECTED_ROWS = 204

# Teksty do „odcisku” tokenizera: identyczne ciągi identyfikatorów = ten sam tokenizer (deduplikacja kolumn).
PROBE_TEXTS = [
    "The quick brown fox jumps over the lazy dog. 1234567890",
    "Zażółć gęślą jaźń. Wójt gminy Łomianki ogłasza przetarg nieograniczony.",
    "Příliš žluťoučký kůň úpěl ďábelské ódy. Árvíztűrő tükörfúrógép.",
    "Съешь же ещё этих мягких французских булок. Ξεσκεπάζω την ψυχοφθόρα βδελυγμία.",
    "Il-Malti huwa l-lingwa nazzjonali ta' Malta. Tá an aimsir go maith inniu.",
    "    def f(x):\n        return x ** 2  # komentarz\n",
]


def load_yaml(name: str) -> dict:
    with open(CONFIG / name, encoding="utf-8") as f:
        return yaml.safe_load(f)


def languages() -> list[dict]:
    return load_yaml("languages.yaml")["languages"]


def words_of(text: str) -> int:
    """Słowo = ciąg znaków rozdzielony białymi znakami (jak u autora i w pracy)."""
    return len(text.split())


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def read_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------- SIB-200

def sib_path(code: str) -> Path:
    return DATA / "sib200" / f"{code}.jsonl"


def download_sib200(codes: list[str]) -> None:
    """Pobiera split testowy SIB-200 dla podanych języków do data/sib200/<kod>.jsonl.

    Najpierw automatycznie skonwertowane pliki parquet z gałęzi refs/convert/parquet (bez skryptu ładowania),
    potem zapasowo biblioteka datasets.
    """
    out_dir = DATA / "sib200"
    out_dir.mkdir(parents=True, exist_ok=True)
    for code in codes:
        target = sib_path(code)
        if target.exists():
            continue
        rows = None
        errors = []
        try:
            import pandas as pd
            from huggingface_hub import HfApi, hf_hub_download
            files = [f for f in HfApi().list_repo_files(SIB_REPO, repo_type="dataset", revision="refs/convert/parquet")
                     if f.startswith(f"{code}/") and f"/{SIB_SPLIT}/" in f and f.endswith(".parquet")]
            if not files:
                raise FileNotFoundError(f"brak parquet dla {code}/{SIB_SPLIT}")
            frames = [pd.read_parquet(hf_hub_download(SIB_REPO, f, repo_type="dataset", revision="refs/convert/parquet"))
                      for f in sorted(files)]
            df = pd.concat(frames)
            rows = [{"index_id": int(r["index_id"]), "text": str(r["text"])} for _, r in df.iterrows()]
        except Exception as exc:  # noqa: BLE001
            errors.append(f"parquet: {exc}")
        if rows is None:
            try:
                from datasets import load_dataset
                ds = load_dataset(SIB_REPO, code, split=SIB_SPLIT)
                rows = [{"index_id": int(r["index_id"]), "text": str(r["text"])} for r in ds]
            except Exception as exc:  # noqa: BLE001
                errors.append(f"datasets: {exc}")
        if rows is None:
            raise RuntimeError(f"Nie udało się pobrać SIB-200 {code}: {' | '.join(errors)}")
        rows.sort(key=lambda r: r["index_id"])
        if len(rows) != SIB_EXPECTED_ROWS:
            print(f"  ! {code}: {len(rows)} zdań zamiast {SIB_EXPECTED_ROWS}")
        with open(target, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"  SIB-200 {code}: {len(rows)} zdań")


def make_blocks(sentences: list[str], block_chars: int = BLOCK_CHARS) -> list[str]:
    """Skleja zdania (w kolejności index_id, rozdzielone nową linią) w bloki po ok. block_chars znaków."""
    blocks, cur = [], []
    cur_len = 0
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        add = len(s) + (1 if cur else 0)
        if cur and cur_len + add > block_chars:
            blocks.append("\n".join(cur))
            cur, cur_len = [], 0
            add = len(s)
        cur.append(s)
        cur_len += add
    if cur:
        last = "\n".join(cur)
        if blocks and len(last) < MIN_LAST_BLOCK:
            blocks[-1] = blocks[-1] + "\n" + last
        else:
            blocks.append(last)
    return blocks


def sib_blocks() -> dict[str, list[str]]:
    """Bloki dla wszystkich 25 języków (z data/sib200)."""
    out = {}
    for lang in languages():
        rows = read_jsonl(sib_path(lang["code"]))
        if not rows:
            raise FileNotFoundError(f"Brak danych {sib_path(lang['code'])} — uruchom: python -m tt.data")
        out[lang["code"]] = make_blocks([r["text"] for r in sorted(rows, key=lambda r: r["index_id"])])
    return out


# ---------------------------------------------------------------- statystyka

def fertility_stats(blocks: list[dict]) -> dict:
    """blocks: [{'words': int, 'tokens': int}] → średnia po blokach tokens/words, SE, n."""
    vals = [b["tokens"] / b["words"] for b in blocks if b.get("words") and b.get("tokens") is not None]
    n = len(vals)
    if n == 0:
        return {"fertility": None, "se": None, "n_blocks": 0}
    mean = sum(vals) / n
    se = math.sqrt(sum((v - mean) ** 2 for v in vals) / (n - 1)) / math.sqrt(n) if n > 1 else None
    return {"fertility": mean, "se": se, "n_blocks": n}


def bootstrap_ci(values: list[float], reps: int = 2000, seed: int = 20261101) -> tuple[float, float] | None:
    if len(values) < 2:
        return None
    rng = random.Random(seed)
    n = len(values)
    means = sorted(sum(values[rng.randrange(n)] for _ in range(n)) / n for _ in range(reps))
    return means[int(0.025 * reps)], means[int(0.975 * reps) - 1]


def safe_name(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s).strip("_")


def select_blocks(n: int, k: int) -> list[int]:
    """Indeksy k bloków rozłożonych równomiernie (ten sam wybór w próbce lokalnej i przez API)."""
    if k >= n:
        return list(range(n))
    if k == 1:
        return [n // 2]
    return sorted({round(i * (n - 1) / (k - 1)) for i in range(k)})
