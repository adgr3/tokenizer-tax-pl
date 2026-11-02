"""Praca domowa 2: pre-tokenizacja — co robią regexy tokenizerów i po co.

    python -m tt.pretok selftest   # regexy GPT-2/GPT-4/GPT-4o z tiktoken vs podziały sprawdzone innym silnikiem (Node)
    python -m tt.pretok catalog    # jaki pre-tokenizer ma każdy tokenizer + sondy cech (tabela porównawcza)
    python -m tt.pretok stats      # SIB-200: kawałki na słowo, odsetek kawałków = 1 token (25 języków)
    python -m tt.pretok demo       # kolorowy podział przykładów: charts/regex_demo.html + results/regex/demo.md
    python -m tt.pretok bench      # Bench Team: litera odpowiedzi (zadanie A6) i liczby
    python -m tt.pretok nergal     # NERGAL: dane osobowe w tokenach + reguły scrub_pii.py (kod NIE jest uruchamiany)
    python -m tt.pretok all        # wszystko po kolei

Kawałek (pre-token) = fragment tekstu po podziale regexem/pre-tokenizerem; BPE skleja tokeny tylko wewnątrz kawałka.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import html
import json
import re

from .backends import load_tokenizer
from .common import CHARTS, RESULTS, ROOT, load_yaml, read_json, sib_blocks, words_of, write_json

OUT = RESULTS / "regex"
LETTER = re.compile(r"[^\W\d_]", re.UNICODE)


# ------------------------------------------------------------------ pomocnicze

def _bytes_to_unicode() -> dict[int, str]:
    bs = list(range(ord("!"), ord("~") + 1)) + list(range(ord("¡"), ord("¬") + 1)) + list(range(ord("®"), ord("ÿ") + 1))
    cs = bs[:]
    n = 0
    for b in range(256):
        if b not in bs:
            bs.append(b)
            cs.append(256 + n)
            n += 1
    return dict(zip(bs, map(chr, cs)))


_BYTE_DEC = {v: k for k, v in _bytes_to_unicode().items()}


def show(s: str) -> str:
    return s.replace("\r", "␍").replace("\n", "⏎").replace("\t", "⇥").replace(" ", "␣").replace("▁", "␣")


def kind_of(piece: str) -> str:
    p = piece.replace("▁", " ").replace("Ġ", " ")
    if not p.strip():
        return "spacje"
    if LETTER.search(p):
        return "słowo"
    if p.strip().isdigit():
        return "cyfry"
    return "interpunkcja"


class Pipe:
    """Jednolity dostęp do: podziału na kawałki, tokenów kawałka i tokenów całego tekstu."""

    def __init__(self, spec: dict, tok):
        self.spec = spec
        self.kind, self.obj = tok.raw or ("none", None)
        self.bytelevel = False
        self.js = None
        self.approx = False
        if self.kind == "tokenizers":
            self.js = json.loads(self.obj.to_str())
            blob = json.dumps({k: self.js.get(k) for k in ("pre_tokenizer", "decoder")})
            self.bytelevel = '"ByteLevel"' in blob
        elif self.kind == "slow":
            self.approx = True

    def _disp(self, s: str) -> str:
        if self.bytelevel:
            try:
                return bytes(_BYTE_DEC[c] for c in s).decode("utf-8", "replace")
            except KeyError:
                return s
        return s.replace("▁", " ")

    def pieces(self, text: str) -> list[str]:
        if self.kind == "tiktoken":
            import regex
            return regex.findall(self.obj._pat_str, text)
        if self.kind == "tokenizers":
            bt = self.obj
            norm = bt.normalizer.normalize_str(text) if bt.normalizer else text
            if bt.pre_tokenizer:
                return [p for p, _ in bt.pre_tokenizer.pre_tokenize_str(norm)]
            # Brak pre-tokenizera (typ SentencePiece: Bielik v3, Gemma…): cały tekst to jeden „kawałek”.
            # Do statystyk dzielimy po znaczniku „▁” (BPE i tak go nie przekracza); zgodność sprawdza mismatch_blocks.
            self.approx = "brak pre-tokenizera — podział po ▁"
            return re.findall(r"▁?[^▁]+|▁+", norm)
        return re.findall(r" ?\S+|\s+", text)   # slow / mock: przybliżenie podziałem po spacjach

    def stat_pieces(self, text: str) -> list[str]:
        """Kawałki do statystyk. Gdy pre-tokenizer istnieje, ale nie dzieli tekstu na słowa (Metaspace split=False:
        Bielik v3, Llama 2; Gemma: Split(" ") po zamianie spacji na ▁; ByteLevel bez regexu), cały blok byłby jednym
        „słowem” — wtedy dzielimy po znaczniku spacji (▁ albo Ġ), jak przy braku pre-tokenizera."""
        pcs = self.pieces(text)
        if self.kind != "tokenizers" or not self.obj.pre_tokenizer:
            return pcs
        if not hasattr(self, "_nosplit"):
            bt = self.obj
            probe = bt.normalizer.normalize_str("ab cd ef") if bt.normalizer else "ab cd ef"
            self._nosplit = len(bt.pre_tokenizer.pre_tokenize_str(probe)) == 1
        if not self._nosplit:
            return pcs
        m = "Ġ" if self.bytelevel else "▁"
        self.approx = f"pre-tokenizer nie dzieli słów — podział po {m}"
        return [x for p in pcs for x in re.findall(f"{m}?[^{m}]+|{m}+", p)]

    def piece_tokens(self, piece: str) -> list[str]:
        if self.kind == "tiktoken":
            return [self.obj.decode_single_token_bytes(i).decode("utf-8", "replace") for i in self.obj.encode_ordinary(piece)]
        if self.kind == "tokenizers":
            return [self._disp(t.value) for t in self.obj.model.tokenize(piece)]
        if self.kind == "slow":
            return [self._disp(t) for t in self.obj.tokenize(piece)]
        if self.kind == "mock":
            n = max(1, int(self.obj))
            w = piece
            return [w[i:i + n] for i in range(0, len(w), n)] or [w]
        return [piece]

    def encode(self, text: str) -> tuple[list[int], list[str]]:
        if self.kind == "tiktoken":
            ids = self.obj.encode_ordinary(text)
            return ids, [self.obj.decode_single_token_bytes(i).decode("utf-8", "replace") for i in ids]
        if self.kind == "tokenizers":
            e = self.obj.encode(text, add_special_tokens=False)
            return list(e.ids), [self._disp(t) for t in e.tokens]
        if self.kind == "slow":
            ids = self.obj.encode(text, add_special_tokens=False)
            return ids, [self._disp(t) for t in self.obj.convert_ids_to_tokens(ids)]
        toks = [t for p in self.pieces(text) for t in self.piece_tokens(p)]
        return [hash(t) % 99991 for t in toks], toks

    def split_display(self, text: str) -> tuple[str, int]:
        """„kawałek │ kawałek”, w środku kawałka tokeny rozdzielone „·”; zwraca też liczbę tokenów."""
        parts, n = [], 0
        for p in self.pieces(text):
            toks = self.piece_tokens(p)
            n += len(toks)
            parts.append("·".join(show(t) for t in toks))
        return " │ ".join(parts), n

    def describe(self) -> dict:
        if self.kind == "tiktoken":
            return {"pre_tokenizer": "regex (tiktoken)", "regexes": [self.obj._pat_str], "normalizer": None, "model": "BPE (bajty)"}
        if self.kind == "tokenizers":
            regexes, kinds = [], []

            def walk(node):
                if not node:
                    return
                t = node.get("type")
                if t == "Sequence":
                    for x in node.get("pretokenizers", node.get("normalizers", [])):
                        walk(x)
                    return
                if t == "Split":
                    pat = node.get("pattern", {})
                    regexes.append(pat.get("Regex") or pat.get("String"))
                    kinds.append("Split(regex)")
                elif t == "ByteLevel":
                    kinds.append("ByteLevel" + ("+regex GPT-2" if node.get("use_regex", True) else ""))
                    if node.get("use_regex", True):
                        regexes.append("<wbudowany regex GPT-2 (ByteLevel use_regex)>")
                elif t == "Metaspace":
                    kinds.append(f"Metaspace(prepend={node.get('prepend_scheme', node.get('add_prefix_space'))}, split={node.get('split', True)})")
                elif t == "Digits":
                    kinds.append(f"Digits(individual={node.get('individual_digits')})")
                else:
                    kinds.append(t)
            walk(self.js.get("pre_tokenizer"))
            norm = self.js.get("normalizer")
            nkinds = []
            if norm:
                for x in (norm.get("normalizers") or [norm]):
                    nkinds.append(x.get("type") + (f"({x.get('pattern', {}).get('String', '')!r}→{x.get('content', '')!r})" if x.get("type") == "Replace" else ""))
            model = self.js.get("model", {})
            return {"pre_tokenizer": " + ".join(kinds) if kinds else "brak (cały tekst do modelu; SentencePiece)",
                    "regexes": regexes, "normalizer": ", ".join(nkinds) or None,
                    "model": model.get("type") + (" + byte_fallback" if model.get("byte_fallback") else "")}
        if self.kind == "slow":
            return {"pre_tokenizer": f"wolny tokenizer ({type(self.obj).__name__}) — przybliżenie", "regexes": [], "normalizer": None, "model": "?"}
        return {"pre_tokenizer": f"atrapa ({self.kind})", "regexes": [], "normalizer": None, "model": "mock"}


def extra_specs() -> list[dict]:
    """Tokenizery spoza pracy 1 (np. Aster-0.5B) — z config/regex_examples.yaml, bez zmiany tokenizers.yaml."""
    return list(load_yaml("regex_examples.yaml").get("extra_tokenizers") or [])


def extra_ids(flag: str | None = None) -> list[str]:
    return [s["id"] for s in extra_specs() if flag is None or s.get(flag)]


def available(i: str) -> bool:
    return (RESULTS / "local" / f"{i}.json").exists() or i in extra_ids()


def specs_by_id(config: str) -> dict:
    specs = {s["id"]: s for s in load_yaml(config)["tokenizers"]}
    for s in extra_specs():
        specs.setdefault(s["id"], s)
    return specs


def measured_ids(unique_only: bool) -> list[str]:
    """Tokenizery policzone w pracy 1 (results/local); unique_only = bez powtórzeń tego samego tokenizera."""
    res = sorted((read_json(p) for p in (RESULTS / "local").glob("*.json")), key=lambda r: r["id"])
    out, seen = [], set()
    for r in res:
        if unique_only and r["fingerprint"] in seen and not (r.get("polish_model") or r.get("group") == "encoder"):
            continue
        seen.add(r["fingerprint"])
        out.append(r["id"])
    return out + [i for i in extra_ids() if i not in out]


def open_pipes(ids: list[str], config: str) -> dict[str, Pipe]:
    specs = specs_by_id(config)
    pipes = {}
    for i in ids:
        if i not in specs:
            continue
        try:
            tok, _ = load_tokenizer(specs[i])
            pipes[i] = Pipe(specs[i], tok)
        except Exception as exc:  # noqa: BLE001
            print(f"! {i}: {str(exc)[:160]}")
    return pipes


def write_csv(path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    cols = list(dict.fromkeys(k for r in rows for k in r))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


# ------------------------------------------------------------------ kroki

def selftest(_args) -> int:
    """Czy regexy z tiktoken dają w Pythonie (moduł regex) te same podziały, co sprawdzone w Node."""
    import regex
    import tiktoken
    expected = json.loads((ROOT / "tests" / "rx_expected.json").read_text(encoding="utf-8"))
    encs = {"gpt2": "gpt2", "cl100k": "cl100k_base", "o200k": "o200k_base"}
    bad = 0
    for text, by in expected.items():
        for name, enc_name in encs.items():
            got = regex.findall(tiktoken.get_encoding(enc_name)._pat_str, text)
            if got != by[name]:
                bad += 1
                print(f"! {name} na {text[:40]!r}:\n   oczekiwane {by[name]}\n   jest       {got}")
    graphic = load_yaml("regex_examples.yaml").get("graphic_o200k")
    if graphic:
        same = re.sub(r"\s", "", graphic) == re.sub(r"\s", "", tiktoken.get_encoding("o200k_base")._pat_str)
        print(f"Regex z grafiki = o200k_base z tiktoken: {'TAK' if same else 'NIE (różni się zapisem — sprawdź)'}")
    print("SELFTEST OK" if not bad else f"SELFTEST: {bad} różnic")
    return 0 if not bad else 2


def catalog(args) -> int:
    probes = load_yaml("regex_examples.yaml")["probes"]
    ids = measured_ids(unique_only=False)
    pipes = open_pipes(ids, args.config)
    known = {}
    try:
        import tiktoken
        for name, enc in (("GPT-2", "gpt2"), ("GPT-4 (cl100k)", "cl100k_base"), ("GPT-4o (o200k)", "o200k_base")):
            known[tiktoken.get_encoding(enc)._pat_str] = name
    except Exception:  # noqa: BLE001
        pass
    rows, groups = [], {}
    for i, p in pipes.items():
        d = p.describe()
        key = hashlib.sha256(json.dumps([d["pre_tokenizer"], d["regexes"]]).encode()).hexdigest()[:10]
        family = next((known[r] for r in d["regexes"] if r in known), None)
        if not family and any("ByteLevel use_regex" in r for r in d["regexes"]) and len(d["regexes"]) == 1:
            family = "GPT-2 (wbudowany)"
        groups.setdefault(key, []).append(p.spec["label"])
        row = {"tokenizer": i, "label": p.spec["label"], "group": p.spec.get("group"), "pre_tokenizer": d["pre_tokenizer"],
               "regex_family": family, "regex_group": key, "normalizer": d["normalizer"], "model": d["model"],
               "regexes": " ||| ".join(r for r in d["regexes"] if r), "approx": p.approx}
        for name, text in probes.items():
            row[f"probe_{name}"], row[f"ntok_{name}"] = p.split_display(text)
        rows.append(row)
    for r in rows:
        if not r["regex_family"]:
            members = groups[r["regex_group"]]
            r["regex_family"] = "własny" if len(members) == 1 else f"wspólny: {', '.join(members[:3])}{'…' if len(members) > 3 else ''}"
    write_csv(OUT / "catalog.csv", rows)
    write_json(OUT / "catalog.json", rows)
    print(f"Katalog: {len(rows)} tokenizerów, {len(groups)} różnych pre-tokenizerów → {OUT / 'catalog.csv'}")
    return 0


def stats(args) -> int:
    blocks = sib_blocks()
    langs = args.langs or list(blocks)
    pipes = open_pipes(measured_ids(unique_only=True), args.config)
    rows = []
    for i, p in pipes.items():
        for code in langs:
            agg = {"words": 0, "pieces": 0, "tokens": 0, "word_pieces": 0, "word_single": 0, "digit_pieces": 0,
                   "punct_pieces": 0, "space_pieces": 0, "tokens_in_words": 0, "mismatch_blocks": 0}
            for b in blocks[code]:
                pcs = p.stat_pieces(b)
                agg["words"] += words_of(b)
                total = 0
                for pc in pcs:
                    n = len(p.piece_tokens(pc))
                    total += n
                    k = kind_of(p._disp(pc))
                    agg["pieces"] += 1
                    if k == "słowo":
                        agg["word_pieces"] += 1
                        agg["word_single"] += n == 1
                        agg["tokens_in_words"] += n
                    elif k == "cyfry":
                        agg["digit_pieces"] += 1
                    elif k == "interpunkcja":
                        agg["punct_pieces"] += 1
                    else:
                        agg["space_pieces"] += 1
                agg["tokens"] += total
                if p.kind in ("tokenizers", "tiktoken") and total != len(p.encode(b)[0]):
                    agg["mismatch_blocks"] += 1
            rows.append({"tokenizer": i, "label": p.spec["label"], "group": p.spec.get("group"), "language": code,
                         **agg, "pieces_per_word": agg["pieces"] / agg["words"],
                         "tokens_per_piece": agg["tokens"] / agg["pieces"],
                         "single_token_word_share": agg["word_single"] / max(1, agg["word_pieces"]),
                         "tokens_per_word_piece": agg["tokens_in_words"] / max(1, agg["word_pieces"]),
                         "approx": p.approx})
        pl = next((r for r in rows if r["tokenizer"] == i and r["language"] == "pol_Latn"), None)
        en = next((r for r in rows if r["tokenizer"] == i and r["language"] == "eng_Latn"), None)
        if pl and en:
            print(f"+ {i}: słowo = 1 token — EN {en['single_token_word_share']:.0%}, PL {pl['single_token_word_share']:.0%}"
                  + (f"  ! niezgodność z pełnym kodowaniem w {pl['mismatch_blocks'] + en['mismatch_blocks']} blokach" if pl["mismatch_blocks"] + en["mismatch_blocks"] else ""))
    write_csv(OUT / "stats_long.csv", rows)
    return 0


def demo(args) -> int:
    ex = load_yaml("regex_examples.yaml")
    ids = [i for i in ex["demo_tokenizers"] if available(i)] or measured_ids(True)[:8]
    pipes = open_pipes(ids, args.config)
    md, blocks_html = [], []
    palette = ["#FDE2B8", "#CDE7F7"]
    for text in ex["demo"]:
        md.append(f"**Tekst:** `{show(text)}`\n\n```")
        rows_html = []
        for i, p in pipes.items():
            disp, n = p.split_display(text)
            md.append(f"{p.spec['label'][:22]:<22} ({n:>2} tok.)  {disp}")
            spans = []
            for k, pc in enumerate(p.pieces(text)):
                toks = p.piece_tokens(pc)
                inner = "".join(f'<span class="t">{html.escape(show(t))}</span>' for t in toks)
                spans.append(f'<span class="p" style="background:{palette[k % 2]}">{inner}</span>')
            rows_html.append(f'<tr><th>{html.escape(p.spec["label"])}<br><small>{n} tokenów</small></th><td>{"".join(spans)}</td></tr>')
        md.append("```\n")
        blocks_html.append(f'<h2>{html.escape(show(text))}</h2><table>{"".join(rows_html)}</table>')
    (OUT).mkdir(parents=True, exist_ok=True)
    legend = "Kawałek (pre-token) = kolorowe pole; tokeny wewnątrz kawałka oddzielone pionową kreską. ␣ spacja, ⏎ nowa linia."
    (OUT / "demo.md").write_text(legend + "\n\n" + "\n".join(md), encoding="utf-8")
    CHARTS.mkdir(parents=True, exist_ok=True)
    (CHARTS / "regex_demo.html").write_text(f"""<!doctype html><html lang="pl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Pre-tokenizacja: demo</title>
