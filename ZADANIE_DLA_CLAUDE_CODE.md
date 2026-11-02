# Zadanie: ile tokenów na jedno słowo — replikacja dla polskich modeli i analiza w agregacie

Pracujesz autonomicznie na laptopie użytkownika (Windows). Użytkownik jest nietechniczny i chce klikać jak najmniej.
Pytaj go tylko w sytuacjach z sekcji „Kiedy przerwać i zapytać” oraz raz przed publikacją (krok 12).

## Cel

Praca domowa z kursu fabryka.ai. Prowadzący poprosił:
1. „o replikację tego dla polskich modeli, np. PLLuM / Bielik czy Slayer1B” (wykres z pracy arXiv 2605.24718:
   tokeny na słowo, 25 języków, 6 tokenizerów);
2. „o więcej tokenizerów i analizę ich w agregacie vs języki, aby wyciągnąć coś więcej”.

Ten sam pomiar daje też tabele dla zespołu Bench Team (Slayer 1B i modele odniesienia) i dla NERGAL-a (enkodery).
Kod jest gotowy w `tt/`. Twoja praca: środowisko, weryfikacja listy tokenizerów, uruchomienie kroków, kontrola wyników,
publikacja po zgodzie.

## Zasady

- **GPU niepotrzebne.** Liczenie tokenów działa na CPU. Pobierasz **tylko tokenizery** (kod robi to sam), nigdy wag modeli.
- **Budżet API:**
  - AIHubMix: tylko modele z ceną **wejścia ≤ 0,20 USD za 1 mln tokenów** (darmowe też). Bezpiecznik łączny
    `AIHUBMIX_MAX_SPEND_USD` w `.env` (domyślnie 1,00 USD). Na koncie jest 8,56 USD.
  - OpenRouter: **tylko darmowe** modele, których nie ma w AIHubMix. Limit 50 darmowych zapytań na dzień — co nie
    zmieści się dziś, dokończ kolejnego dnia (skrypt sam pilnuje i wznawia).
- Klucze tylko w pliku `.env` (wzór `.env.example`). Nigdy nie wypisuj ich w czacie, logach ani w repo.
- Nie zmieniaj logiki pomiaru (`tt/common.py`: bloki, definicja słowa, średnia po blokach). Wolno poprawić błąd, który
  blokuje uruchomienie — każdą zmianę zapisz w `ZMIANY.md` (co, dlaczego).
- **Długie kroki uruchamiaj do końca.** Jeśli puszczasz coś w tle, sprawdzaj postęp i nie kończ odpowiedzi, dopóki
  krok się nie skończy. Wszystkie kroki są wznawialne (pomijają to, co już policzone).
- Liczby w raporcie pochodzą wyłącznie z `results/` (generuje je `tt.report`). Nie wpisuj liczb ręcznie.
- Ustaw `PYTHONUTF8=1` w sesji (polskie znaki na Windows).

## Krok 1 — środowisko

```
py -3.12 -m venv .venv          (albo inny Python ≥ 3.11)
.venv\Scripts\python -m pip install -r requirements.txt
```
Dalej `python` = `.venv\Scripts\python`. Sprawdź logowanie do Hugging Face: `.venv\Scripts\hf auth whoami`.
Brak logowania nie blokuje (większość tokenizerów jest publiczna); repo za bramką zgody zastępujesz kopiami z pola `alt`.

## Krok 2 — test bez sieci

`python tests/run_offline_test.py` → musi wypisać `TEST OK`. Jeśli nie — popraw środowisko, nie kod pomiaru.

## Krok 3 — dane i lista tokenizerów

1. `python -m tt.data` → 25 języków po 204 zdania (komunikat „!” przy innej liczbie = stop i sprawdź).
2. Zweryfikuj `config/tokenizers.yaml`: dla każdego wpisu sprawdź, czy repo istnieje i ma tokenizer
   (`huggingface_hub.HfApi().model_info`). Złe nazwy popraw (wyszukaj na HF). Repo za bramką zgody → kopie z `alt`
   albo inne niebramkowane kopie tego samego modelu (np. `unsloth/…`); zapisz w `ZMIANY.md`, skąd wziąłeś tokenizer.
