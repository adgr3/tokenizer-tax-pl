**Podatek tokenowy — replikacja dla polskich modeli + agregat (51 tokenizerów, 25 języków)**

• Polski kosztuje średnio 2,45 tokenu na słowo, czyli 1,72× tyle co angielski (miejsce 11 z 25 języków). Rozrzut między tokenizerami jest duży: od 1,46 (polish-gpt2) do 4,40 (Konrad 456).
• Najtaniej wychodzą: angielski (1,58), hiszpański (1,86), francuski (1,96). Najdrożej: bułgarski (4,04), ukraiński (4,68), grecki (5,53).
• Po rodzinach językowych (ile razy drożej niż angielski): romańskie 1,33×, germańskie 1,39×, celtyckie 1,76×, słowiańskie 2,06×, ugrofińskie 2,24×, bałtyckie 2,27×, semickie 2,40×, grecki 3,43×.
• Najlepsze tokenizery dla polskiego: polish-gpt2 (1,46), APT3 1B (Azurro) (1,51), SlayerLab Polish BPE 32k (1,57); najsłabsze: GPT-2 (3,73), Slayer149 (3,84), Konrad 456 (4,40).
• Tokenizery polskich modeli: średnio 2,36 tok./słowo po polsku; pozostałe: 2,50.
• Wielkość słownika a polski: korelacja rang Spearmana -0,18 (dla angielskiego -0,66). Wartość ujemna = większy słownik, mniej tokenów.

Kalibracja z danymi z pracy: średnio 0,014 tok./słowo różnicy.
Raport i kod: https://github.com/adgr3/tokenizer-tax-pl · dane: https://huggingface.co/datasets/adegier/tokenizer-fertility-pl
