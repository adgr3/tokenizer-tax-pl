# Pre-tokenizacja a ocena odpowiedzi i liczb: Slayer 1B i modele odniesienia

Analiza pomocnicza do zadania **A6** („litera odpowiedzi ze spacją i bez”) i do testów z liczbami.

## Dlaczego „A” i „␣A” to różne tokeny

We wszystkich tokenizerach z regexem spacja należy do **następnego** słowa (`␣A` to jeden kawałek). Bez spacji litera
po dwukropku bywa doklejana do interpunkcji (`:A` w GPT-4/4o i DeepSeek). lm-eval koduje całość „kontekst + odpowiedź”
i odcina tokeny kontekstu — kolumna „zgodne” mówi, czy tokeny odpowiedzi w całości są takie same jak odpowiedzi
zakodowanej osobno. „nie” = odpowiedź oceniana jest na innych tokenach, niż się wydaje.

| model | kontekst + odpowiedź | tokeny całości | odpowiedź osobno | odpowiedź w całości | zgodne |
|---|---|---|---|---|---|
| Aster-0.5B (OrisTeam) | `Answer:` + `␣A` | `A · ns · wer · : · ␣A` | `␣A` | `␣A` | tak |
| Aster-0.5B (OrisTeam) | `Answer:` + `A` | `A · ns · wer · : · A` | `A` | `A` | tak |
| Aster-0.5B (OrisTeam) | `Odpowiedź:` + `␣A` | `Odpowie · dź · : · ␣A` | `␣A` | `␣A` | tak |
| Aster-0.5B (OrisTeam) | `Question?⏎` + `A` | `Q · ue · stion · ? · ⏎ · A` | `A` | `A` | tak |
| Aster-0.5B (OrisTeam) | `(` + `A)` | `( · A · )` | `A · )` | `A · )` | tak |
| Bielik 1.5B v3 | `Answer:` + `␣A` | `␣A · ns · wer · : · ␣A` | `␣A` | `␣A` | tak |
| Bielik 1.5B v3 | `Answer:` + `A` | `␣A · ns · wer · : · A` | `␣A` | `A` | **nie** |
| Bielik 1.5B v3 | `Odpowiedź:` + `␣A` | `␣Odpowiedź · : · ␣A` | `␣A` | `␣A` | tak |
| Bielik 1.5B v3 | `Question?⏎` + `A` | `␣Que · sti · on · ? · <0x0A> · A` | `␣A` | `A` | **nie** |
| Bielik 1.5B v3 | `(` + `A)` | `␣( · A · )` | `␣A · )` | `A · )` | **nie** |
| EuroLLM | `Answer:` + `␣A` | `␣Ans · wer · : · ␣A` | `␣A` | `␣A` | tak |
| EuroLLM | `Answer:` + `A` | `␣Ans · wer · : · A` | `␣A` | `A` | **nie** |
| EuroLLM | `Odpowiedź:` + `␣A` | `␣Odpowied · ź · : · ␣A` | `␣A` | `␣A` | tak |
| EuroLLM | `Question?⏎` + `A` | `␣Question · ? · <0x0A> · A` | `␣A` | `A` | **nie** |
| EuroLLM | `(` + `A)` | `␣( · A · )` | `␣A · )` | `A · )` | **nie** |
| LFM2.5 | `Answer:` + `␣A` | `Answer · : · ␣A` | `␣A` | `␣A` | tak |
| LFM2.5 | `Answer:` + `A` | `Answer · :A` | `A` | `—` | **nie** |
| LFM2.5 | `Odpowiedź:` + `␣A` | `Od · pow · ied · ź · : · ␣A` | `␣A` | `␣A` | tak |
| LFM2.5 | `Question?⏎` + `A` | `Question · ?⏎ · A` | `A` | `A` | tak |
| LFM2.5 | `(` + `A)` | `(A · )` | `A · )` | `—` | **nie** |
| LFM3 | `Answer:` + `␣A` | `Answer · : · ␣A` | `␣A` | `␣A` | tak |
| LFM3 | `Answer:` + `A` | `Answer · :A` | `A` | `—` | **nie** |
| LFM3 | `Odpowiedź:` + `␣A` | `Od · pow · ied · ź · : · ␣A` | `␣A` | `␣A` | tak |
| LFM3 | `Question?⏎` + `A` | `Question · ?⏎ · A` | `A` | `A` | tak |
| LFM3 | `(` + `A)` | `(A · )` | `A · )` | `—` | **nie** |
| Pythia (GPT-NeoX) | `Answer:` + `␣A` | `Answer · : · ␣A` | `␣A` | `␣A` | tak |
| Pythia (GPT-NeoX) | `Answer:` + `A` | `Answer · : · A` | `A` | `A` | tak |
| Pythia (GPT-NeoX) | `Odpowiedź:` + `␣A` | `O · dp · ow · ied · � · � · : · ␣A` | `␣A` | `␣A` | tak |
| Pythia (GPT-NeoX) | `Question?⏎` + `A` | `Question · ? · ⏎ · A` | `A` | `A` | tak |
| Pythia (GPT-NeoX) | `(` + `A)` | `( · A · )` | `A · )` | `A · )` | tak |
| Qwen3.5 | `Answer:` + `␣A` | `Answer · : · ␣A` | `␣A` | `␣A` | tak |
| Qwen3.5 | `Answer:` + `A` | `Answer · :A` | `A` | `—` | **nie** |
| Qwen3.5 | `Odpowiedź:` + `␣A` | `O · dp · owied · ź · : · ␣A` | `␣A` | `␣A` | tak |
| Qwen3.5 | `Question?⏎` + `A` | `Question · ? · ⏎ · A` | `A` | `A` | tak |
| Qwen3.5 | `(` + `A)` | `(A · )` | `A · )` | `—` | **nie** |
| Slayer1B | `Answer:` + `␣A` | `Answer · : · ␣A` | `␣A` | `␣A` | tak |
| Slayer1B | `Answer:` + `A` | `Answer · : · A` | `A` | `A` | tak |
| Slayer1B | `Odpowiedź:` + `␣A` | `Odpowie · dź · : · ␣A` | `␣A` | `␣A` | tak |
| Slayer1B | `Question?⏎` + `A` | `Question · ? · ⏎ · A` | `A` | `A` | tak |
| Slayer1B | `(` + `A)` | `( · A · )` | `A · )` | `A · )` | tak |

