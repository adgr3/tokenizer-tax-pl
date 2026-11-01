# Przepis

- Kod: https://github.com/adgr3/tokenizer-tax-pl (commit: uzupełnij po wypchnięciu)
- Dane: Davlan/sib200, split test, 25 języków; bloki ok. 6000 znaków
- Komendy: `python -m tt.data && python -m tt.measure_local && python -m tt.analyze`
- Tokenizery i rewizje: `results/fertility_long.csv` (kolumna `repo_used`) i `results/local/*.json` w repo kodu
- Sprzęt: CPU (GPU niepotrzebne). Data: 2026-11-01