3. **Polskie tokenizery — wszystkie, jakie się da:** sprawdź zawartość zbioru `SlayerLab/tokenizers` (repo typu dataset)
   i dopisz każdy tokenizer (`kind: tokenizer_json`, `repo_type: dataset`, `file: <ścieżka>`, `group: pl`).
   Poszukaj też innych polskich LLM na HF (PLLuM w nowszych wersjach, Bielik v3 w innych rozmiarach, modele SlayerLab,
   Qra) i dopisz te z własnym tokenizerem.
4. **Brakujące tokenizery z pracy arXiv 2605.24718** (oprócz 6 z wykresu praca mierzyła też Mistral Large 3,
   Nemotron Super 3 i Amazon Nova Pro): dopisz Mistral Large 3 i Nemotron Super 3, jeśli ich tokenizery są publiczne na
   HF (`group: global`, w `label` dopisek „(z pracy)”). Nova Pro ma cenę wejścia powyżej 0,20 USD — nie mierz jej; jeśli
   zmierzysz tańszy model Nova (Micro/Lite) przez API, zaznacz w `note`, że to przybliżenie tokenizera Nova Pro.
5. Możesz dopisać kolejne rodziny globalne/europejskie z **własnym** tokenizerem (najnowsza generacja rodziny).
   Łącznie maksymalnie ok. 60 wpisów. Duplikaty nie szkodzą — analiza sama scala ten sam tokenizer.

## Krok 4 — pomiar lokalny

`python -m tt.measure_local` (kilka–kilkanaście minut). Potem przejrzyj `results/skipped.json`: co się da, popraw
(nazwa repo, `trust_remote_code: true`, kopia z `alt`) i uruchom ponownie z `--only <id>`. Czego się nie da — zostaw;
trafi do raportu z powodem.

## Krok 5 — kalibracja

`python -m tt.calibrate` → musi być **ZALICZONA** (średnia różnica ≤ 0,02, maks. ≤ 0,08; autor wykresu z kursu miał
0,007 / 0,049). Jeśli nie — stop, opisz wynik (który tokenizer i język odstaje) i zapytaj.

## Krok 6 — modele przez API

1. Utwórz `.env` z `.env.example`. Jeśli brakuje kluczy, poproś użytkownika, żeby **sam** wpisał je do pliku `.env`
   (podaj ścieżkę); nie proś o wklejenie klucza do czatu.
2. `python -m tt.subsample` (ile bloków na język wystarczy).
3. `python -m tt.api_models` → `results/api_catalog/kandydaci.csv`. Jeśli AIHubMix nie podaje cen w API, sprawdź
   cennik na stronie AIHubMix.
4. Wpisz wybrane modele do `config/api_models.yaml` według reguł:
   - AIHubMix: cena wejścia ≤ 0,20 USD/1 mln tokenów; OpenRouter: tylko darmowe i nieobecne w AIHubMix;
   - mierzymy rodziny z **niepublicznym** tokenizerem (np. Gemini, Amazon Nova, Grok, ERNIE, Doubao, Hunyuan, Reka,
     Jamba — co jest dostępne); jeden model na rodzinę/generację;
   - modeli z publicznym tokenizerem (Llama, Qwen, Mistral open, DeepSeek, Gemma, GPT/tiktoken…) przez API nie
     mierzymy — **wyjątek:** 1 model kontrolny w AIHubMix i 1 w OpenRouter z tokenizerem policzonym lokalnie
     (pole `note: "kontrola: …"`). Analiza sprawdzi, czy liczby z API pokrywają się z lokalnymi;
   - modele „decyzyjne” (np. Jev) tylko jeśli działają przez zwykłe `chat/completions`.
5. `python -m tt.measure_api --dry-run` (szacunek), potem `python -m tt.measure_api`.

## Krok 7 — polski na różnych rodzajach tekstu

1. Obejrzyj strukturę `SlayerLab/polish-dynaword` (strumieniowo, kilka wierszy): nazwę kolumny tekstu, kolumny źródła
   i listę wartości źródła.
2. Uzupełnij `config/polish_sources.yaml`: ok. 11 źródeł, m.in. Dziennik Ustaw, Wikipedia, Wolne Lektury, stenogramy
   Sejmu (jak u autora wykresu) + inne różnorodne (prasa, fora, administracja).
