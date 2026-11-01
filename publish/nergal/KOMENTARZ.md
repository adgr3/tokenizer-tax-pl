Tytuł: Ile polskiego tekstu mieści okno NERGAL-a — porównanie tokenizerów enkoderów

Cześć, przy okazji pomiaru „tokenów na słowo” (SIB-200, 25 języków; raport: https://github.com/adgr3/tokenizer-tax-pl) policzyłem
też tokenizer NERGAL-a (XLM-RoBERTa) i polskie enkodery. Tabela pokazuje, ile polskiego tekstu mieści jedno okno
512 tokenów (przybliżenie: bez znaczników specjalnych i bez nakładania okien).

| enkoder | słownik | PL tok./słowo | PL słów / okno 512 | PL znaków / okno 512 | tokenów vs NERGAL |
|---|---|---|---|---|---|
| Polish RoBERTa | 128001 | 1,35 | 379 | 2723 | 0,74 |
| HerBERT | 50000 | 1,42 | 360 | 2585 | 0,78 |
| XLM-RoBERTa | 250002 | 1,82 | 280 | 2011 | 1,00 |
| NERGAL (XLM-R) | 250004 | 1,82 | 280 | 2011 | 1,00 |

Co z tego wynika: tokenizer wpływa na szybkość i liczbę okien na dokument, nie na jakość wykrywania. Jeśli kiedyś
powstanie wersja NERGAL-a na polskim enkoderze, ta tabela pokazuje, ile tekstu zyskałoby jedno okno.
Dane: https://huggingface.co/datasets/adegier/tokenizer-fertility-pl (plik data/nergal_encoders.csv).