<style>body{{font:14px/1.5 system-ui,sans-serif;margin:16px;color:#222;background:#fff}}
table{{border-collapse:collapse;margin-bottom:24px}}th{{text-align:left;padding:6px 10px;vertical-align:top;white-space:nowrap;font-weight:600}}
td{{padding:6px 4px;font-family:ui-monospace,Consolas,monospace}}.p{{display:inline-block;margin:1px;border-radius:4px;padding:1px 0}}
.t{{display:inline-block;padding:0 3px;border-left:1px solid rgba(0,0,0,.35)}}.t:first-child{{border-left:none}}
h2{{font-family:ui-monospace,Consolas,monospace;font-size:14px;background:#f3f3f3;padding:6px}}small{{color:#666;font-weight:400}}</style>
</head><body><h1>Jak tokenizery tną ten sam tekst</h1><p>{legend}</p>{"".join(blocks_html)}</body></html>""", encoding="utf-8")
    print(f"Demo: {CHARTS / 'regex_demo.html'}, {OUT / 'demo.md'}")
    return 0


def bench(args) -> int:
    ex = load_yaml("regex_examples.yaml")
    ids = [r["id"] for r in (read_json(p) for p in (RESULTS / "local").glob("*.json")) if r.get("bench_ref")]
    ids += [i for i in extra_ids("bench_ref") if i not in ids]
    pipes = open_pipes(sorted(ids), args.config)
    ans, nums = [], []
    for i, p in pipes.items():
        for case in ex["bench_answer"]:
            ctx, cont = case["context"], case["continuation"]
            whole_ids, whole_toks = p.encode(ctx + cont)
            ctx_ids, _ = p.encode(ctx)
            cont_ids, cont_toks = p.encode(cont)
            prefix_ok = whole_ids[:len(ctx_ids)] == ctx_ids
            cont_in_whole = whole_toks[len(ctx_ids):] if prefix_ok else None
            ans.append({"tokenizer": i, "label": p.spec["label"], "context": show(ctx), "continuation": show(cont),
                        "whole_tokens": " · ".join(show(t) for t in whole_toks),
                        "continuation_alone": " · ".join(show(t) for t in cont_toks), "continuation_n": len(cont_ids),
                        "context_is_prefix": prefix_ok,
                        "continuation_in_context": " · ".join(show(t) for t in cont_in_whole) if cont_in_whole is not None else "—",
                        "same_as_alone": prefix_ok and whole_ids[len(ctx_ids):] == cont_ids})
        for num in ex["bench_numbers"]:
            ids_, toks = p.encode(num)
            nums.append({"tokenizer": i, "label": p.spec["label"], "number": num, "n_tokens": len(ids_),
                         "tokens": " · ".join(show(t) for t in toks)})
    write_csv(OUT / "bench_answer.csv", ans)
    write_csv(OUT / "bench_numbers.csv", nums)
    print(f"Bench Team: {len(pipes)} tokenizerów → {OUT / 'bench_answer.csv'}, {OUT / 'bench_numbers.csv'}")
    return 0


def scrub_rules(path) -> list[dict]:
    """Wyciąga wzorce regex z pliku Pythona przez analizę składni (ast) — bez uruchamiania kodu."""
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    names = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    names[id(node.value)] = t.id
    rules = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        fname = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")
        if fname != "compile" or not node.args:
            continue
        arg = node.args[0]
        pattern = arg.value if isinstance(arg, ast.Constant) and isinstance(arg.value, str) else None
        flags = ast.get_source_segment(src, node.args[1]) if len(node.args) > 1 else \
            next((ast.get_source_segment(src, k.value) for k in node.keywords if k.arg == "flags"), "")
        rules.append({"line": node.lineno, "name": names.get(id(node), ""), "pattern": pattern,
                      "dynamic_source": None if pattern is not None else (ast.get_source_segment(src, arg) or "")[:300],
                      "flags": flags or ""})
    return rules


def nergal(args) -> int:
    ex = load_yaml("regex_examples.yaml")
    want = [i for i in ("nergal", "xlm_roberta", "herbert", "polish_roberta", "gpt4o", "bielik_4_5b_v3", "slayer1b",
                        "aster") if available(i)]
    pipes = open_pipes(want, args.config)
    rows = []
    for item in [dict(x, kind="dane osobowe") for x in ex["nergal_pii"]] + [dict(x, kind="pułapka (nie PII)") for x in ex["nergal_decoys"]]:
        for i, p in pipes.items():
            ids_, toks = p.encode(item["text"])
            rows.append({"kind": item["kind"], "category": item["category"], "text": item["text"], "tokenizer": i,
                         "label": p.spec["label"], "n_tokens": len(ids_), "tokens": " · ".join(show(t) for t in toks)})
    write_csv(OUT / "nergal_tokens.csv", rows)

    rules_out = []
    try:
        if args.scrub_file:
            from pathlib import Path
            path = Path(args.scrub_file)
        else:
            from huggingface_hub import hf_hub_download
            from pathlib import Path
            path = Path(hf_hub_download("SlayerLab/NERGAL", "scrub_pii.py"))
        rules = scrub_rules(path)
        try:
            import regex
        except ImportError:   # awaryjnie: moduł re (bez klas \p{…})
            import re as regex
        tests = [dict(x, kind="dane osobowe") for x in ex["nergal_pii"]] + [dict(x, kind="pułapka (nie PII)") for x in ex["nergal_decoys"]]
        for r in rules:
            hits_pii, hits_decoy, err = [], [], ""
            if r["pattern"] is not None:
                fl = 0
                for name, val in (("IGNORECASE", regex.I), (".I", regex.I), ("MULTILINE", regex.M), ("VERBOSE", regex.X),
                                  (".X", regex.X), ("ASCII", regex.A), ("DOTALL", regex.S)):
                    if name in r["flags"]:
                        fl |= val
                try:
                    cre = regex.compile(r["pattern"], fl)
                    for t in tests:
                        m = cre.search(t["text"])
                        if m and m.group(0).strip():
                            (hits_pii if t["kind"] == "dane osobowe" else hits_decoy).append(f"{t['category']}: {m.group(0)}")
                except Exception as exc:  # noqa: BLE001
                    err = str(exc)[:120]
            rules_out.append({**r, "hits_pii": " | ".join(hits_pii), "hits_decoys": " | ".join(hits_decoy), "compile_error": err})
        print(f"scrub_pii.py: {len(rules)} wzorców (stałe: {sum(1 for r in rules if r['pattern'])}, "
              f"budowane dynamicznie: {sum(1 for r in rules if r['pattern'] is None)})")
    except Exception as exc:  # noqa: BLE001
        print(f"! analiza scrub_pii.py pominięta: {exc}")
    write_csv(OUT / "nergal_rules.csv", rules_out)
    write_json(OUT / "nergal_rules.json", rules_out)
    print(f"NERGAL: {OUT / 'nergal_tokens.csv'}, {OUT / 'nergal_rules.csv'}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["selftest", "catalog", "stats", "demo", "bench", "nergal", "all"])
    ap.add_argument("--config", default="tokenizers.yaml")
    ap.add_argument("--langs", nargs="*", help="kody języków dla stats (domyślnie wszystkie 25)")
    ap.add_argument("--scrub-file", help="lokalny scrub_pii.py zamiast pobierania (testy)")
    args = ap.parse_args(argv)
    steps = {"selftest": selftest, "catalog": catalog, "stats": stats, "demo": demo, "bench": bench, "nergal": nergal}
    if args.step == "all":
        rc = 0
        for name in ("selftest", "catalog", "stats", "demo", "bench", "nergal"):
            print(f"\n=== {name} ===")
            rc |= steps[name](args)
        return rc
    return steps[args.step](args)


if __name__ == "__main__":
    raise SystemExit(main())
