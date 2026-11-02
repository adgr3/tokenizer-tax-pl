# Zadanie: praca domowa 2 — regexy tokenizerów: co robią i po co

Pracujesz autonomicznie w repo z pracy 1 (`tokenizer-tax-pl`). Użytkownik jest nietechniczny. Pytasz tylko w sytuacjach
z „Kiedy przerwać i zapytać” oraz raz przed publikacją.

## Cel

Polecenie prowadzącego: „analizować te regexy, aby zrozumieć, co robią i po co”. Grafiki z zadania to pre-tokenizery
GPT-2, **GPT-4o (o200k_base)** i DeepSeek V3; kontekst: wpis Alberta Gu o regexach w LLM i praca Boundless BPE
(arXiv 2504.00178). Ta sama analiza ma dać trzy wyniki:
1. **praca domowa:** `REGEX.md` (rozbiór regexów + przykłady + porównanie rodzin + pomiar na SIB-200);
2. **Bench Team:** `publish/bench_team/regex/README.md` (litera odpowiedzi „A” vs „␣A” — ich zadanie A6 — i liczby);
3. **NERGAL:** `publish/nergal/REGEXY.md` (dane osobowe w tokenach + reguły `scrub_pii.py` na identyfikatorach przetargowych).

Gotowe są: objaśnienie regexów (`docs/REGEX_OBJASNIENIA.md`, przykłady sprawdzone silnikiem JavaScript),
kod (`tt/pretok.py`, `tt/report_regex.py`), przykłady i sondy (`config/regex_examples.yaml`).

**Dodatkowo Aster-0.5B (OrisTeam):** tokenizera nie ma w pracy 1. Jest dopisany w `config/regex_examples.yaml`
(`extra_tokenizers`), a `tokenizers.yaml` się nie zmienia. Plik `tokenizer.json` pobiera się z publicznego repo HF
(bez tokenu). Aster ma być w `catalog`, `stats`, `demo`, `bench` i `nergal`. W raporcie i w podsumowaniu pokaż go
obok Slayer1B i Bielika v3: jaki ma pre-tokenizer i regex, jak tnie liczby, „A” i „␣A” oraz dane osobowe.

## Zasady

- Bez API i bez kosztów — wszystko lokalnie na tokenizerach z pracy 1. GPU niepotrzebne.
- **`scrub_pii.py` NERGAL-a tylko czytamy** (analiza składni `ast`). Nigdy go nie importuj ani nie uruchamiaj.
- Nie zmieniaj wyników pracy 1 (`results/local`, `results/tables`). Nie nadpisuj `config/tokenizers.yaml`.
- Liczby w raportach pochodzą z `results/regex/` (generuje kod). Teksty słowne piszesz tylko w miejscach oznaczonych
  `<!-- AGENT: … -->`, wyłącznie na podstawie tabel.
- Każdą zmianę kodu lub dokumentacji zapisz w `ZMIANY.md`.

## Krok 1 — wgranie łatki

1. Sprawdź, że praca 1 jest zrobiona: `results/local/*.json` istnieją.
2. Pliki z paczki są już na miejscu (`tt/pretok.py`, `tt/report_regex.py`, `docs/`, `config/regex_examples.yaml`,
   `tests/rx_expected.json`) — poza `tt/backends.py`, który leży w `praca2/backends.py`.
3. `tt/backends.py`: sprawdź `git diff`/`git log` tego pliku od pierwszego commitu pracy 1.
   - Jeśli nie był zmieniany → zastąp go plikiem `praca2/backends.py`.
   - Jeśli był → dopisz ręcznie: w klasie `Tok` po obliczeniu `self.fingerprint` linię `self.raw = None`, a w
     `_load_one` w każdej gałęzi przypisz przed `return`: tiktoken → `t.raw = ("tiktoken", enc)`;
     tokenizer_json → `t.raw = ("tokenizers", tok)`; hf → `t.raw = ("tokenizers", tok.backend_tokenizer) if
     getattr(tok, "is_fast", False) else ("slow", tok)`; mock → `t.raw = ("mock", cpt)` (wzór: `praca2/backends.py`).
4. `.venv\Scripts\python -m pip install regex` (zwykle już jest z tiktoken). Dopisz `regex` do `requirements.txt`.
5. `python tests/run_offline_test.py` → `TEST OK` (praca 1 dalej działa).

## Krok 2 — selftest

`python -m tt.pretok selftest` → `SELFTEST OK` i „Regex z grafiki = o200k_base z tiktoken: TAK”.
Selftest porównuje podziały GPT-2 / GPT-4 / GPT-4o w Pythonie (moduł `regex` + wzorce z tiktoken) z podziałami
policzonymi niezależnie w JavaScript (`tests/rx_expected.json`). Różnice → stop i zapytaj (to znaczy, że objaśnienie
może opisywać inne zachowanie niż w rzeczywistości).

