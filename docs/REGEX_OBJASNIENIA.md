## Po co tokenizerowi regex

Tokenizer BPE nie skleja tokenów na całym tekście naraz. Najpierw **regex tnie tekst na kawałki** (pre-tokeny), a
dopiero potem BPE skleja bajty **wewnątrz każdego kawałka**. Token nigdy nie przekracza granicy kawałka. Regex decyduje
więc z góry, co w ogóle *może* stać się jednym tokenem: czy spacja przyklei się do słowa, czy liczba zostanie pocięta,
czy kropka połączy się z następnym słowem.

Albert Gu (współautor Mamby i H-Net) zwrócił uwagę, że takie ręcznie pisane regexy siedzą w każdym czołowym LLM i
„wykonują sporo ciężkiej pracy”, a mało kto o nich wie. Praca *Boundless BPE* (arXiv 2504.00178) pokazuje drugą stronę:
regex sprawia, że 90–95% kawałków to po prostu jeden token (całe słowo), więc częste zwroty z kilku słów nigdy nie
staną się jednym tokenem.

Notacja klas znaków (Unicode): `\p{L}` litera dowolnego alfabetu (`Lu` wielka, `Ll` mała, `Lt` tytułowa, `Lm`
modyfikująca, `Lo` litera bez wielkości — np. chińska, arabska), `\p{M}` znak łączący (akcent doklejany do litery),
`\p{N}` cyfra/liczba, `\p{P}` interpunkcja, `\p{S}` symbol, `\s` biały znak, `(?!\S)` „dalej nie ma znaku niebiałego”,
`(?i:…)` bez rozróżniania wielkości liter. W przykładach `␣` = spacja, `⏎` = nowa linia, `│` = granica kawałka.

---

## GPT-2 (2019; używany w wielu modelach do ok. 2022)

```
's|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+
```

