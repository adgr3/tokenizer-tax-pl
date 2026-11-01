# Tokeny na słowo — co robisz Ty

1. Rozpakuj folder do `D:\VPS\fabryka\tokenizer-tax-pl`.
2. Otwórz w nim Claude Code i napisz: **Wykonaj ZADANIE_DLA_CLAUDE_CODE.md**
3. Agent poprosi o dwie rzeczy:
   - wpisanie kluczy AIHubMix i OpenRouter do pliku `.env` (sam wklejasz je do pliku, nie do czatu);
   - zgodę na publikację na GitHub i Hugging Face.
4. Na końcu dostaniesz podsumowanie i gotową wiadomość na kurs (`report/DISCORD.md`).

Karta graficzna nie jest potrzebna. Pobierane są tylko tokenizery (kilka–kilkadziesiąt MB każdy), bez wag modeli.

## Co powstanie

- `README.md` — raport z wykresami (strona główna repo na GitHub).
- `charts/` — 9 wykresów: replikacja dla polskich modeli, wszystkie tokenizery, języki, rodziny, ranking dla polskiego,
  słownik vs polski, stabilność rankingu, polski na różnych rodzajach tekstu, NERGAL.
- `publish/hf/` — zbiór danych na Hugging Face (`adegier/tokenizer-fertility-pl`).
- `publish/bench_team/` — tabela dla Bench Team (wysyłasz dopiero po rozmowie na #bench-team).
- `publish/nergal/KOMENTARZ.md` — gotowy wpis dla autora NERGAL-a (zakładka Community przy modelu).

## Budżet API

- AIHubMix: tylko modele z ceną wejścia ≤ 0,20 USD za 1 mln tokenów; bezpiecznik łączny 1 USD (zmienisz w `.env`).
- OpenRouter: tylko darmowe modele, których nie ma w AIHubMix (limit 50 zapytań dziennie — reszta następnego dnia).
