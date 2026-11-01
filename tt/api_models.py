"""Krok 5a: lista modeli u dostawców API → kandydaci do pomiaru.

Zapisuje surowe listy (results/api_catalog/) i plik z kandydatami do przeglądu
(results/api_catalog/kandydaci.csv). Agent wybiera z niego modele i wpisuje je do config/api_models.yaml
według reguł:
  * AIHubMix: modele darmowe i płatne z ceną WEJŚCIA ≤ 0,20 USD za 1 mln tokenów;
  * OpenRouter: tylko darmowe modele (cena 0), których NIE ma w AIHubMix;
  * pomijamy modele, których tokenizer jest publiczny i policzony lokalnie (poza 1–2 modelami kontrolnymi);
  * jeden model na rodzinę/tokenizer (np. jedna wersja Gemini Flash-Lite, nie trzy).

    python -m tt.api_models
"""
from __future__ import annotations

import csv
import os

import requests

from .common import RESULTS, write_json

AIHUBMIX_BASE = os.environ.get("AIHUBMIX_BASE_URL", "https://aihubmix.com/v1")
OPENROUTER_BASE = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
MAX_INPUT_USD_PER_M = 0.20


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def aihubmix_models() -> list[dict]:
    key = os.environ.get("AIHUBMIX_API_KEY")
    r = requests.get(f"{AIHUBMIX_BASE}/models", headers={"Authorization": f"Bearer {key}"} if key else {}, timeout=60)
    r.raise_for_status()
    raw = r.json()
    write_json(RESULTS / "api_catalog" / "aihubmix_raw.json", raw)
    items = raw.get("data", raw if isinstance(raw, list) else [])
    out = []
    for m in items:
        # Ceny AIHubMix bywają w różnych polach; gdy ich nie ma, agent uzupełnia ze strony cennika.
        p = m.get("pricing") or {}
        price = None
        for key_name in ("input", "prompt", "input_price", "prompt_price"):
            if key_name in p:
                price = _num(p[key_name])
                break
        if price is not None and price < 0.01:   # cena za token → za milion
            price *= 1e6
        out.append({"provider": "aihubmix", "model": m.get("id"), "input_usd_per_m": price,
                    "owned_by": m.get("owned_by"), "free": price == 0 if price is not None else None})
    return out


def openrouter_models() -> list[dict]:
    r = requests.get(f"{OPENROUTER_BASE}/models", timeout=60)
    r.raise_for_status()
    raw = r.json()
    write_json(RESULTS / "api_catalog" / "openrouter_raw.json", raw)
    out = []
    for m in raw.get("data", []):
        p = m.get("pricing") or {}
        prompt, completion = _num(p.get("prompt")), _num(p.get("completion"))
        free = prompt == 0 and (completion in (0, None))
        out.append({"provider": "openrouter", "model": m.get("id"), "input_usd_per_m": (prompt or 0) * 1e6,
                    "owned_by": (m.get("id") or "").split("/")[0], "free": free,
                    "tokenizer_hint": (m.get("architecture") or {}).get("tokenizer")})
    return out


def base_name(model_id: str) -> str:
    s = (model_id or "").lower().split("/")[-1]
    for suffix in (":free", "-free", "-preview", "-latest", "-instruct", "-chat"):
        s = s.replace(suffix, "")
    return s


def main() -> int:
    rows = []
    try:
        ahm = aihubmix_models()
        rows += ahm
        print(f"AIHubMix: {len(ahm)} modeli")
    except Exception as exc:  # noqa: BLE001
        ahm = []
        print(f"! AIHubMix: {exc}")
    try:
        orm = openrouter_models()
        print(f"OpenRouter: {len(orm)} modeli, darmowych: {sum(1 for m in orm if m['free'])}")
    except Exception as exc:  # noqa: BLE001
        orm = []
        print(f"! OpenRouter: {exc}")
    in_ahm = {base_name(m["model"]) for m in ahm}
    for m in orm:
        if m["free"]:
            m["also_in_aihubmix"] = base_name(m["model"]) in in_ahm
            rows.append(m)
    for m in rows:
        price = m.get("input_usd_per_m")
        if m["provider"] == "aihubmix":
            m["eligible"] = price is not None and price <= MAX_INPUT_USD_PER_M
        else:
            m["eligible"] = bool(m["free"]) and not m.get("also_in_aihubmix")
    path = RESULTS / "api_catalog" / "kandydaci.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    cols = ["provider", "model", "input_usd_per_m", "free", "eligible", "also_in_aihubmix", "owned_by", "tokenizer_hint"]
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore", delimiter=";")
        w.writeheader()
        w.writerows(rows)
    unknown = sum(1 for m in rows if m["provider"] == "aihubmix" and m["input_usd_per_m"] is None)
    print(f"Kandydaci: {path} ({sum(1 for m in rows if m['eligible'])} spełnia reguły; "
          f"AIHubMix bez ceny w API: {unknown} — sprawdź cennik na stronie)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
