"""Krok 10: raport i pliki do publikacji. Wszystkie liczby biorą się z results/ (nic nie wpisujemy ręcznie).

    python -m tt.report --author "Artur ..." --hf adegier/tokenizer-fertility-pl --gh adgr3/tokenizer-tax-pl

Tworzy:
  README.md                         raport + jak odtworzyć (strona główna repo GitHub)
  report/DISCORD.md                 krótka wersja do wklejenia
  publish/hf/                       karta zbioru danych + CSV do wgrania na Hugging Face
  publish/bench_team/tokenizer-fertility/   paczka dla Bench Team (do ewentualnego PR, po zgodzie zespołu)
  publish/nergal/KOMENTARZ.md       krótka notatka dla autora NERGAL-a (zakładka Community)
"""
from __future__ import annotations

import argparse
import shutil
from datetime import date

import pandas as pd

from .common import CHARTS, RESULTS, ROOT, WORK, languages, read_json

LANG = {lang["code"]: lang["pl"] for lang in languages()}


def f(x, d=2):
    if x is None or (isinstance(x, float) and x != x):
        return "—"
    return f"{x:.{d}f}".replace(".", ",")


def md_table(df: pd.DataFrame, cols: dict, digits: dict | None = None) -> str:
    digits = digits or {}
    head = "| " + " | ".join(cols.values()) + " |\n|" + "|".join("---" for _ in cols) + "|\n"
    rows = []
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            cells.append(f(v, digits.get(c, 2)) if isinstance(v, float) else str(v))
        rows.append("| " + " | ".join(cells) + " |")
    return head + "\n".join(rows) + "\n"


