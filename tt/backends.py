"""Ładowanie tokenizerów: Hugging Face (AutoTokenizer), plik tokenizer.json, tiktoken; plus atrapy do testów.

Pobierany jest wyłącznie tokenizer (kilka–kilkadziesiąt MB), nigdy wagi modelu.
"""
from __future__ import annotations

import hashlib
import json
import zlib

from .common import PROBE_TEXTS

TOKENIZER_FILES = ["tokenizer.json", "tokenizer_config.json", "tokenizer.model", "special_tokens_map.json",
                   "vocab.json", "merges.txt", "vocab.txt", "sentencepiece.bpe.model", "spiece.model",
                   "added_tokens.json", "tiktoken.model", "*.tiktoken", "config.json", "tokenization_*.py", "*_tokenizer.py",
                   "configuration_*.py"]


class Tok:
    def __init__(self, count_fn, vocab_size: int | None, meta: dict):
        self._count = count_fn
        self.vocab_size = vocab_size
        self.meta = meta
        self.fingerprint = self._fingerprint()

    def count(self, text: str) -> int:
        return self._count(text)

    def _fingerprint(self) -> str:
        ids = [self.meta.get("_ids_fn", lambda t: [self.count(t)])(t) for t in PROBE_TEXTS]
        payload = json.dumps([self.vocab_size, ids])
        self.meta.pop("_ids_fn", None)
        return hashlib.sha256(payload.encode()).hexdigest()[:16]


def _hf_revision_sha(repo: str, revision: str | None) -> str | None:
    try:
        from huggingface_hub import HfApi
        return HfApi().model_info(repo, revision=revision).sha
    except Exception:  # noqa: BLE001
        return None


def _load_one(spec: dict, repo: str) -> Tok:
    kind = spec["kind"]
    revision = spec.get("revision")
    if kind == "tiktoken":
        import tiktoken
        enc = tiktoken.get_encoding(repo)
        ids = lambda t: enc.encode(t, disallowed_special=())  # noqa: E731
        return Tok(lambda t: len(ids(t)), enc.n_vocab,
                   {"source": f"tiktoken:{repo}", "revision": getattr(tiktoken, "__version__", None), "_ids_fn": ids})
    if kind == "tokenizer_json":
        from huggingface_hub import hf_hub_download
        from tokenizers import Tokenizer
        path = hf_hub_download(repo, spec.get("file", "tokenizer.json"), revision=revision,
                               repo_type=spec.get("repo_type", "model"))
        if spec.get("row"):
            # Tokenizer zapisany jako wiersz pliku parquet (kolumna tokenizer_json), np. SlayerLab/tokenizers.
            import pandas as pd
            df = pd.read_parquet(path, columns=["source_path", "tokenizer_json"])
            tok = Tokenizer.from_str(df.loc[df["source_path"] == spec["row"], "tokenizer_json"].iloc[0])
        else:
            tok = Tokenizer.from_file(path)
        ids = lambda t: tok.encode(t, add_special_tokens=False).ids  # noqa: E731
        return Tok(lambda t: len(ids(t)), tok.get_vocab_size(with_added_tokens=True),
                   {"source": f"hf:{repo}/{spec.get('file', 'tokenizer.json')}" + (f"#{spec['row']}" if spec.get("row") else ""),
                    "revision": revision or _hf_revision_sha(repo, None), "_ids_fn": ids})
    if kind == "hf":
        from huggingface_hub import snapshot_download
        from transformers import AutoTokenizer
        sub = spec.get("subfolder")
        patterns = [f"{sub}/{p}" for p in TOKENIZER_FILES] if sub else TOKENIZER_FILES
        local = snapshot_download(repo, revision=revision, allow_patterns=patterns, repo_type=spec.get("repo_type", "model"))
        path = f"{local}/{sub}" if sub else local
        tok = AutoTokenizer.from_pretrained(path, trust_remote_code=bool(spec.get("trust_remote_code")))
        try:
            tok.model_max_length = 10 ** 9  # bez ostrzeżeń o długości; liczymy tylko tokeny
        except Exception:  # noqa: BLE001
            pass
        ids = lambda t: tok(t, add_special_tokens=False)["input_ids"]  # noqa: E731
        return Tok(lambda t: len(ids(t)), len(tok),
                   {"source": f"hf:{repo}", "revision": revision or _hf_revision_sha(repo, None),
                    "tokenizer_class": type(tok).__name__, "_ids_fn": ids})
    if kind == "mock":
        # Atrapa do testów bez sieci: tokeny = ceil(liczba_znaków / chars_per_token) w każdym słowie.
        cpt = float(spec.get("chars_per_token", 4))
        def ids(t):
            out = []
            for w in t.split():
                out += [zlib.crc32(w[i:i + int(cpt)].encode()) % 50000 for i in range(0, len(w), max(1, int(cpt)))]
            return out
        return Tok(lambda t: len(ids(t)), 50000 + int(cpt * 1000), {"source": f"mock:{cpt}", "_ids_fn": ids})
    raise ValueError(f"Nieznany rodzaj tokenizera: {kind}")


def load_tokenizer(spec: dict) -> tuple[Tok, str]:
    """Próbuje repo, potem kolejne z listy alt. Zwraca (tokenizer, użyte_repo)."""
    errors = []
    for n, repo in enumerate([spec["repo"], *spec.get("alt", [])]):
        try:
            # przypięta rewizja dotyczy repo głównego; kopie z alt mają inne historie commitów
            return _load_one(spec if n == 0 else {**spec, "revision": None}, repo), repo
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{repo}: {type(exc).__name__}: {str(exc)[:200]}")
    raise RuntimeError(" | ".join(errors))
