### Co z tego wynika

*To wnioski autora na podstawie liczb z raportu, nie osobny pomiar.*

Polski tekst kosztuje średnio 1,72× tyle tokenów co angielski (2,45 wobec 1,58 tokenu na słowo). To więcej niż w językach
romańskich i germańskich, ale mniej niż w bałtyckich, ugrofińskich czy w greckim. Przy wyborze modelu do polskich
zastosowań bardziej liczy się to, na czym tokenizer był uczony, niż wielkość słownika: najoszczędniejsze są tokenizery
uczone na polskim (polish-gpt2 1,46, APT3 1,51, Bielik 4.5B v3 1,63, Slayer1B 1,66) przy słowniku ok. 32–50 tys.,
a wielkość słownika słabo wiąże się z wynikiem dla polskiego (korelacja −0,18 wobec −0,66 dla angielskiego). Nie każdy
„polski” model ma jednak polski tokenizer: Bielik 11B v3 i PLLuM 8x7B (2,95), Llama-PLLuM 8B (2,61) i PLLuM 12B (2,22)
dziedziczą tokenizer modelu bazowego. Tokenizery uczone tylko na polskim wygrywają po polsku, ale wyraźnie przegrywają
w innych językach, dlatego ranking dla polskiego najsłabiej zgadza się z rankingami pozostałych języków (to samo podbija
średnie innych języków w agregacie). Dla kosztu API: w tej próbie Grok 4.1 Fast koduje polski najoszczędniej (1,86),
a Claude Haiku 5.5 najdrożej (3,46), czyli ten sam polski tekst to u Claude'a prawie dwa razy więcej tokenów; po
uwzględnieniu ceny najtańszy na 1000 polskich słów jest Doubao Seed 2.0 Mini (0,000068 USD).

### Modele przez API, których nie zmierzono

- Gemini Pro (AIHubMix): „model cannot be served” — innego Gemini z ceną wejścia ≤ 0,20 USD/1 mln tokenów nie ma.
- ERNIE X1 Turbo (brak dostępu, HTTP 401) i ERNIE 4.5 Turbo (model offline) — rodzina ERNIE bez wyniku.
- Jev (model decyzyjny): HTTP 404 przez `chat/completions` — zgodnie z regułą pominięty.
- Darmowe modele AIHubMix (Cohere North Mini, Kimi K3, dots.3, Flint, Xing 4.0): wyczerpany dzienny limit darmowych
  zapytań (North: 92 ze 126 zapytań); skrypt dokończy je kolejnego dnia.
- OpenRouter: Inkling (Thinking Machines) dostępny tylko w aplikacjach agentowych (HTTP 403); darmowe modele kontrolne
  (Gemma 4, LFM2.5) chwilowo przeciążone u dostawców (HTTP 429) — do ponowienia kolejnego dnia.
- Amazon Nova: brak w katalogu AIHubMix.
