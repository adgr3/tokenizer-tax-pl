---
license: cc-by-sa-4.0
language: [pl, en, es, fr, pt, it, nl, de, da, sv, ro, ga, cs, sl, hr, bg, sk, uk, hu, et, lt, lv, fi, el, mt]
pretty_name: Tokenizer fertility — Polish models and 25 European languages
tags: [tokenizer, fertility, tokenizer-tax, polish, multilingual, evaluation]
size_categories: [n<1K]
configs:
  - config_name: default
    data_files: data/fertility_long.csv
  - config_name: replication
    data_files: data/replication.csv
  - config_name: tokenizers
    data_files: data/agg_tokenizers.csv
  - config_name: languages
    data_files: data/agg_languages.csv
---

# Ile tokenów na jedno słowo — polskie modele i 25 języków europejskich

Pomiary „podatku tokenowego” (tokeny na słowo) dla 52 unikalnych tokenizerów LLM i 4
enkoderów na SIB-200 (split testowy, 25 języków), z replikacją arXiv 2605.24718 dla polskich modeli.
Raport z wykresami i kod: https://github.com/adgr3/tokenizer-tax-pl

## Pliki

- `data/fertility_long.csv` — jeden wiersz = tokenizer × język: `fertility` (średnia po blokach), `se`, `n_blocks`,
  `chars_per_token`, `bytes_per_token`, metoda (`local` / `api:<dostawca>`), `alias_of` (ten sam tokenizer co …).
- `data/replication.csv` — tabela jak na wykresie z pracy, z kolumnami polskich modeli.
- `data/agg_*.csv` — agregaty po językach, rodzinach, tokenizerach, pochodzeniu i wielkości słownika.
- `data/spearman_languages.csv` — zgodność rankingu tokenizerów między językami.
- `data/bench_team.csv`, `data/nergal_encoders.csv`, `data/polish_registers.csv` — tabele tematyczne.
- `data/summary.json`, `data/calibration.json` — liczby raportu i kalibracja z danymi autora pracy.

## Metoda

SIB-200 test (204 zdania), bloki ok. 6000 znaków, tokeny / słowa (podział po spacjach), średnia po blokach.
Kalibracja z [overthelex/tokenizer-fertility-map](https://huggingface.co/datasets/overthelex/tokenizer-fertility-map):
Na 150 parach (tokenizer × język) średnia różnica wobec danych autora pracy to 0,014 tokenu na słowo, maksymalna 0,068 → kalibracja zaliczona.

Zbiór zawiera wyłącznie pomiary; nie zawiera tekstów SIB-200 ani polish-dynaword.

## Cytowanie

Ovcharov V., „The Tokenizer Tax Across 25 European Languages”, arXiv:2605.24718 (2026). Pierwsza polska wersja wykresu:
Dariusz Ciba. Ten zbiór: adgr3, 2026-11-01.

## Pre-tokenizacja (praca 2)

- `data/regex_catalog.csv` — jaki pre-tokenizer (regex / SentencePiece) ma każdy tokenizer i jak tnie sondy
  (liczby, skróty, camelCase, „Answer:A”, „(Łódź”, „ZUS-u”).
- `data/regex_stats_long.csv` — SIB-200: kawałki na słowo, odsetek słów = 1 token, 25 języków.
- `data/regex_bench_*.csv` — litera odpowiedzi i liczby (Bench Team), `data/regex_nergal_*.csv` — dane osobowe w
  tokenach i reguły `scrub_pii.py` NERGAL-a na identyfikatorach przetargowych.
