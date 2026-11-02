**Praca domowa 2: regexy tokenizerów — co robią i po co** (64 tokenizery, 22 różne pre-tokenizery, SIB-200, wszystko lokalnie)

- Regex z grafiki to dokładnie pre-tokenizer GPT-4o (`o200k_base` z tiktoken). Rozbiór sprawdziłem dwoma silnikami (Python `regex` i JavaScript), a podziały są zgodne.
- Regex tnie tekst na kawałki, zanim zadziała BPE, i token nigdy nie przekracza granicy kawałka. W tokenizerach z regexem średnio 81% angielskich i tylko 43% polskich słów to jeden token (GPT-4o: 95% wobec 41%).
- Najwięcej polskich słów w jednym tokenie mają tokenizery polskie: polish-gpt2 80%, Aster-0.5B 74%, Slayer1B 67%, i to ze starym regexem GPT-2. Ten wynik daje słownik, a nie regex.
- Liczby: „2026” to jeden kawałek w GPT-2, `202│6` w GPT-4o, Llamie 3 i DeepSeeku, a po jednej cyfrze w Qwen3, Mistralu Nemo, PLLuM 12B, Gemmie i Bielikach v3.
- Nowość w GPT-4o: podział na granicy małych i wielkich liter (`XMLHttp│Request`, `Mc│Donald`). DeepSeek V3 tnie w 3 krokach: liczby → znaki CJK → główny regex. Jego reguła doklejania interpunkcji zna tylko `A-Za-z`, więc `(Lodz` zostaje razem, a `(Łódź` się rozdziela.
- „A” i „␣A” to różne tokeny. W Bielikach v3, EuroLLM, LFM i Qwen3.5 odpowiedź bez spacji jest w kontekście kodowana inaczej niż osobno (ważne dla oceny literami, zadanie A6). W Slayer1B i Asterze kodowanie jest zgodne.
- NERGAL: reguły `scrub_pii.py` sprawdziłem na identyfikatorach przetargowych bez uruchamiania kodu. Kilka z nich trafia też numery, które nie są danymi osobowymi (nr ogłoszenia BZP, „umowa nr …”, data).

Raport: https://github.com/adgr3/tokenizer-tax-pl/blob/main/REGEX.md
