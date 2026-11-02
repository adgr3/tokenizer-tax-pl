"""Praca domowa 2 — raport o pre-tokenizacji: REGEX.md + paczki dla Bench Team i NERGAL-a + dane na HF.

Uruchamiać PO `python -m tt.report` (dokłada pliki do publish/hf/).

    python -m tt.report_regex --hf adegier/tokenizer-fertility-pl --gh adgr3/tokenizer-tax-pl
"""
from __future__ import annotations

import argparse
import csv
import shutil
from datetime import date

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .common import CHARTS, RESULTS, ROOT, WORK, languages  # noqa: E402

OUT = RESULTS / "regex"
LANG = {l["code"]: l["pl"] for l in languages()}  # noqa: E741


def rcsv(name: str) -> list[dict]:
    p = OUT / name
    if not p.exists() or not p.stat().st_size:
        return []
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def pct(x) -> str:
    return f"{float(x) * 100:.0f}%".replace(".", ",")


def num(x, d=2) -> str:
    return f"{float(x):.{d}f}".replace(".", ",")


def agent_text(src: str, name: str) -> str:
    """Wstawia tekst z report/<name> pod komentarzem <!-- AGENT: … --> (przetrwa ponowne generowanie raportu)."""
    f = WORK / "report" / name
    if not f.exists():
        return src
    end = src.index("-->", src.index("<!-- AGENT:")) + 3
    return src[:end] + "\n\n" + f.read_text(encoding="utf-8").strip() + "\n" + src[end:]


def is_approx(r: dict) -> bool:
    """Bez regexu (SentencePiece, ByteLevel bez regexu, wolny tokenizer) — kawałki to przybliżenie podziałem po spacji."""
    return (r.get("approx") or "False") != "False"


def cell(s: str) -> str:
    return (s or "").replace("|", "\\|")