3. `python -m tt.polish --sample`, potem `python -m tt.polish`. Tekstów nie publikujemy (zostają w `data/`).

## Krok 8 — analiza, wykresy, raport

```
python -m tt.analyze
python -m tt.charts
python -m tt.report --author "adgr3" --hf adegier/tokenizer-fertility-pl --gh adgr3/tokenizer-tax-pl
```

## Krok 9 — kontrola

- Obejrzyj każdy wykres w `charts/` (otwórz plik PNG). Napisy nie mogą na siebie nachodzić; jeśli kolumn jest dużo,
  popraw wymiary w `tt/charts.py` (to nie zmienia pomiaru) i wygeneruj ponownie.
- Przeczytaj `README.md`. Sprawdź 3 liczby losowo względem `results/tables/*.csv`.
- Kontrole z API: model kontrolny powinien wyjść jako alias tokenizera lokalnego (sekcja „Aliasy”). Jeśli nie — opisz
  różnicę w `ZMIANY.md` i w raporcie (to informacja o dostawcy).

## Krok 10 — wnioski słowne

Pod sekcją „Najważniejsze wnioski” w `README.md` dopisz krótki akapit „Co z tego wynika” (3–5 zdań, prostym językiem),
**wyłącznie na podstawie liczb z raportu**: co znaczy wynik dla polskiego, dla wyboru modelu do polskich zastosowań,
dla kosztu API. Zaznacz, że to wnioski autora, nie pomiar. Ten akapit przepada przy ponownym `tt.report` — zapisz go też
w `report/WNIOSKI.md`.

## Krok 11 — paczki dla Bench Team i NERGAL

Nic nie wysyłasz. Sprawdź, że są trzy osobne wyniki:
- praca domowa: `README.md` (pełny raport) + `report/DISCORD.md`;
- Bench Team: `publish/bench_team/tokenizer-fertility/` (README z tabelą, RECIPE, wyniki);
- NERGAL: `publish/nergal/KOMENTARZ.md` (gotowy wpis do zakładki Community przy modelu).

## Krok 12 — publikacja (najpierw zapytaj)

Zadaj użytkownikowi **jedno** pytanie z listą: czy publikujesz
- GitHub: publiczne repo `adgr3/tokenizer-tax-pl` (cały folder; `.gitignore` wyklucza `data/`, `.env`, `.venv`);
- Hugging Face: zbiór `adegier/tokenizer-fertility-pl` (zawartość `publish/hf/`).

Po zgodzie:
```
git init && git add . && git commit -m "Tokenizer tax: replikacja dla polskich modeli + agregat"
gh repo create adgr3/tokenizer-tax-pl --public --source . --push
hf repo create adegier/tokenizer-fertility-pl --repo-type dataset
hf upload adegier/tokenizer-fertility-pl publish/hf . --repo-type dataset
```
Przed `git add` sprawdź `git status`: żadnego `.env`, żadnych tekstów z `data/`. Do Hugging Face potrzebny jest token
z prawem zapisu — jeśli go nie ma, poproś użytkownika o `hf auth login` (sam wpisuje token).

**Bench Team: bez PR.** Użytkownik najpierw zapyta na Discordzie #bench-team, czy chcą tę analizę u siebie.

## Krok 13 — podsumowanie dla użytkownika

W czacie maks. 10 linijek: ile tokenizerów (unikalnych), wynik kalibracji, 3 najciekawsze wnioski, wydatek API, linki
(GitHub, HF), lista pominiętych. Na końcu wklej treść `report/DISCORD.md` (gotowa wiadomość na kurs) i podaj ścieżki
do paczek dla Bench Team i NERGAL-a.

## Kiedy przerwać i zapytać

- Kalibracja niezaliczona.
- Nie da się pobrać SIB-200.
- Brak kluczy API w `.env` (poproś o wpisanie do pliku, nie do czatu).
- Szacunek kosztu przekracza bezpiecznik.
- Przed publikacją (krok 12).

W każdym przypadku jeden akapit: co się stało, co już działa, czego potrzebujesz.
