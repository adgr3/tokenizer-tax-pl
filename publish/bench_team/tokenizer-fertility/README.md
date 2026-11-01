# Tokeny na słowo: Slayer 1B i modele odniesienia

Analiza pomocnicza (nie benchmark): ile tokenów na słowo i bajtów UTF-8 na token mają tokenizery Slayera 1B, pięciu
modeli odniesienia i modelu kontrolnego Pythia, po polsku i po angielsku (SIB-200, test; 25 języków w pełnej wersji).

Po co zespołowi:
- porównania liczone na token (np. BLiMP „na token”) zależą od tokenizera — tabela podaje przelicznik;
- udział angielskiego w danych liczony w tokenach różni się między tokenizerami (karta Slayera 1.00: 10% w cl100k,
  17,6% w tokenach Slayera) — tabela pozwala przeliczać;
- obszar „Architecture & Learning”: dane do decyzji o tokenizerze kolejnej wersji (koszt i pojemność kontekstu po polsku).

| model | PL tok./słowo | EN tok./słowo | PL bajtów/token | EN bajtów/token | PL tokenów vs Slayer |
|---|---|---|---|---|---|
| Bielik 1.5B v3 | 1,63 | 2,10 | 4,68 | 2,90 | 0,98 |
| Slayer1B | 1,66 | 1,38 | 4,59 | 4,43 | 1,00 |
| EuroLLM | 1,85 | 1,36 | 4,11 | 4,47 | 1,12 |
| Qwen3.5 | 2,15 | 1,29 | 3,55 | 4,71 | 1,29 |
| LFM3 | 2,28 | 1,24 | 3,34 | 4,91 | 1,37 |
| LFM2.5 | 2,47 | 1,25 | 3,08 | 4,89 | 1,49 |
| Pythia (GPT-NeoX) | 3,13 | 1,28 | 2,43 | 4,76 | 1,89 |

Pełny raport, kalibracja i kod: https://github.com/adgr3/tokenizer-tax-pl. Dane: https://huggingface.co/datasets/adegier/tokenizer-fertility-pl.
Wartości to pomiar deterministyczny (bez losowania pytań); SE podane w `results/fertility_long.csv` to rozrzut między
blokami tekstu.