def build(args) -> dict:
    t = RESULTS / "tables"
    s = read_json(RESULTS / "summary.json")
    long = pd.read_csv(t / "fertility_long.csv")
    label = long.drop_duplicates("tokenizer").set_index("tokenizer")["label"].to_dict()
    lab = lambda i: label.get(i, i)  # noqa: E731
    agg_lang = pd.read_csv(t / "agg_languages.csv", index_col=0)
    agg_tok = pd.read_csv(t / "agg_tokenizers.csv", index_col=0)
    agg_fam = pd.read_csv(t / "agg_families.csv", index_col=0)
    agg_origin = pd.read_csv(t / "agg_origin.csv", index_col=0)
    agg_vocab = pd.read_csv(t / "agg_vocab.csv", index_col=0)
    pl = s["polish"]
    cal = s.get("calibration")
    sp = s.get("api_spend") or {}
    today = date.today().isoformat()

    # ---------- najważniejsze wnioski (automatycznie z liczb)
    best = ", ".join(f"{x['language_pl']} ({f(x['mean'])})" for x in s["languages_best"])
    worst = ", ".join(f"{x['language_pl']} ({f(x['mean'])})" for x in s["languages_worst"])
    fam_sorted = agg_fam.sort_values("tax_vs_en")
    fams = ", ".join(f"{i} {f(r['tax_vs_en'])}×" for i, r in fam_sorted.iterrows())
    top_pl = ", ".join(f"{x['label']} ({f(x['pl'])})" for x in s["tokenizers_best_pl"][:3])
    bottom_pl = ", ".join(f"{x['label']} ({f(x['pl'])})" for x in s["tokenizers_worst_pl"][-3:])
    pol_origin = agg_origin.loc["Polska", "pl"] if "Polska" in agg_origin.index else None
    other_origin = agg_tok[agg_tok["origin"] != "Polska"]["pl"].mean()
    bullets = [
        f"**Polski** kosztuje średnio **{f(pl['mean'])} tokenu na słowo**, czyli **{f(pl['tax_vs_en'])}×** tyle co angielski "
        f"(miejsce {pl['rank_of_25']} z 25 języków). Rozrzut między tokenizerami jest duży: od {f(pl['min'])} "
        f"({lab(pl['min_tokenizer'])}) do {f(pl['max'])} ({lab(pl['max_tokenizer'])}).",
        f"Najtaniej wychodzą: {best}. Najdrożej: {worst}.",
        f"Po rodzinach językowych (ile razy drożej niż angielski): {fams}.",
        f"Najlepsze tokenizery dla polskiego: {top_pl}; najsłabsze: {bottom_pl}.",
    ]
    if pol_origin is not None:
        bullets.append(f"Tokenizery polskich modeli: średnio {f(pol_origin)} tok./słowo po polsku; pozostałe: {f(other_origin)}.")
    if s.get("vocab_vs_pl_spearman") is not None:
        bullets.append(f"Wielkość słownika a polski: korelacja rang Spearmana {f(s['vocab_vs_pl_spearman'])} "
                       f"(dla angielskiego {f(s['vocab_vs_en_spearman'])}). Wartość ujemna = większy słownik, mniej tokenów.")
    bullets.append(f"Ranking tokenizerów jest między językami {'stabilny' if s['mean_rank_correlation_between_languages'] >= 0.7 else 'niestabilny'}: "
                   f"średnia korelacja rang {f(s['mean_rank_correlation_between_languages'])}. Polskiemu najbliżej rankingiem do: "
                   f"{LANG.get(pl['most_similar_language_ranking'])}, najdalej: {LANG.get(pl['least_similar_language_ranking'])}.")
    if s.get("polish_registers"):
        pr = s["polish_registers"]
        rho = ", ".join(f"{k} {f(v)}" for k, v in pr["spearman_vs_sib"].items())
        bullets.append(f"Polski na różnych rodzajach tekstu: zgodność rankingu z SIB-200 (Spearman): {rho}.")
    api_alias = {k: v for k, v in s["aliases"].items() if k.startswith("api_")}
    if api_alias:
        bullets.append("Modele przez API z tokenizerem identycznym jak lokalny: " +
                       ", ".join(f"{lab(k)} = {lab(v)}" for k, v in api_alias.items()) + ".")

    # ---------- tabele
    rep = pd.read_csv(t / "replication.csv", index_col=0)
    rep_md = "| język | " + " | ".join(lab(c) for c in rep.columns) + " |\n|" + "|".join("---" for _ in range(len(rep.columns) + 1)) + "|\n"
    for code, r in rep.iterrows():
        name = f"**{LANG[code]}**" if code == "pol_Latn" else LANG[code]
        rep_md += f"| {name} | " + " | ".join(f(v, 1) for v in r) + " |\n"
    agg_lang_md = md_table(agg_lang.sort_values("mean").assign(min_l=lambda d: d["min_tokenizer"].map(lab), max_l=lambda d: d["max_tokenizer"].map(lab)),
                           {"language_pl": "język", "family": "rodzina", "mean": "średnio", "median": "mediana",
                            "min": "min", "min_l": "najlepszy tokenizer", "max": "maks.", "max_l": "najgorszy", "tax_vs_en_mean": "× ang."})
    tok_md = md_table(agg_tok.sort_values("pl").assign(worst=lambda d: d["worst_language"].map(LANG)),
                      {"label": "tokenizer", "origin": "pochodzenie", "vocab_size": "słownik", "pl": "PL", "en": "EN",
                       "pl_vs_en": "PL/EN", "mean_25": "średnio 25 jęz.", "worst": "najgorszy język", "worst_vs_en": "× ang.",
                       "pl_words_per_4096": "PL słów w 4096 tok."}, {"vocab_size": 0, "pl_words_per_4096": 0})
    fam_md = md_table(fam_sorted.reset_index(), {"family": "rodzina", "mean": "średnio tok./słowo", "tax_vs_en": "× ang.", "languages": "języków"})
    origin_md = md_table(agg_origin.reset_index(), {"origin": "pochodzenie", "n": "tokenizerów", "pl": "PL", "mean_25": "średnio 25", "pl_vs_en": "PL/EN"})
    vocab_md = md_table(agg_vocab.reset_index(), {"vocab_bucket": "słownik", "n": "tokenizerów", "pl": "PL", "mean_25": "średnio 25", "pl_vs_en": "PL/EN"})

    api_rows = agg_tok[agg_tok["method"].astype(str).str.startswith("api")]
    api_md = md_table(api_rows.assign(cost=lambda d: d["usd_per_1000_pl_words"]),
                      {"label": "model", "pl": "PL", "en": "EN", "input_usd_per_m": "USD / 1 mln tok.", "cost": "USD / 1000 PL słów"},
                      {"cost": 6, "input_usd_per_m": 3}) if len(api_rows) else "_Brak modeli mierzonych przez API._\n"

    bench_md = ""
    if (t / "bench_team.csv").exists():
        b = pd.read_csv(t / "bench_team.csv")
        cols = {"label": "model", "fertility_pol_Latn": "PL tok./słowo", "fertility_eng_Latn": "EN tok./słowo",
                "bytes_per_token_pol_Latn": "PL bajtów/token", "bytes_per_token_eng_Latn": "EN bajtów/token"}
        if "tokens_vs_slayer_pl" in b:
            cols["tokens_vs_slayer_pl"] = "PL tokenów vs Slayer"
        bench_md = md_table(b.sort_values("fertility_pol_Latn"), cols)
    nergal_md = ""
    if (t / "nergal_encoders.csv").exists():
        e = pd.read_csv(t / "nergal_encoders.csv")
        cols = {"label": "enkoder", "vocab_size": "słownik", "fertility": "PL tok./słowo", "pl_words_per_510": "PL słów / okno 512",
                "pl_chars_per_510": "PL znaków / okno 512"}
        if "tokens_vs_nergal" in e:
            cols["tokens_vs_nergal"] = "tokenów vs NERGAL"
        nergal_md = md_table(e, cols, {"vocab_size": 0, "pl_words_per_510": 0, "pl_chars_per_510": 0})

    skipped = "\n".join(f"- {k}: {v}" for k, v in s.get("skipped", {}).items()) or "- brak"
    aliases = "\n".join(f"- {lab(k)} → ten sam tokenizer co {lab(v)}" for k, v in s["aliases"].items()) or "- brak"
    cal_line = (f"Na {cal['n']} parach (tokenizer × język) średnia różnica wobec danych autora pracy to "
                f"**{f(cal['mean_abs'], 3)}** tokenu na słowo, maksymalna {f(cal['max_abs'], 3)} → "
                f"{'kalibracja zaliczona' if cal['passed'] else '**kalibracja NIEZALICZONA — wyniki do sprawdzenia**'}.") if cal else \
        "Kalibracji nie wykonano."
    plan = read_json(RESULTS / "subsample.json") if (RESULTS / "subsample.json").exists() else None
    api_line = (f"Przez API: AIHubMix — modele z ceną wejścia ≤ 0,20 USD/1 mln tokenów, {plan['k_aihubmix']} bloki na język "
                f"(błąd próbkowania ≤ {f(plan['thresholds']['max_abs'], 2)}); OpenRouter — tylko darmowe modele spoza AIHubMix, "
                f"1 blok na język (błąd średnio {f(plan['error_k1']['mean_abs'], 3)}, maks. {f(plan['error_k1']['max_abs'], 3)}). "
                f"Wydano {f(sp.get('aihubmix_usd', 0), 4)} USD.") if plan else ""

    charts = sorted(p.name for p in CHARTS.glob("*.png"))
    img = lambda n, alt: f"![{alt}](charts/{n})\n" if n in charts else ""  # noqa: E731

    report = f"""# Podatek tokenowy: ile tokenów na jedno słowo w 25 językach

Replikacja wykresu z pracy [arXiv 2605.24718](https://arxiv.org/abs/2605.24718) („The Tokenizer Tax Across 25 European
Languages”) dla polskich modeli (PLLuM, Bielik, Slayer1B i inne) i rozszerzenie z analizą w agregacie: języki, rodziny językowe,
grupy tokenizerów. Zmierzono {s['n_tokenizers_measured']} modeli ({s['n_local']} lokalnie, {s['n_api']} przez API); po
odrzuceniu powtórzeń tego samego tokenizera zostaje **{s['n_unique_llm']} unikalnych tokenizerów LLM**. Do tego
{s['n_encoders']} tokenizery enkoderów (NERGAL i porównanie).

Autor: {args.author}. Data: {today}. Dane: [Hugging Face](https://huggingface.co/datasets/{args.hf}). Kod: [GitHub](https://github.com/{args.gh}).

## Najważniejsze wnioski

""" + "\n".join(f"- {b}" for b in bullets) + f"""

{img('01_replikacja.png', 'Replikacja')}
## Metoda

- Tekst: [SIB-200](https://huggingface.co/datasets/Davlan/sib200), split testowy, 204 te same zdania w 25 językach
  (24 języki UE i ukraiński — zestaw z pracy). Zdania sklejone w bloki po ok. 6000 znaków.
- Miara: **tokeny na słowo**, słowo = ciąg znaków rozdzielony spacjami; wynik = średnia po blokach (jak w pracy).
  Tokeny liczone bez znaczników specjalnych (BOS/EOS).
- Tokenizery otwarte: liczone lokalnie (pobrany tylko tokenizer, bez wag modelu). {api_line}
- Jeden tokenizer = jedna kolumna w agregatach. Modele dzielące tokenizer (identyczne wyniki na tekstach kontrolnych)
  są aliasami; polskie modele z polecenia zostają w tabeli replikacji z dopiskiem „= …”.
- Kalibracja: {cal_line}

## Replikacja: tokenizery z pracy i polskie modele

{rep_md}
## Agregat po językach

{img('03_jezyki.png', 'Języki')}
{agg_lang_md}
{img('04_rodziny.png', 'Rodziny')}
{fam_md}
## Agregat po tokenizerach

{img('05_ranking_polski.png', 'Ranking dla polskiego')}
{tok_md}
### Grupy tokenizerów

Według pochodzenia:

{origin_md}
Według wielkości słownika:

{vocab_md}
{img('06_slownik_vs_polski.png', 'Słownik a polski')}
{img('02_wszystkie.png', 'Wszystkie tokenizery')}
## Czy ranking zależy od języka?

{img('07_stabilnosc_rankingu.png', 'Stabilność rankingu')}
Średnia korelacja rang Spearmana między językami: {f(s['mean_rank_correlation_between_languages'])}.

""" + (f"""## Polski na różnych rodzajach tekstu

{img('08_polski_rodzaje_tekstu.png', 'Polski: rodzaje tekstu')}
Próbki z [SlayerLab/polish-dynaword](https://huggingface.co/datasets/SlayerLab/polish-dynaword); tekstów nie publikujemy.
Zgodność rankingu z SIB-200 (Spearman): {", ".join(f"{k} {f(v)}" for k, v in s['polish_registers']['spearman_vs_sib'].items())}.

""" if s.get("polish_registers") else "") + f"""## Modele przez API: koszt polskiego tekstu

{api_md}
## Dla Bench Team (Slayer 1B, modele odniesienia, Pythia)

Ile tokenów na polskie i angielskie słowo oraz ile bajtów UTF-8 przypada na token. Przydaje się przy porównywaniu
wyników liczonych na token (np. BLiMP na token), przy przeliczaniu udziału angielskiego w danych między tokenizerami
i przy decyzji o tokenizerze kolejnej wersji Slayera.

{bench_md or '_Brak danych._'}
## Dla NERGAL-a (enkodery)

NERGAL to XLM-RoBERTa-large z dwoma znacznikami; tnie tekst na okna do 512 tokenów. Tabela pokazuje, ile polskiego tekstu
mieści jedno okno w porównaniu z polskimi enkoderami. To przybliżenie (bez znaczników specjalnych i bez nakładania okien).

{img('09_nergal_enkodery.png', 'NERGAL')}
{nergal_md or '_Brak danych._'}
## Ograniczenia

- Jeden rodzaj tekstu w porównaniu 25 języków (wiadomości, SIB-200/FLORES); inne rodzaje tylko dla polskiego.
- „Słowo” liczone po spacjach — języki z długimi złożeniami (fiński, węgierski, niemiecki) mają mniej, dłuższych słów.
- Przez API liczba tokenów pochodzi od dostawcy; narzut szablonu czatu odjęty na podstawie zapytania „x”.
  Modele OpenRouter liczone na 1 bloku na język (mniejsza dokładność).
- Tokeny na słowo to koszt i pojemność kontekstu, a nie jakość modelu.

## Aliasy i pominięte tokenizery

Aliasy (ten sam tokenizer):
{aliases}

Pominięte (z powodem):
{skipped}

## Źródła i podziękowania

- Praca i dane referencyjne: V. Ovcharov, [arXiv 2605.24718](https://arxiv.org/abs/2605.24718),
  [overthelex/tokenizer-fertility-map](https://huggingface.co/datasets/overthelex/tokenizer-fertility-map).
- Pierwsza polska wersja wykresu i metoda bloków: Dariusz Ciba.
- Tekst: [SIB-200](https://huggingface.co/datasets/Davlan/sib200) (CC BY-SA 4.0), [polish-dynaword](https://huggingface.co/datasets/SlayerLab/polish-dynaword).
"""
    repro = f"""
## Jak odtworzyć

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt   # Windows: .venv\\Scripts\\pip
python -m tt.data            # SIB-200
python -m tt.measure_local   # tokenizery lokalne
python -m tt.calibrate       # zgodność z danymi z pracy
python -m tt.subsample       # ile bloków wystarczy przez API
python -m tt.api_models && python -m tt.measure_api   # API (klucze w .env)
python -m tt.polish --sample && python -m tt.polish   # polski: rodzaje tekstu (opcjonalnie)
python -m tt.analyze && python -m tt.charts && python -m tt.report
```

Wyniki surowe: `results/local/`, `results/apisum/`, tabele: `results/tables/`, liczby raportu: `results/summary.json`.
"""
    (WORK / "README.md").write_text(report + repro, encoding="utf-8")

    discord = f"""**Podatek tokenowy — replikacja dla polskich modeli + agregat ({s['n_unique_llm']} tokenizerów, 25 języków)**

""" + "\n".join(f"• {b.replace('**', '')}" for b in bullets[:6]) + f"""

Kalibracja z danymi z pracy: średnio {f(cal['mean_abs'], 3) if cal else '—'} tok./słowo różnicy.
Raport i kod: https://github.com/{args.gh} · dane: https://huggingface.co/datasets/{args.hf}
"""
    (WORK / "report").mkdir(exist_ok=True)
    (WORK / "report" / "DISCORD.md").write_text(discord, encoding="utf-8")

    # ---------- Hugging Face: karta zbioru + dane
    hf = WORK / "publish" / "hf"
    if hf.exists():
        shutil.rmtree(hf)
    (hf / "data").mkdir(parents=True)
    for name in ["fertility_long.csv", "replication.csv", "agg_languages.csv", "agg_families.csv", "agg_tokenizers.csv",
                 "agg_origin.csv", "agg_vocab.csv", "spearman_languages.csv", "bench_team.csv", "nergal_encoders.csv",
                 "polish_registers.csv"]:
        if (t / name).exists():
            shutil.copy(t / name, hf / "data" / name)
    shutil.copy(RESULTS / "summary.json", hf / "data" / "summary.json")
    if (RESULTS / "calibration.json").exists():
        shutil.copy(RESULTS / "calibration.json", hf / "data" / "calibration.json")
    (hf / "charts").mkdir()
    for n in charts:
        shutil.copy(CHARTS / n, hf / "charts" / n)
    card = f"""---
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

Pomiary „podatku tokenowego” (tokeny na słowo) dla {s['n_unique_llm']} unikalnych tokenizerów LLM i {s['n_encoders']}
enkoderów na SIB-200 (split testowy, 25 języków), z replikacją arXiv 2605.24718 dla polskich modeli.
Raport z wykresami i kod: https://github.com/{args.gh}

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
{cal_line.replace('**', '')}

Zbiór zawiera wyłącznie pomiary; nie zawiera tekstów SIB-200 ani polish-dynaword.

## Cytowanie

Ovcharov V., „The Tokenizer Tax Across 25 European Languages”, arXiv:2605.24718 (2026). Pierwsza polska wersja wykresu:
Dariusz Ciba. Ten zbiór: {args.author}, {today}.
"""
    (hf / "README.md").write_text(card, encoding="utf-8")

    # ---------- Bench Team: paczka analizy (do PR dopiero po zgodzie zespołu na #bench-team)
    bt = WORK / "publish" / "bench_team" / "tokenizer-fertility"
    if bt.exists():
        shutil.rmtree(bt)
    (bt / "results").mkdir(parents=True)
    for name in ["bench_team.csv", "agg_tokenizers.csv", "fertility_long.csv"]:
        if (t / name).exists():
            shutil.copy(t / name, bt / "results" / name)
    (bt / "README.md").write_text(f"""# Tokeny na słowo: Slayer 1B i modele odniesienia

Analiza pomocnicza (nie benchmark): ile tokenów na słowo i bajtów UTF-8 na token mają tokenizery Slayera 1B, pięciu
modeli odniesienia i modelu kontrolnego Pythia, po polsku i po angielsku (SIB-200, test; 25 języków w pełnej wersji).

Po co zespołowi:
- porównania liczone na token (np. BLiMP „na token”) zależą od tokenizera — tabela podaje przelicznik;
- udział angielskiego w danych liczony w tokenach różni się między tokenizerami (karta Slayera 1.00: 10% w cl100k,
  17,6% w tokenach Slayera) — tabela pozwala przeliczać;
- obszar „Architecture & Learning”: dane do decyzji o tokenizerze kolejnej wersji (koszt i pojemność kontekstu po polsku).

{bench_md}
Pełny raport, kalibracja i kod: https://github.com/{args.gh}. Dane: https://huggingface.co/datasets/{args.hf}.
Wartości to pomiar deterministyczny (bez losowania pytań); SE podane w `results/fertility_long.csv` to rozrzut między
blokami tekstu.
""", encoding="utf-8")
    (bt / "RECIPE.md").write_text(f"""# Przepis

- Kod: https://github.com/{args.gh} (commit: uzupełnij po wypchnięciu)
- Dane: Davlan/sib200, split test, 25 języków; bloki ok. 6000 znaków
- Komendy: `python -m tt.data && python -m tt.measure_local && python -m tt.analyze`
- Tokenizery i rewizje: `results/fertility_long.csv` (kolumna `repo_used`) i `results/local/*.json` w repo kodu
- Sprzęt: CPU (GPU niepotrzebne). Data: {today}
""", encoding="utf-8")
    # ---------- NERGAL: krótka notatka do zakładki Community przy modelu
    if nergal_md:
        ng = WORK / "publish" / "nergal"
        ng.mkdir(parents=True, exist_ok=True)
        (ng / "KOMENTARZ.md").write_text(f"""Tytuł: Ile polskiego tekstu mieści okno NERGAL-a — porównanie tokenizerów enkoderów

Cześć, przy okazji pomiaru „tokenów na słowo” (SIB-200, 25 języków; raport: https://github.com/{args.gh}) policzyłem
też tokenizer NERGAL-a (XLM-RoBERTa) i polskie enkodery. Tabela pokazuje, ile polskiego tekstu mieści jedno okno
512 tokenów (przybliżenie: bez znaczników specjalnych i bez nakładania okien).

{nergal_md}
Co z tego wynika: tokenizer wpływa na szybkość i liczbę okien na dokument, nie na jakość wykrywania. Jeśli kiedyś
powstanie wersja NERGAL-a na polskim enkoderze, ta tabela pokazuje, ile tekstu zyskałoby jedno okno.
Dane: https://huggingface.co/datasets/{args.hf} (plik data/nergal_encoders.csv).
""", encoding="utf-8")

    print(f"README.md, report/DISCORD.md, publish/hf/ ({len(list((hf / 'data').iterdir()))} plików danych), publish/bench_team/")
    return s


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--author", default="adgr3")
    ap.add_argument("--hf", default="adegier/tokenizer-fertility-pl")
    ap.add_argument("--gh", default="adgr3/tokenizer-tax-pl")
    build(ap.parse_args(argv))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
