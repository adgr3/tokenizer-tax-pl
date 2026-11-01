# Zmiany względem paczki startowej

Logika pomiaru (`tt/common.py`: bloki ok. 6000 znaków, słowo = podział po białych znakach, średnia po blokach)
nie była zmieniana.

## Środowisko

- `requirements.txt`: dopisany `scipy` — pandas potrzebuje go do korelacji Spearmana w `tt.analyze`
  (bez niego test offline kończył się błędem).
- Doinstalowany `torch` (wersja CPU) — wymaga go kod tokenizera Teuken (`gptx_tokenizer.py`, `trust_remote_code`).
  Nie ma go w `requirements.txt`, bo jest potrzebny tylko dla jednego tokenizera:
  `pip install torch --index-url https://download.pytorch.org/whl/cpu`.

## Kod (tylko ładowanie tokenizerów i pobieranie próbek)

- `tt/backends.py`
  - `kind: tokenizer_json` z polem `row`: tokenizer czytany z wiersza pliku parquet (kolumna `tokenizer_json`,
    wiersz wybierany po `source_path`). Powód: zbiór `SlayerLab/tokenizers` przechowuje tokenizery warsztatowe
    w `data/train-00000-of-00001.parquet`, nie jako osobne pliki (osobno leży tylko `GollemTokenizer/49152/tokenizer.json`).
  - Przypięta `revision` dotyczy tylko repo głównego; kopie z `alt` ładowane są bez niej (inne repo = inna historia
    commitów, więc z przypiętą rewizją kopie nigdy by nie zadziałały).
  - Do listy pobieranych plików dopisany wzorzec `*_tokenizer.py` (Teuken ma `gptx_tokenizer.py`).
- `tt/polish.py --sample`: źródło z polem `data_files` czytane jest strumieniowo z własnego pliku parquet.
  Powód: `SlayerLab/polish-dynaword` ma osobny plik na źródło (`data/<źródło>/<źródło>.parquet`), a strumień całości
  idzie źródło po źródle — przy limicie 400 tys. wierszy nie doszedłby dalej niż do pierwszych katalogów.
  Próbka to pierwsze dokumenty każdego źródła (do 120 tys. znaków, maks. 20 tys. znaków z dokumentu).

## Lista tokenizerów (`config/tokenizers.yaml`)

Każde repo sprawdzone przez API Hugging Face (istnieje, ma pliki tokenizera, bramka zgody). Brak logowania do HF,
więc repo za bramką zastąpione kopiami:

| wpis | repo oryginalne | skąd tokenizer |
|---|---|---|
| llama4_maverick, llama33, gemma2, gemma3 | meta-llama/…, google/… (bramka) | kopie `unsloth/…` (już w `alt`) |
| bielik_11b_v3 | speakleash/Bielik-11B-v3.0-Instruct (bramka) | `speakleash/Bielik-11B-v3.0-Instruct-FP8-Dynamic` (oficjalna kwantyzacja, ten sam tokenizer) |
| bielik_4_5b_v3 | speakleash/Bielik-4.5B-v3.0-Instruct (bramka) | `speakleash/Bielik-4.5B-v3.0-Instruct-FP8-Dynamic` |
| bielik_1_5b_v3 | speakleash/Bielik-1.5B-v3 @4b25049 (bramka) | `cpral/Bielik-1.5B-v3-ungated` (kopia modelu bazowego) |
| bielik_minitron_7b | speakleash/Bielik-Minitron-7B-v3.0-Instruct (bramka) | `…-FP8-Dynamic` |

Poprawione nazwy:
- `CYFRAGOVPL/PLLuM-4B-instruct` nie istnieje → `CYFRAGOVPL/PLLuM-4B-instruct-2512`.
- PLLuM 12B i Llama-PLLuM 8B → najnowsze wydania `-2512` (stare nazwy zostały w `alt`).
- Usunięty `NousResearch/Llama-3.3-70B-Instruct` z `alt` (repo nie istnieje).

Dopisane:
- polskie modele: Bielik-PL 11B v3 (pominięty — tylko za bramką, brak kopii), Bielik Minitron 7B v3, PLLuM 8x7B,
  APT3 1B (Azurro), GoLLeM v6 250M, Slayer149;