| # | Fragment | Co robi | Po co |
|---|---|---|---|
| 1 | `'s\|'t\|'re\|'ve\|'m\|'ll\|'d` | odcina angielskie końcówki skrótów jako osobne kawałki | „he's” = „he” + „'s”; ten sam token „'s” w tysiącach słów |
| 2 | ` ?\p{L}+` | ciąg liter z opcjonalną spacją z przodu | słowo razem z poprzedzającą spacją = jeden kawałek („␣Gmina”) |
| 3 | ` ?\p{N}+` | ciąg cyfr dowolnej długości, ze spacją | liczby trzymane razem |
| 4 | ` ?[^\s\p{L}\p{N}]+` | ciąg interpunkcji/symboli, ze spacją | „):”, „␣(” |
| 5 | `\s+(?!\S)` | spacje, ale bez ostatniej przed słowem | ostatnia spacja przykleja się do słowa (reguła 2) |
| 6 | `\s+` | pozostałe spacje | koniec tekstu |

Słabości widoczne na przykładach: skróty tylko małymi literami („They'LL” → `␣They │ ' │ LL`), liczby bez limitu
długości (`␣44051401359` — PESEL to jeden kawałek, więc BPE może zbudować dziwne tokeny z długich ciągów cyfr).

## GPT-4 (cl100k_base, 2023; podobny ma Llama 3)

```
'(?i:[sdmt]|ll|ve|re)|[^\r\n\p{L}\p{N}]?+\p{L}+|\p{N}{1,3}| ?[^\s\p{L}\p{N}]++[\r\n]*|\s*[\r\n]|\s+(?!\S)|\s+
```

Zmiany względem GPT-2:
- skróty bez względu na wielkość liter: `'(?i:…)` („They'LL” → `␣They │ 'LL`);
- **przed słowem może stać jeden dowolny znak, który nie jest literą, cyfrą ani nową linią** — nie tylko spacja:
  `(Łódź`, `.kowalski`, `@gmina`, `-mail` to jeden kawałek;
- **cyfry w grupach po maksymalnie 3**: `\p{N}{1,3}` — „2026” → `202 │ 6`, PESEL → `440 │ 514 │ 013 │ 59`, a spacja
  przed liczbą staje się osobnym kawałkiem (`␣ │ 202 │ 6`). Po co: tokenizer ma najwyżej 1110 tokenów-liczb (0–999),
  więc arytmetyka widzi liczby w regularnych kawałkach;
- interpunkcja może zabrać ze sobą nowe linie (`):⏎`), a nowe linie z wcięciem tworzą osobny kawałek — ważne dla kodu.
- `?+` i `++` to kwantyfikatory zaborcze (bez cofania) — przyspieszają dopasowanie, nie zmieniają wyniku na typowym tekście.

Ten sam regex (bez kwantyfikatorów zaborczych) ma **Llama 3.3** — liczby tnie identycznie: `12345678` → `123 │ 456 │ 78`.
**Qwen3** ma prawie ten sam wzorzec, ale zamiast `\p{N}{1,3}` stoi `\p{N}` — każda cyfra to osobny kawałek
(`2026` → `2 │ 0 │ 2 │ 6`, PESEL = 11 tokenów). Po jednej cyfrze tną też Mistral Nemo i PLLuM 12B (regex „Tekken”,
który — jak GPT-4o — dzieli też na granicy wielkości liter: `XMLHttp │ Request`).

## GPT-4o (o200k_base, 2024) — regex z grafiki

```
[^\r\n\p{L}\p{N}]?[\p{Lu}\p{Lt}\p{Lm}\p{Lo}\p{M}]*[\p{Ll}\p{Lm}\p{Lo}\p{M}]+(?i:'s|'t|'re|'ve|'m|'ll|'d)?
|[^\r\n\p{L}\p{N}]?[\p{Lu}\p{Lt}\p{Lm}\p{Lo}\p{M}]+[\p{Ll}\p{Lm}\p{Lo}\p{M}]*(?i:'s|'t|'re|'ve|'m|'ll|'d)?
|\p{N}{1,3}| ?[^\s\p{L}\p{N}]+[\r\n/]*|\s*[\r\n]+|\s+(?!\S)|\s+
```

| # | Fragment | Co robi | Przykład |
|---|---|---|---|
| 1 | jeden znak-nie-litera? + **wielkie\*** + **małe+** + skrót? | słowo pisane „normalnie” (małe albo Wielka+małe); skrót angielski **doklejony** do słowa | `He's`, `␣Gmina`, `␣Łomianki`, `␣PESELu` |
| 2 | jeden znak-nie-litera? + **wielkie+** + **małe\*** + skrót? | słowo z samych wielkich liter albo zaczynające się ich ciągiem | `␣ZUS`, `PESEL`, `␣They'LL` |
| 3 | `\p{N}{1,3}` | cyfry po maks. 3, jak w GPT-4 | `202 │ 6` |
| 4 | ` ?[^\s\p{L}\p{N}]+[\r\n/]*` | interpunkcja/symbole; może zabrać nowe linie **i ukośniki** | `):⏎`, `␣„`, `://` |
| 5 | `\s*[\r\n]+` | nowe linie (z poprzedzającymi spacjami) | |
| 6 | `\s+(?!\S)` | spacje bez ostatniej przed słowem | wcięcia w kodzie |
| 7 | `\s+` | pozostałe spacje | |

Co nowego (to, czego Albert Gu „nie rozumie”): **granica wielkości liter**. Słowo kończy się tam, gdzie po małych
literach zaczyna się wielka: `XMLHttpRequest` → `␣XMLHttp │ Request`, `McDonald` → `␣Mc │ Donald`. To dzieli
nazwy z kodu (camelCase) i nazwiska na części, które częściej występują osobno. Skróty angielskie są teraz *częścią*
słowa (`He's` jeden kawałek), a klasy `Lm`, `Lo`, `M` są w obu grupach, więc pisma bez wielkich liter (chiński,
arabski) i akcenty łączące działają w obu gałęziach.

Dla polskiego: `PESELu` zostaje jednym kawałkiem (wielkie, potem małe), ale `ZUS-u` → `␣ZUS │ -u`, a `ZP.271.12.2026`
→ `␣ZP │ . │ 271 │ . │ 12 │ . │ 202 │ 6`.

## DeepSeek V3 (2024) — regex z grafiki (trzy kroki po kolei)

```
krok 1: \p{N}{1,3}
krok 2: [一-龥぀-ゟ゠-ヿ]+
krok 3: [!"#$%&'()*+,\-./:;<=>?@\[\\\]^_`{|}~][A-Za-z]+|[^\r\n\p{L}\p{P}\p{S}]?[\p{L}\p{M}]+| ?[\p{P}\p{S}]+[\r\n]*|\s*[\r\n]+|\s+(?!\S)|\s+
```

Tekst jest cięty **etapami**: najpierw odcinane są liczby (po maks. 3 cyfry), potem ciągi znaków chińskich
i japońskich (hiragana, katakana) — każdy taki ciąg to osobny kawałek — a dopiero resztę tnie regex z kroku 3:

| # | Fragment | Co robi | Przykład |
|---|---|---|---|
| 1 | jeden znak ASCII interpunkcji + `[A-Za-z]+` | doklejenie interpunkcji **tylko do słów z liter łacińskich bez ogonków** | `(x`, `.kowalski`, `@gmina`, `-mail`, `:A` |
| 2 | znak-nie-litera-nie-interpunkcja? + litery i akcenty | zwykłe słowo, zwykle ze spacją | `␣Gmina`, `Łódź` |
| 3 | ` ?[\p{P}\p{S}]+[\r\n]*` | interpunkcja/symbole, ze spacją i nowymi liniami | `␣(`, `):⏎` |
| 4–6 | jak w GPT-4 | nowe linie i spacje | |

Ciekawostka dla polskiego: reguła 1 zna tylko `A-Za-z`, więc `(Lodz` (bez ogonków, bez spacji przed nawiasem) to
jeden kawałek, a `(Łódź` zawsze dzieli się na `( │ Łódź`. To samo dotyczy `.Żółw` w adresach i e-mailach. Brak reguły skrótów angielskich (`He │ 's`). Chiński i japoński mają osobny
etap, bo DeepSeek trenowano w dużej części na tekstach chińskich.

## Tokenizery bez regexu (SentencePiece)

Gemma, Llama 2, Bielik v3, XLM-RoBERTa (NERGAL), część polskich modeli używają **SentencePiece**: spacja zamieniana
jest na znak `▁` doklejany do początku słowa. Nie ma tu regexu tnącego tekst na kawałki — cały tekst trafia do modelu
BPE/Unigram i to on decyduje o podziale (cyfry pojedynczo w Gemmie, Bielikach v3 i Llamie 2: `2·0·2·6`). Gemma ma
formalnie pre-tokenizer `Split(" ")`, ale normalizator wcześniej zamienia każdą spację na `▁`, więc ten podział nic nie
robi. Wyjątek: XLM-RoBERTa (NERGAL) dzieli tekst po białych znakach (`WhitespaceSplit`) — kawałkiem jest całe „słowo”
razem z interpunkcją (`␣Answer:` , `␣ZP.271.12.2026`). Analiza poniżej pokazuje ich zachowanie na tych samych przykładach.

## Co z tego wynika — wspólne obserwacje

1. **Spacja należy do następnego słowa** we wszystkich wersjach (`␣Gmina`). Dlatego „A” i „␣A” to różne tokeny — ma
   to znaczenie przy ocenie odpowiedzi literami w benchmarkach.
2. **Liczby:** GPT-2 trzyma liczbę w jednym kawałku (BPE tnie ją potem dowolnie: `␣4·405·14·01·359`),
   GPT-4/4o/Llama 3/DeepSeek tną po 3 cyfry od lewej, Qwen3 i Mistral Nemo/PLLuM 12B — regexem po jednej cyfrze,
   SentencePiece (Gemma, Bielik v3, Llama 2) też po jednej cyfrze. Ta sama liczba to więc zupełnie inne tokeny w
   różnych modelach.
3. **Interpunkcja przed słowem:** od GPT-4 jeden znak (`.`, `@`, `-`, `(`) może się dokleić do słowa — wygodne dla
   e-maili i kodu, ale `.kowalski` i `␣kowalski` to różne kawałki.
4. **Reguły są pisane pod angielski** (skróty `'s`, `'ll`); dla polskiego nie ma odpowiedników (np. „-u”, „-owi” przy
   skrótowcach), więc `ZUS-u` zawsze się rozpada: `␣ZUS │ -u` (GPT-4 i nowsze) albo `␣ZUS │ - │ u` (GPT-2).
