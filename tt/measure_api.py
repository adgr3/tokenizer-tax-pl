"""Krok 5b: pomiar przez API — liczba tokenów wejścia zwrócona przez dostawcę (pole usage.prompt_tokens).

Modele z config/api_models.yaml. Dla każdego: zapytanie bazowe „x” (narzut szablonu czatu), potem k bloków na
język (z results/subsample.json). max_tokens=1, temperature=0. Wyniki per zapytanie w results/api/*.jsonl
(wznawianie), podsumowanie w results/apisum/<id>.json w tym samym formacie co pomiar lokalny.

Zabezpieczenia:
  * model z ceną wejścia > 0,20 USD/1 mln tokenów → odmowa (reguła budżetu);
  * łączny limit wydatków AIHubMix: zmienna AIHUBMIX_MAX_SPEND_USD (domyślnie 1.00); przed każdym modelem
    szacunek kosztu, po każdym zapytaniu koszt z usage; przekroczenie → stop;
  * OpenRouter: tylko modele darmowe; odstęp między zapytaniami i dzienny limit zapytań
    (OPENROUTER_DAILY_LIMIT, domyślnie 50 — taki jest limit darmowych modeli dla kont bez doładowania).

    python -m tt.measure_api                       # wszystkie z api_models.yaml
    python -m tt.measure_api --only gemini_flash_lite --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import time
from datetime import date, datetime, timezone

import requests

from .common import ROOT, RESULTS, fertility_stats, load_yaml, read_json, read_jsonl, safe_name, select_blocks, sib_blocks, words_of, write_json

PROVIDERS = {
    "aihubmix": {"base": os.environ.get("AIHUBMIX_BASE_URL", "https://aihubmix.com/v1"), "key": "AIHUBMIX_API_KEY", "sleep": 0.4},
    "openrouter": {"base": os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"), "key": "OPENROUTER_API_KEY", "sleep": 3.5},
}
MAX_INPUT_USD_PER_M = 0.20
SPEND_FILE = RESULTS / "api" / "spend.json"


def load_env() -> None:
    path = ROOT / ".env"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def spend() -> dict:
    return read_json(SPEND_FILE) if SPEND_FILE.exists() else {"aihubmix_usd": 0.0, "openrouter_requests": {}}


def call(provider: str, model: str, text: str, session: requests.Session) -> dict:
    cfg = PROVIDERS[provider]
    headers = {"Authorization": f"Bearer {os.environ[cfg['key']]}", "Content-Type": "application/json"}
    if provider == "openrouter":
        headers["X-Title"] = "tokenizer-tax-pl"
    last = None
    for max_tokens in (1, 16, 64):
        body = {"model": model, "messages": [{"role": "user", "content": text}], "max_tokens": max_tokens, "temperature": 0}
        for attempt in range(4):
            r = session.post(f"{cfg['base']}/chat/completions", headers=headers, data=json.dumps(body), timeout=180)
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(10 * (attempt + 1))
                continue
            break
        last = r
        if r.status_code == 200:
            data = r.json()
            usage = data.get("usage") or {}
            if usage.get("prompt_tokens") is None:
                raise RuntimeError(f"brak usage.prompt_tokens w odpowiedzi: {str(data)[:300]}")
            return {"prompt_tokens": int(usage["prompt_tokens"]),
                    "completion_tokens": int(usage.get("completion_tokens") or 0),
                    "cached_tokens": (usage.get("prompt_tokens_details") or {}).get("cached_tokens"),
                    "cost_reported": usage.get("cost"), "max_tokens": max_tokens}
        if r.status_code == 400 and "token" in r.text.lower():
            continue  # spróbuj większego max_tokens (niektóre modele wymagają minimum)
        break
    raise RuntimeError(f"HTTP {last.status_code}: {last.text[:300]}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--dry-run", action="store_true", help="tylko szacunek kosztu, bez zapytań")
    args = ap.parse_args(argv)
    load_env()

    models = load_yaml("api_models.yaml").get("models", [])
    if args.only:
        models = [m for m in models if m["id"] in args.only]
    plan = read_json(RESULTS / "subsample.json") if (RESULTS / "subsample.json").exists() else {"k_aihubmix": 3, "k_openrouter": 1}
    blocks = sib_blocks()
    cap = float(os.environ.get("AIHUBMIX_MAX_SPEND_USD", "1.00"))
    daily = int(os.environ.get("OPENROUTER_DAILY_LIMIT", "50"))
    session = requests.Session()
    sp = spend()
    today = date.today().isoformat()

    for m in models:
        prov, mid = m["provider"], m["model"]
        price = float(m.get("input_usd_per_m") or 0)
        if prov == "aihubmix" and price > MAX_INPUT_USD_PER_M:
            print(f"! {m['id']}: cena wejścia {price} > {MAX_INPUT_USD_PER_M} USD/1M — pomijam (reguła budżetu)")
            continue
        if prov == "openrouter" and price > 0:
            print(f"! {m['id']}: OpenRouter tylko darmowe — pomijam")
            continue
        k = plan["k_aihubmix"] if prov == "aihubmix" else plan["k_openrouter"]
        todo = [("__baseline__", 0, "x")]
        for code, bl in blocks.items():
            for i in select_blocks(len(bl), k):
                todo.append((code, i, bl[i]))
        log = RESULTS / "api" / f"{prov}__{safe_name(mid)}.jsonl"
        done = {(r["lang"], r["block"]) for r in read_jsonl(log) if "prompt_tokens" in r}
        todo = [t for t in todo if (t[0], t[1]) not in done]
        est_tokens = sum(len(t[2]) for t in todo) / 2.0          # ostrożnie: ok. 2 znaki na token
        est_cost = est_tokens * price / 1e6
        print(f"\n== {m['id']} ({prov}:{mid}) — do wysłania {len(todo)} zapytań, szac. koszt {est_cost:.4f} USD")
        if args.dry_run:
            continue
        if prov == "aihubmix" and sp["aihubmix_usd"] + est_cost > cap:
            print(f"! limit wydatków: wydano {sp['aihubmix_usd']:.4f} + szac. {est_cost:.4f} > {cap} USD — pomijam")
            continue
        if prov == "openrouter":
            used = sp["openrouter_requests"].get(today, 0)
            if used + len(todo) > daily:
                print(f"! dzienny limit OpenRouter: dziś {used}/{daily}, model potrzebuje {len(todo)} — dokończ jutro")
                continue
        log.parent.mkdir(parents=True, exist_ok=True)
        failed = False
        for lang, i, text in todo:
            try:
                res = call(prov, mid, text, session)
            except Exception as exc:  # noqa: BLE001
                print(f"  ! {lang}/{i}: {exc}")
                with open(log, "a", encoding="utf-8") as f:
                    f.write(json.dumps({"lang": lang, "block": i, "error": str(exc)[:500]}, ensure_ascii=False) + "\n")
                failed = True
                break
            row = {"lang": lang, "block": i, "chars": len(text), "bytes": len(text.encode("utf-8")),
                   "words": words_of(text), **res, "at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
            with open(log, "a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            if prov == "aihubmix":
                sp["aihubmix_usd"] += res["prompt_tokens"] * price / 1e6 + res["completion_tokens"] * float(m.get("output_usd_per_m") or 0) / 1e6
            else:
                sp["openrouter_requests"][today] = sp["openrouter_requests"].get(today, 0) + 1
            write_json(SPEND_FILE, sp)
            time.sleep(PROVIDERS[prov]["sleep"])
        if failed:
            continue
        summarize(m, log, k)
    print(f"\nWydatki AIHubMix łącznie: {sp['aihubmix_usd']:.4f} USD (limit {cap}); "
          f"OpenRouter dziś: {sp['openrouter_requests'].get(today, 0)} zapytań")
    return 0


def summarize(m: dict, log, k: int) -> None:
    rows = [r for r in read_jsonl(log) if "prompt_tokens" in r]
    base = [r for r in rows if r["lang"] == "__baseline__"]
    if not base:
        print(f"  ! {m['id']}: brak zapytania bazowego")
        return
    overhead = base[-1]["prompt_tokens"] - 1   # „x” = 1 token; reszta to szablon czatu
    langs = {}
    for r in rows:
        if r["lang"] == "__baseline__":
            continue
        langs.setdefault(r["lang"], {}).setdefault(r["block"], r)
    out_langs = {}
    for code, by_block in langs.items():
        bl = [{"block": b, "chars": r["chars"], "bytes": r["bytes"], "words": r["words"],
               "tokens": r["prompt_tokens"] - overhead} for b, r in sorted(by_block.items())]
        out_langs[code] = {"blocks": bl, **fertility_stats(bl)}
    res = {"id": m["id"], "label": m["label"], "method": f"api:{m['provider']}", "kind": "api", "repo_used": m["model"],
           "group": "api", "origin": m.get("origin"), "polish_model": False, "bench_ref": False, "calibration": None,
           "vocab_size": None, "fingerprint": None, "overhead_tokens": overhead, "k_blocks": k,
           "input_usd_per_m": m.get("input_usd_per_m"), "note": m.get("note"),
           "measured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "languages": out_langs}
    write_json(RESULTS / "apisum" / f"{m['id']}.json", res)
    pl = out_langs.get("pol_Latn", {}).get("fertility")
    print(f"  + {m['id']}: narzut {overhead} tok., PL {pl:.3f}" if pl else f"  + {m['id']}: zapisany")


if __name__ == "__main__":
    raise SystemExit(main())