def charts(stats: list[dict]) -> list[str]:
    made = []
    by = {}
    for r in stats:
        by.setdefault(r["tokenizer"], {})[r["language"]] = r
    rows = [(v["eng_Latn"]["label"] + (" *" if is_approx(v["eng_Latn"]) else ""),
             float(v["eng_Latn"]["single_token_word_share"]), float(v["pol_Latn"]["single_token_word_share"]))
            for v in by.values() if "eng_Latn" in v and "pol_Latn" in v and v["eng_Latn"]["group"] != "encoder"]
    if rows:
        rows.sort(key=lambda r: r[2])
        fig, ax = plt.subplots(figsize=(8.5, 0.3 * len(rows) + 1.8))
        y = range(len(rows))
        ax.barh([i + 0.2 for i in y], [r[1] * 100 for r in rows], height=0.4, color="#4C72B0", label="angielski")
        ax.barh([i - 0.2 for i in y], [r[2] * 100 for r in rows], height=0.4, color="#C0392B", label="polski")
        ax.set_yticks(list(y), [r[0] for r in rows], fontsize=8)
        ax.set_xlabel("% słów (kawałków z literami), które są jednym tokenem\n"
                      "* bez regexu — kawałki przybliżone podziałem po spacji (słowo razem z interpunkcją)", fontsize=8)
        ax.set_xlim(0, 100)
        ax.legend(fontsize=8, loc="lower right")
        ax.set_title("Ile słów mieści się w jednym tokenie? (SIB-200)", loc="left", fontweight="bold")
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        fig.tight_layout()
        fig.savefig(CHARTS / "10_regex_slowo_jeden_token.png", dpi=200)
        plt.close(fig)
        made.append("10_regex_slowo_jeden_token.png")
    # związek z pracą 1: odsetek słów = 1 token vs tokeny na słowo (polski)
    fert = {}
    p1 = RESULTS / "tables" / "fertility_long.csv"
    if p1.exists():
        with open(p1, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["language"] == "pol_Latn":
                    fert[r["tokenizer"]] = float(r["fertility"])
    # tokenizery spoza pracy 1 (np. Aster): wynik tą samą metodą v1, zmierzony osobno (test v2, #418)
    from .common import load_yaml
    for spec in load_yaml("regex_examples.yaml").get("extra_tokenizers") or []:
        if spec.get("fertility_pl_v1") is not None:
            fert.setdefault(spec["id"], float(spec["fertility_pl_v1"]))
    pts = [(v["pol_Latn"]["label"], float(v["pol_Latn"]["single_token_word_share"]), fert[k], is_approx(v["pol_Latn"]))
           for k, v in by.items() if "pol_Latn" in v and k in fert and v["pol_Latn"]["group"] != "encoder"]
    if len(pts) >= 3:
        fig, ax = plt.subplots(figsize=(11, 7.5))
        for ap, face in ((False, "#C0392B"), (True, "white")):
            sel = [p for p in pts if p[3] == ap]
            ax.scatter([p[1] * 100 for p in sel], [p[2] for p in sel], facecolor=face, edgecolor="#C0392B", s=30, zorder=3,
                       label="bez regexu (przybliżenie)" if ap else "z regexem")
        # punkty w tym samym miejscu (ten sam tokenizer pod inną nazwą) → jeden podpis; podpisy rozsuwane jak w wykresie 06
        groups = {}
        for lab, x, yv, ap in pts:
            groups.setdefault((round(x * 100), round(yv, 2)), [x * 100, yv, []])[2].append(lab + (" *" if ap else ""))
        fig.canvas.draw()
        rend = fig.canvas.get_renderer()
        from matplotlib.transforms import Bbox
        # punkty też są „zajęte”, żeby podpisy nie zasłaniały kółek
        placed = [Bbox.from_bounds(px - 3.5, py - 3.5, 7, 7)
                  for px, py in ax.transData.transform([(p[1] * 100, p[2]) for p in pts])]
        skipped = 0
        offsets = [(5, 2), (5, -9), (-5, 2), (-5, -9), (5, 11), (-5, 11), (5, -18), (-5, -18), (5, 20), (-5, 20),
                   (5, -27), (-5, -27), (5, 29), (-5, 29)]
        for vx, vy, names in sorted(groups.values(), key=lambda g: (-len(g[2]), -g[1])):
            txt = " / ".join(names)
            for dx, dy in offsets:
                ha = "left" if dx > 0 else "right"
                t_ = ax.annotate(txt, (vx, vy), fontsize=7, xytext=(dx, dy), textcoords="offset points", ha=ha)
                bb = t_.get_window_extent(renderer=rend).expanded(1.0, 1.05)
                t_.remove()
                inside = ax.get_window_extent(renderer=rend).contains(bb.x0, bb.y0) and \
                    ax.get_window_extent(renderer=rend).contains(bb.x1, bb.y1)
                if inside and not any(bb.overlaps(o) for o in placed):
                    placed.append(bb)
                    ax.annotate(txt, (vx, vy), fontsize=7, xytext=(dx, dy), textcoords="offset points", ha=ha,
                                arrowprops=None if (dx, dy) == (5, 2) else {"arrowstyle": "-", "color": "#999", "lw": 0.5,
                                                                            "shrinkA": 0, "shrinkB": 3})
                    break
            else:
                skipped += len(names)
        ax.legend(fontsize=8, loc="upper right")
        ax.set_xlabel("% polskich słów, które są jednym tokenem"
                      + (f"\n(punkty bez podpisu w gęstych skupiskach: {skipped} — wartości w tabeli w REGEX.md)" if skipped else ""))
        ax.set_ylabel("tokeny na polskie słowo (praca 1)")
        ax.set_title("Mniej rozbitych słów = tańszy polski", loc="left", fontweight="bold")
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        fig.tight_layout()
        fig.savefig(CHARTS / "11_regex_vs_tokeny_na_slowo.png", dpi=200)
        plt.close(fig)
        made.append("11_regex_vs_tokeny_na_slowo.png")
    return made


def build(args) -> None:
    cat = rcsv("catalog.csv")
    stats = rcsv("stats_long.csv")
    ans = rcsv("bench_answer.csv")
    nums = rcsv("bench_numbers.csv")
    ntok = rcsv("nergal_tokens.csv")
    rules = rcsv("nergal_rules.csv")
    made = charts(stats) if stats else []
    explain = (ROOT / "docs" / "REGEX_OBJASNIENIA.md").read_text(encoding="utf-8")
    demo = (OUT / "demo.md").read_text(encoding="utf-8") if (OUT / "demo.md").exists() else "_Brak demo._"
    today = date.today().isoformat()

    # porównanie rodzin
    probe_cols = [("liczba_8_cyfr", "12345678"), ("skrot_en", "They'LL"), ("camelcase", "XMLHttpRequest"),
                  ("bez_spacji_litera", "Answer:A"), ("nawias_polski", "(Łódź"), ("skrotowiec_odmiana", "ZUS-u")]
    fam = "| tokenizer | pre-tokenizer | regex | " + " | ".join(f"`{t}`" for _, t in probe_cols) + " |\n"
    fam += "|" + "---|" * (3 + len(probe_cols)) + "\n"
    for r in sorted(cat, key=lambda r: (r["regex_family"] or "", r["label"])):
        if r["group"] == "encoder":
            continue
        fam += f"| {cell(r['label'])} | {cell(r['pre_tokenizer'])} | {cell(r['regex_family'])} | " + \
               " | ".join(f"`{cell(r.get('probe_' + k, ''))}`" for k, _ in probe_cols) + " |\n"

    # statystyki EN/PL
    by = {}
    for r in stats:
        by.setdefault(r["tokenizer"], {})[r["language"]] = r
    head = "| tokenizer | kawałków na słowo EN | PL | słowo = 1 token EN | PL | tokenów na słowo-kawałek PL |\n|---|---|---|---|---|---|\n"
    srt = sorted((v for v in by.values() if "pol_Latn" in v and "eng_Latn" in v),
                 key=lambda v: -float(v["pol_Latn"]["single_token_word_share"]))

    def stat_rows(vs):
        out = head
        for v in vs:
            e, p = v["eng_Latn"], v["pol_Latn"]
            out += f"| {cell(p['label'])} | {num(e['pieces_per_word'])} | {num(p['pieces_per_word'])} | {pct(e['single_token_word_share'])} | " \
                   f"{pct(p['single_token_word_share'])} | {num(p['tokens_per_word_piece'])} |\n"
        return out
    st = stat_rows(v for v in srt if not is_approx(v["pol_Latn"]))
    noregex = [v for v in srt if is_approx(v["pol_Latn"])]
    st_noregex = stat_rows(noregex) if noregex else ""
    llm = [v for v in srt if v["pol_Latn"]["group"] != "encoder" and not is_approx(v["pol_Latn"])]
    if llm:
        mean_en = sum(float(v["eng_Latn"]["single_token_word_share"]) for v in llm) / len(llm)
        mean_pl = sum(float(v["pol_Latn"]["single_token_word_share"]) for v in llm) / len(llm)
        stat_line = (f"Średnio po {len(llm)} tokenizerach LLM z regexem: **{pct(mean_en)}** angielskich i **{pct(mean_pl)}** "
                     f"polskich słów to jeden token. Praca Boundless BPE podaje 90–95% dla angielskiego przy własnych tokenizerach.")
    else:
        stat_line = ""
    mism, nlang = {}, len({r["language"] for r in stats})
    for r in stats:
        if int(r.get("mismatch_blocks") or 0):
            m = mism.setdefault(r["label"], {"blocks": 0, "langs": [], "approx": is_approx(r)})
            m["blocks"] += int(r["mismatch_blocks"])
            m["langs"].append(r["language"])
    everywhere = [k for k, m in mism.items() if len(m["langs"]) == nlang]
    some = [f"{k} ({m['blocks']} bl. w {len(m['langs'])} jęz.{'' if 'pol_Latn' in m['langs'] else ', bez polskiego'})"
            for k, m in mism.items() if k not in everywhere]
    mism_line = "Kontrola: suma tokenów kawałków = pełne kodowanie we wszystkich blokach (`mismatch_blocks` = 0)." if not mism else (
        "Kontrola (`mismatch_blocks` — suma tokenów kawałków ≠ pełne kodowanie): "
        + (f"pojedyncze bloki — {', '.join(some)}; odsetki tych tokenizerów są lekko przybliżone. " if some else "")
        + (f"We wszystkich {nlang} językach — {', '.join(everywhere)}: to ByteLevel bez regexu, BPE skleja tu tokeny ponad "
           f"spacjami (np. `:␣A`), więc podział po `Ġ` jest tylko orientacyjny." if everywhere else ""))

    # Aster obok Slayer1B i Bielików v3
    cat_by = {r["tokenizer"]: r for r in cat}
    pesel = {r["tokenizer"]: f"{r['n_tokens']}: `{cell(r['tokens'])}`" for r in ntok if r["category"] == "PESEL"}
    aster_md = ""
    cmp_ids = [i for i in ("aster", "slayer1b", "bielik_4_5b_v3", "bielik_11b_v3") if i in cat_by]
    if "aster" in cmp_ids:
        aster_md = ("| | " + " | ".join(cell(cat_by[i]["label"]) for i in cmp_ids) + " |\n|" + "---|" * (1 + len(cmp_ids)) + "\n")
        rowdefs = [("pre-tokenizer", lambda i: cell(cat_by[i]["pre_tokenizer"])),
                   ("regex", lambda i: cell(cat_by[i]["regex_family"]) if cat_by[i]["regexes"].strip() else "brak regexu"),
                   ("`12345678`", lambda i: f"`{cell(cat_by[i]['probe_liczba_8_cyfr'])}`"),
                   ("`Answer: A`", lambda i: f"`{cell(cat_by[i]['probe_spacja_litera'])}`"),
                   ("`Answer:A`", lambda i: f"`{cell(cat_by[i]['probe_bez_spacji_litera'])}`"),
                   ("`ZUS-u`", lambda i: f"`{cell(cat_by[i]['probe_skrotowiec_odmiana'])}`"),
                   ("PESEL `44051401359`", lambda i: pesel.get(i, "—")),
                   ("słowo = 1 token PL / EN", lambda i: (f"{pct(by[i]['pol_Latn']['single_token_word_share'])} / "
                                                          f"{pct(by[i]['eng_Latn']['single_token_word_share'])}"
                                                          + (" *" if is_approx(by[i]['pol_Latn']) else ""))
                    if i in by and "pol_Latn" in by[i] else "—")]
        for name, fn in rowdefs:
            aster_md += f"| {name} | " + " | ".join(fn(i) for i in cmp_ids) + " |\n"
        aster_md += "\n\\* bez regexu — przybliżenie podziałem po spacji.\n"

    # Bench Team
    ans_md = "| model | kontekst + odpowiedź | tokeny całości | odpowiedź osobno | odpowiedź w całości | zgodne |\n|---|---|---|---|---|---|\n"
    for r in ans:
        ans_md += f"| {cell(r['label'])} | `{cell(r['context'])}` + `{cell(r['continuation'])}` | `{cell(r['whole_tokens'])}` | " \
                  f"`{cell(r['continuation_alone'])}` | `{cell(r['continuation_in_context'])}` | {'tak' if r['same_as_alone'] == 'True' else '**nie**'} |\n"
    num_md = "| model | " + " | ".join(dict.fromkeys(f"`{r['number']}`" for r in nums)) + " |\n"
    num_md += "|" + "---|" * (1 + len(dict.fromkeys(r["number"] for r in nums))) + "\n"
    for lab in dict.fromkeys(r["label"] for r in nums):
        num_md += f"| {cell(lab)} | " + " | ".join(f"`{cell(r['tokens'])}`" for r in nums if r["label"] == lab) + " |\n"
    bt_dir = WORK / "publish" / "bench_team" / "regex"
    bt_dir.mkdir(parents=True, exist_ok=True)
    (bt_dir / "README.md").write_text(f"""# Pre-tokenizacja a ocena odpowiedzi i liczb: Slayer 1B i modele odniesienia

Analiza pomocnicza do zadania **A6** („litera odpowiedzi ze spacją i bez”) i do testów z liczbami.

## Dlaczego „A” i „␣A” to różne tokeny

We wszystkich tokenizerach z regexem spacja należy do **następnego** słowa (`␣A` to jeden kawałek). Bez spacji litera
po dwukropku bywa doklejana do interpunkcji (`:A` w GPT-4/4o i DeepSeek). lm-eval koduje całość „kontekst + odpowiedź”
i odcina tokeny kontekstu — kolumna „zgodne” mówi, czy tokeny odpowiedzi w całości są takie same jak odpowiedzi
zakodowanej osobno. „nie” = odpowiedź oceniana jest na innych tokenach, niż się wydaje.

{ans_md}
## Liczby

Ten sam zapis liczby to różne tokeny w różnych modelach (po 3 cyfry, po jednej, w całości). Ma to znaczenie dla testów
matematycznych (GSM8K, MathQA, MATH w Space).

{num_md}
Kawałki rozdziela „│”, tokeny w kawałku „·”. Pełny raport: https://github.com/{args.gh}/blob/main/REGEX.md.
Dane: `results/regex/bench_answer.csv`, `results/regex/bench_numbers.csv` w repo kodu. Data: {today}.
""", encoding="utf-8")

    # NERGAL
    ng_dir = WORK / "publish" / "nergal"
    ng_dir.mkdir(parents=True, exist_ok=True)
    tok_md = "| rodzaj | kategoria | tekst | " + " | ".join(dict.fromkeys(r["label"] for r in ntok)) + " |\n"
    tok_md += "|" + "---|" * (3 + len(dict.fromkeys(r["label"] for r in ntok))) + "\n"
    for key in dict.fromkeys((r["kind"], r["category"], r["text"]) for r in ntok):
        cells = [f"{r['n_tokens']}: `{cell(r['tokens'])}`" for r in ntok if (r["kind"], r["category"], r["text"]) == key]
        tok_md += f"| {key[0]} | {cell(key[1])} | `{cell(key[2])}` | " + " | ".join(cells) + " |\n"
    rules_md = "| linia | nazwa | wzorzec (skrót) | trafia dane osobowe | trafia pułapki (nie PII) |\n|---|---|---|---|---|\n"
    for r in rules:
        patt = r["pattern"] or f"(dynamiczny) {r['dynamic_source']}"
        rules_md += f"| {r['line']} | {cell(r['name'])} | `{cell(patt[:90])}{'…' if len(patt) > 90 else ''}` | " \
                    f"{cell(r['hits_pii']) or '—'} | {cell(r['hits_decoys']) or '—'} |\n"
    risky = [r for r in rules if r.get("hits_decoys")]
    (ng_dir / "REGEXY.md").write_text(agent_text(f"""Tytuł: Regexy i tokeny w NERGAL-u na danych przetargowych — co łapią i gdzie się mylą

Cześć, w ramach pracy domowej o pre-tokenizacji (regexy tokenizerów: co robią i po co) przyjrzałem się też NERGAL-owi:
(1) jak tokenizer NERGAL-a (XLM-RoBERTa) i inne tną dane osobowe, (2) co robią reguły regex z `scrub_pii.py` na
polskich identyfikatorach przetargowych. Kodu nie uruchamiałem — wzorce wyciągnąłem analizą składni pliku.

## 1. Dane osobowe w tokenach

Model BIO decyduje token po tokenie. Numer rozbity na wiele krótkich tokenów (np. ze spacjami) łatwiej zamaskować
częściowo — to pasuje do ograniczenia z karty („spaced numbers may be partly masked”).

{tok_md}
## 2. Reguły `scrub_pii.py` na danych osobowych i na pułapkach przetargowych

Pułapki to identyfikatory z dokumentów przetargowych, które **nie** są danymi osobowymi (CPV, nr ogłoszenia BZP,
znak sprawy, sygnatura KIO, Dz.U., kwota, data, „nr …”). Trafienie pułapki = ryzyko niepotrzebnego zamaskowania.

{rules_md}
{"Wzorce trafiające pułapki: " + ", ".join(r["name"] or ("linia " + r["line"]) for r in risky) + "." if risky else "Żaden stały wzorzec nie trafił pułapek z tej listy."}

<!-- AGENT: poniżej dopisz 3–6 zdań prostym językiem: jakie rodziny reguł są w pliku (telefony, identyfikatory,
     e-maile…), po co każda, i które pułapki są ryzykowne. Tylko na podstawie tabel wyżej. -->

Pełny raport: https://github.com/{args.gh}/blob/main/REGEX.md · dane: https://huggingface.co/datasets/{args.hf}
""", "NERGAL_REGEXY_KOMENTARZ.md"), encoding="utf-8")

    # REGEX.md
    risky_line = (f"Reguły `scrub_pii.py`: {len(rules)} wzorców; trafiające pułapki przetargowe: "
                  f"{', '.join(r['name'] or 'linia ' + r['line'] for r in risky) or 'brak'}.") if rules else ""
    img = lambda n, alt: f"![{alt}](charts/{n})\n" if n in made else ""  # noqa: E731
    report = f"""# Regexy tokenizerów: co robią i po co

Praca domowa 2 (fabryka.ai). Regex z grafiki to pre-tokenizer **GPT-4o (o200k_base)**; obok GPT-2, GPT-4 (cl100k)
i DeepSeek V3. Analiza na tych samych tokenizerach co [praca 1 (tokeny na słowo)](README.md). Data: {today}.

{explain}

---

## Te same przykłady w prawdziwych tokenizerach

Wygenerowane z plików tokenizerów (kawałek │ kawałek, tokeny w kawałku ·). Kolorowa wersja:
[charts/regex_demo.html](charts/regex_demo.html).

{demo}

## Porównanie rodzin pre-tokenizerów

Kolumny z sondami: jak tokenizer tnie dany zapis (kawałki │, tokeny ·).

{fam}
## Pomiar na SIB-200: ile słów to jeden token

{stat_line}

{img('10_regex_slowo_jeden_token.png', 'Słowo = jeden token')}
{st}
### Tokenizery bez regexu

SentencePiece (Bielik v3, Gemma, Llama 2…), ByteLevel bez regexu i wolne tokenizery nie dzielą tekstu na słowa przed
BPE. Do statystyki kawałki przybliżono podziałem po znaczniku spacji (`▁` / `Ġ`), więc „słowo” zawiera tu też
przyklejoną interpunkcję (`␣utrzymują,`) — odsetki nie są wprost porównywalne z tabelą wyżej i nie wchodzą do średniej.
Kimi K2 i Teuken mają tylko wolny tokenizer (bez dostępu do pre-tokenizera) — tu też przybliżenie podziałem po spacjach;
bardzo niski wynik Teukena to artefakt tego przybliżenia (każdy kawałek dostaje dodatkowy token `▁`), nie cecha modelu.

{st_noregex}
{mism_line}

{img('11_regex_vs_tokeny_na_slowo.png', 'Związek z pracą 1')}
## Aster-0.5B obok Slayer1B i Bielików v3

Aster-0.5B (OrisTeam) nie był mierzony w pracy 1 — dodany tylko tutaj (`config/regex_examples.yaml`).

{aster_md}
## Dla Bench Team: litera odpowiedzi i liczby

Spacja należy do następnego słowa, więc „A” i „␣A” to różne tokeny, a „:A” bywa jednym kawałkiem. Tabela dla Slayera
1B i modeli odniesienia: [publish/bench_team/regex/README.md](publish/bench_team/regex/README.md).

## Dla NERGAL-a: dane osobowe w tokenach i reguły regex

Jak tokenizer NERGAL-a tnie PESEL, telefon, IBAN, e-mail, i co reguły `scrub_pii.py` robią z identyfikatorami
przetargowymi. {risky_line} Szczegóły: [publish/nergal/REGEXY.md](publish/nergal/REGEXY.md).

## Kontekst

- **Albert Gu** (współautor Mamby i H-Net): ręcznie pisane regexy są w każdym czołowym LLM i wykonują sporo ciężkiej
  pracy, a mało kto o tym wie; przy GPT-4o przyznaje, że nie wie dokładnie, po co są nowe reguły („coś z wielkimi
  i małymi literami”). Powyższy rozbiór pokazuje, co one robią: dzielą słowa na granicy małe→wielkie (`XMLHttp │ Request`).
  Sam pracuje nad modelami, które uczą się dzielić bajty bez tokenizera (H-Net).
- **Boundless BPE** ([arXiv 2504.00178](https://arxiv.org/abs/2504.00178)): pre-tokenizacja sprawia, że 90–95% kawałków
  to jeden token, a zwroty z kilku słów („of the”) nigdy nie są tokenem. Zdjęcie tej bariery („superwords”) daje do
  15% więcej bajtów na token. Kod: https://github.com/kensho-technologies/boundlessbpe.
- **Peek2** ([arXiv 2601.05833](https://arxiv.org/abs/2601.05833)): implementacja tych samych pre-tokenizerów bez regexów.

## Wnioski

<!-- AGENT: 4–6 zdań prostym językiem, tylko z liczb i przykładów wyżej (zapisz też w report/WNIOSKI_REGEX.md). -->

## Źródła

Regexy z tiktoken (`gpt2`, `cl100k_base`, `o200k_base`) i z plików `tokenizer.json` modeli na Hugging Face; przykłady
podziału sprawdzone dwoma silnikami (Python `regex` i JavaScript). Wpis Alberta Gu na X (2026). Praca 1:
[README.md](README.md). Dane: https://huggingface.co/datasets/{args.hf}.
"""
    (WORK / "REGEX.md").write_text(agent_text(report, "WNIOSKI_REGEX.md"), encoding="utf-8")

    # dane na HF
    hf = WORK / "publish" / "hf"
    if hf.exists():
        (hf / "data").mkdir(exist_ok=True)
        for name in ("catalog.csv", "stats_long.csv", "bench_answer.csv", "bench_numbers.csv", "nergal_tokens.csv", "nergal_rules.csv"):
            if (OUT / name).exists():
                shutil.copy(OUT / name, hf / "data" / f"regex_{name}")
        (hf / "charts").mkdir(exist_ok=True)
        for n in made + ["regex_demo.html"]:
            if (CHARTS / n).exists():
                shutil.copy(CHARTS / n, hf / "charts" / n)
        card = (hf / "README.md").read_text(encoding="utf-8")
        if "## Pre-tokenizacja (praca 2)" not in card:
            card += """
## Pre-tokenizacja (praca 2)

- `data/regex_catalog.csv` — jaki pre-tokenizer (regex / SentencePiece) ma każdy tokenizer i jak tnie sondy
  (liczby, skróty, camelCase, „Answer:A”, „(Łódź”, „ZUS-u”).
- `data/regex_stats_long.csv` — SIB-200: kawałki na słowo, odsetek słów = 1 token, 25 języków.
- `data/regex_bench_*.csv` — litera odpowiedzi i liczby (Bench Team), `data/regex_nergal_*.csv` — dane osobowe w
  tokenach i reguły `scrub_pii.py` NERGAL-a na identyfikatorach przetargowych.
"""
            (hf / "README.md").write_text(card, encoding="utf-8")
    print(f"REGEX.md, publish/bench_team/regex/README.md, publish/nergal/REGEXY.md, wykresy: {made}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hf", default="adegier/tokenizer-fertility-pl")
    ap.add_argument("--gh", default="adgr3/tokenizer-tax-pl")
    build(ap.parse_args(argv))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