## Krok 3 — pomiary

```
python -m tt.pretok catalog     # kto ma jaki pre-tokenizer + sondy
python -m tt.pretok stats       # SIB-200, 25 języków (kilka–kilkanaście minut)
python -m tt.pretok demo
python -m tt.pretok bench
python -m tt.pretok nergal      # pobiera scrub_pii.py (tylko do odczytu)
```

Po `catalog`: sprawdź w `results/regex/catalog.csv`, czy DeepSeek V3 ma 3 kroki jak na grafice (liczby → znaki
chińskie/japońskie → główny regex). Jeśli nie — popraw opis DeepSeek w `docs/REGEX_OBJASNIENIA.md` według rzeczywistego
pliku i zapisz w `ZMIANY.md`.
Tokenizery bez pre-tokenizera (typ SentencePiece, np. Bielik v3, Gemma) nie mają regexu — w `stats` są dzielone po
znaczniku „▁” i oznaczone w kolumnie `approx`. W raporcie podaj je osobno jako „bez regexu”.
Po `stats`: kolumna `mismatch_blocks` powinna być 0 (podział na kawałki odtwarza pełne kodowanie). Jeśli gdzieś nie jest —
opisz w raporcie, którego tokenizera to dotyczy.

## Krok 4 — raporty

```
python -m tt.report --author "adgr3" --hf adegier/tokenizer-fertility-pl --gh adgr3/tokenizer-tax-pl
python -m tt.report_regex --hf adegier/tokenizer-fertility-pl --gh adgr3/tokenizer-tax-pl
```
(`tt.report` odświeża `publish/hf/` z pracy 1; jeśli dopisałeś wcześniej „Co z tego wynika” do `README.md`, przywróć je
z `report/WNIOSKI.md`.)

## Krok 5 — kontrola treści (najważniejsze)

1. Porównaj każdy przykład w `docs/REGEX_OBJASNIENIA.md` z `results/regex/demo.md` i `catalog.csv`. Jeśli coś się nie
   zgadza (np. jak Gemma tnie cyfry, jak Llama 3 i Qwen tną liczby) — popraw tekst objaśnienia i wygeneruj `REGEX.md`
   ponownie. Objaśnienie ma opisywać rzeczywistość, nie założenia.
2. Otwórz `charts/regex_demo.html` i wykresy `charts/10_*.png`, `charts/11_*.png`. Napisy nie mogą na siebie nachodzić.
3. Uzupełnij miejsca `<!-- AGENT: … -->`:
   - `REGEX.md` → „Wnioski” (4–6 zdań, prosto; kopia w `report/WNIOSKI_REGEX.md`);
   - `publish/nergal/REGEXY.md` → 3–6 zdań: jakie rodziny reguł są w `scrub_pii.py`, po co każda, które pułapki
     przetargowe są ryzykowne.
4. Napisz `report/DISCORD_REGEX.md`: 5–7 punktów na kurs + link do `REGEX.md`.

## Krok 6 — publikacja (najpierw zapytaj)

Jedno pytanie: czy wypchnąć zmiany do `adgr3/tokenizer-tax-pl` (gałąź + PR) i potem wgrać `publish/hf/` do `adegier/tokenizer-fertility-pl`?
**ZASADA NR 1: nigdy nic prosto do `main`.** Zawsze nowa gałąź i pull request; scala adgr3.
Po zgodzie:
```
git switch -c praca-2-regexy
git add -A && git status        # sprawdź: bez .env, bez data/
git commit -m "Praca 2: regexy tokenizerów — co robią i po co"
git push -u origin praca-2-regexy
gh pr create --base main --head praca-2-regexy --title "Praca 2: regexy tokenizerów" --body "Opis w REGEX.md"
```
Bez scalania. Wgranie na Hugging Face (`hf upload adegier/tokenizer-fertility-pl publish/hf . --repo-type dataset`)
dopiero, gdy adgr3 scali PR i jeszcze raz potwierdzi.
Bench Team i NERGAL: **nic nie wysyłasz** — pliki czekają w `publish/`.

## Krok 7 — podsumowanie

Maks. 10 linijek: wynik selftestu, ile różnych pre-tokenizerów, odsetek słów = 1 token (EN vs PL, średnio), 2–3
najciekawsze obserwacje, linki. Na końcu treść `report/DISCORD_REGEX.md` i ścieżki do paczek Bench Team i NERGAL.

W podsumowaniu jedna linijka o Asterze (pre-tokenizer, słowo = 1 token PL/EN, ciekawostka z demo).

## Kiedy przerwać i zapytać

- Selftest pokazuje różnice.
- `tt.pretok` nie potrafi wczytać większości tokenizerów.
- Przed publikacją.