- ze zbioru `SlayerLab/tokenizers` (39 artefaktów, z czego 14 wczytuje się bez konwersji; reszta to własne formaty
  warsztatowe wymagające adapterów): kanoniczny Polish BPE 32k, GollemTokenizer 49k oraz po jednym z każdego autora
  warsztatu (dawidm ×2 — dwa różne korpusy, Janek, KasiaMP, Konrad). Pozostałe 7 wczytywalnych to warianty tych samych
  autorów (inne rozmiary słownika/normalizacja) — pominięte, żeby lista nie przekroczyła ok. 60 wpisów;
- z pracy arXiv 2605.24718: Mistral Large 3, Nemotron Super 3 (oba publiczne na HF);
- inne rodziny (najnowsza generacja): gpt-oss, Cohere Command A (kopia `unsloth/`), AI21 Jamba2, Granite 4, OLMo 3.

## Uwagi z pomiaru

- **Gemma 2 w kalibracji** odstaje najbardziej (średnio +0,048 tok./słowo, we wszystkich 25 językach w tę samą stronę;
  pozostałe 5 tokenizerów ≤ 0,008). Najpewniej przyczyną jest łączenie zdań znakiem nowej linii w blokach: tokenizer
  SentencePiece Gemmy koduje słowo po `\n` bez prefiksu `▁`, czyli na więcej tokenów. Metody nie zmieniono
  (jest zgodna z autorem wykresu z kursu), kalibracja i tak ZALICZONA.
- **Ostrzeżenie transformers o regexie Mistrala** (`fix_mistral_regex=True`): sprawdzone na Mistral Nemo — wynik
  identyczny z poprawką i bez (EN, PL, DE, UK do 4 miejsc), więc pomiar bez zmian.
- Ten sam „odcisk” to identyczne identyfikatory **i** rozmiar słownika. Tokenizery, które kodują tekst identycznie,
  ale mają inną liczbę tokenów specjalnych (np. cl100k / Phi-4 / Granite 4 / OLMo 2–3, Gemma 3 / Gemma 4 / PLLuM 4B),
  liczą się jako osobne kolumny w agregatach. Nie zmieniałem tej reguły.

## Pomiar przez API

- Zmienna środowiskowa Windows (użytkownika) `AIHUBMIX_API_KEY` ze starym kluczem nadpisywała `.env`
  (`load_env` używa `setdefault`) — stąd HTTP 401. Skrypty API uruchamiane z usuniętą zmienną
  (`env -u AIHUBMIX_API_KEY …`), więc klucz pochodzi z `.env`. Logi z pierwszej próby (zawierały fragment starego
  klucza zwrócony przez serwer) usunięte.
- AIHubMix nie podaje cen w `/v1/models` (OpenAI-zgodnym); ceny wzięte z `https://aihubmix.com/api/v1/models`
  (zapis: `results/api_catalog/aihubmix_v1_models.json`).
- Kontrola AIHubMix: GPT-4.1 nano = alias lokalnego o200k (`gpt4o`) — liczby z API zgodne z lokalnymi.
  Kontrola OpenRouter: niezmierzona (darmowe Gemma 4 i LFM2.5 przeciążone u dostawców, HTTP 429).
- Doubao Seed 2.0 Mini ignoruje `max_tokens=1` (ok. 1800 tokenów odpowiedzi na zapytanie); koszt wyjścia jest liczony
  przez skrypt, cały model ok. 0,07 USD. Łącznie AIHubMix: 0,29 USD.
- Niezmierzone modele i powody: `report/WNIOSKI.md` (sekcja „Modele przez API, których nie zmierzono”).
- `config/api_models.yaml`: ERNIE X1 Turbo zamieniony na ERNIE 4.5 Turbo (oba niedostępne), Inkling usunięty
  (HTTP 403, tylko aplikacje agentowe), kontrola OpenRouter zmieniona z Gemma 4 na LFM2.5.

## Wykresy (`tt/charts.py`, bez wpływu na pomiar)

- 06 (słownik vs polski): większy rysunek, jeden podpis dla punktów w tym samym miejscu, prosty algorytm rozsuwania
  podpisów z liniami do punktów (wcześniej podpisy nachodziły na siebie).
- 08 (rodzaje tekstu): paleta `tab20` (13 serii; wcześniej kolory się powtarzały), SIB-200 na czarno, legenda nad
  słupkami.