## Liczby

Ten sam zapis liczby to różne tokeny w różnych modelach (po 3 cyfry, po jednej, w całości). Ma to znaczenie dla testów
matematycznych (GSM8K, MathQA, MATH w Space).

| model | `7` | `42` | `2026` | `12345678` | `3.14159` | `1 000 000` | `1,000,000` | `2026-11-01` | `-17` | `0.5` |
|---|---|---|---|---|---|---|---|---|---|---|
| Aster-0.5B (OrisTeam) | `7` | `42` | `20 · 26` | `123 · 45 · 6 · 78` | `3 · . · 14 · 159` | `1 · ␣000 · ␣000` | `1 · , · 000 · , · 000` | `20 · 26 · - · 11 · - · 01` | `- · 17` | `0 · . · 5` |
| Bielik 1.5B v3 | `␣ · 7` | `␣ · 4 · 2` | `␣ · 2 · 0 · 2 · 6` | `␣ · 1 · 2 · 3 · 4 · 5 · 6 · 7 · 8` | `␣ · 3 · . · 1 · 4 · 1 · 5 · 9` | `␣ · 1 · ␣ · 0 · 0 · 0 · ␣ · 0 · 0 · 0` | `␣ · 1 · , · 0 · 0 · 0 · , · 0 · 0 · 0` | `␣ · 2 · 0 · 2 · 6 · - · 1 · 1 · - · 0 · 1` | `␣- · 1 · 7` | `␣ · 0 · . · 5` |
| EuroLLM | `␣ · 7` | `␣ · 4 · 2` | `␣ · 2 · 0 · 2 · 6` | `␣ · 1 · 2 · 3 · 4 · 5 · 6 · 7 · 8` | `␣ · 3 · . · 1 · 4 · 1 · 5 · 9` | `␣ · 1 · ␣ · 0 · 0 · 0 · ␣ · 0 · 0 · 0` | `␣ · 1 · , · 0 · 0 · 0 · , · 0 · 0 · 0` | `␣ · 2 · 0 · 2 · 6 · - · 1 · 1 · - · 0 · 1` | `␣- · 1 · 7` | `␣ · 0 · . · 5` |
| LFM2.5 | `7` | `42` | `202 · 6` | `123 · 456 · 78` | `3 · . · 141 · 59` | `1 · ␣ · 000 · ␣ · 000` | `1 · , · 000 · , · 000` | `202 · 6 · - · 11 · - · 01` | `- · 17` | `0 · . · 5` |
| LFM3 | `7` | `42` | `202 · 6` | `123 · 456 · 78` | `3 · . · 141 · 59` | `1 · ␣ · 000 · ␣ · 000` | `1 · , · 000 · , · 000` | `202 · 6 · - · 11 · - · 01` | `- · 17` | `0 · . · 5` |
| Pythia (GPT-NeoX) | `7` | `42` | `20 · 26` | `12345 · 678` | `3 · . · 14 · 159` | `1 · ␣000 · ␣000` | `1 · , · 000 · , · 000` | `20 · 26 · - · 11 · - · 01` | `- · 17` | `0 · . · 5` |
| Qwen3.5 | `7` | `4 · 2` | `2 · 0 · 2 · 6` | `1 · 2 · 3 · 4 · 5 · 6 · 7 · 8` | `3 · . · 1 · 4 · 1 · 5 · 9` | `1 · ␣ · 0 · 0 · 0 · ␣ · 0 · 0 · 0` | `1 · , · 0 · 0 · 0 · , · 0 · 0 · 0` | `2 · 0 · 2 · 6 · - · 1 · 1 · - · 0 · 1` | `- · 1 · 7` | `0 · . · 5` |
| Slayer1B | `7` | `42` | `20 · 26` | `123 · 45 · 67 · 8` | `3 · . · 14 · 15 · 9` | `1 · ␣000 · ␣000` | `1 · , · 000 · , · 000` | `20 · 26 · - · 11 · - · 01` | `- · 17` | `0 · . · 5` |

Kawałki rozdziela „│”, tokeny w kawałku „·”. Pełny raport: https://github.com/adgr3/tokenizer-tax-pl/blob/main/REGEX.md.
Dane: `results/regex/bench_answer.csv`, `results/regex/bench_numbers.csv` w repo kodu. Data: 2026-11-02.
