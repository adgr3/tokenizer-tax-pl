Tytuł: Regexy i tokeny w NERGAL-u na danych przetargowych — co łapią i gdzie się mylą

Cześć, w ramach pracy domowej o pre-tokenizacji (regexy tokenizerów: co robią i po co) przyjrzałem się też NERGAL-owi:
(1) jak tokenizer NERGAL-a (XLM-RoBERTa) i inne tną dane osobowe, (2) co robią reguły regex z `scrub_pii.py` na
polskich identyfikatorach przetargowych. Kodu nie uruchamiałem — wzorce wyciągnąłem analizą składni pliku.

## 1. Dane osobowe w tokenach

Model BIO decyduje token po tokenie. Numer rozbity na wiele krótkich tokenów (np. ze spacjami) łatwiej zamaskować
częściowo — to pasuje do ograniczenia z karty („spaced numbers may be partly masked”).

| rodzaj | kategoria | tekst | NERGAL (XLM-R) | XLM-RoBERTa | HerBERT | Polish RoBERTa | GPT-4o (o200k) | Bielik 4.5B v3 | Slayer1B | Aster-0.5B (OrisTeam) |
|---|---|---|---|---|---|---|---|---|---|---|
| dane osobowe | PESEL | `44051401359` | 5: `␣44 · 05 · 140 · 13 · 59` | 5: `␣44 · 05 · 140 · 13 · 59` | 6: `44 · 05 · 14 · 0 · 13 · 59</w>` | 5: `44 · 051 · 40 · 13 · 59` | 4: `440 · 514 · 013 · 59` | 12: `␣ · 4 · 4 · 0 · 5 · 1 · 4 · 0 · 1 · 3 · 5 · 9` | 6: `4 · 40 · 5 · 140 · 13 · 59` | 6: `4 · 40 · 5 · 140 · 13 · 59` |
| dane osobowe | telefon (spacje) | `601 234 567` | 5: `␣ · 601 · ␣234 · ␣ · 567` | 5: `␣ · 601 · ␣234 · ␣ · 567` | 4: `601</w> · 234</w> · 5 · 67</w>` | 4: `60 · 1 · ␣234 · ␣567` | 5: `601 · ␣ · 234 · ␣ · 567` | 12: `␣ · 6 · 0 · 1 · ␣ · 2 · 3 · 4 · ␣ · 5 · 6 · 7` | 6: `60 · 1 · ␣23 · 4 · ␣5 · 67` | 6: `60 · 1 · ␣23 · 4 · ␣5 · 67` |
| dane osobowe | telefon (ciągły, +48) | `+48601234567` | 5: `␣+ · 48 · 60 · 1234 · 567` | 5: `␣+ · 48 · 60 · 1234 · 567` | 7: `+</w> · 48 · 60 · 12 · 34 · 5 · 67</w>` | 6: `+ · 48 · 60 · 1234 · 5 · 67` | 5: `+ · 486 · 012 · 345 · 67` | 12: `␣+ · 4 · 8 · 6 · 0 · 1 · 2 · 3 · 4 · 5 · 6 · 7` | 6: `+ · 48 · 60 · 123 · 45 · 67` | 6: `+ · 48 · 60 · 123 · 45 · 67` |
| dane osobowe | telefon (kreski) | `tel. 601-234-567` | 7: `␣tel · . · ␣60 · 1-2 · 34 · - · 567` | 7: `␣tel · . · ␣60 · 1-2 · 34 · - · 567` | 8: `tel</w> · .</w> · 601</w> · -</w> · 234</w> · -</w> · 5 · 67</w>` | 6: `tel · . · ␣601 · -23 · 4-5 · 67` | 8: `tel · . · ␣ · 601 · - · 234 · - · 567` | 14: `␣tel · . · ␣ · 6 · 0 · 1 · - · 2 · 3 · 4 · - · 5 · 6 · 7` | 10: `tel · . · ␣60 · 1 · - · 23 · 4 · - · 5 · 67` | 10: `tel · . · ␣60 · 1 · - · 23 · 4 · - · 5 · 67` |
| dane osobowe | e-mail | `jan.kowalski@gmina.pl` | 10: `␣jan · . · ko · wal · ski · @ · g · mina · . · pl` | 10: `␣jan · . · ko · wal · ski · @ · g · mina · . · pl` | 8: `jan</w> · .</w> · kow · alski</w> · @</w> · gmina</w> · .</w> · pl</w>` | 8: `jan · . · kowa · lski · @ · gmina · . · pl` | 8: `jan · .k · ow · als · ki · @g · mina · .pl` | 9: `␣ja · n · . · kowa · lski · @ · gmina · . · pl` | 10: `jan · . · kow · al · ski · @ · g · mina · . · pl` | 9: `jan · . · kowa · lski · @ · g · mina · . · pl` |
| dane osobowe | IBAN | `PL61 1090 1014 0000 0712 1981 2874` | 13: `␣PL · 61 · ␣10 · 90 · ␣10 · 14 · ␣ · 0000 · ␣07 · 12 · ␣1981 · ␣28 · 74` | 13: `␣PL · 61 · ␣10 · 90 · ␣10 · 14 · ␣ · 0000 · ␣07 · 12 · ␣1981 · ␣28 · 74` | 12: `PL · 61</w> · 10 · 90</w> · 10 · 14</w> · 0000</w> · 07 · 12</w> · 1981</w> · 28 · 74</w>` | 13: `PL · 61 · ␣10 · 90 · ␣10 · 14 · ␣ · 0000 · ␣07 · 12 · ␣1981 · ␣28 · 74` | 20: `PL · 61 · ␣ · 109 · 0 · ␣ · 101 · 4 · ␣ · 000 · 0 · ␣ · 071 · 2 · ␣ · 198 · 1 · ␣ · 287 · 4` | 33: `␣PL · 6 · 1 · ␣ · 1 · 0 · 9 · 0 · ␣ · 1 · 0 · 1 · 4 · ␣ · 0 · 0 · 0 · 0 · ␣ · 0 · 7 · 1 · 2 · ␣ · 1 · 9 · 8 · 1 · ␣ · 2 · 8 · 7 · 4` | 13: `PL · 61 · ␣10 · 90 · ␣10 · 14 · ␣ · 0000 · ␣07 · 12 · ␣1981 · ␣28 · 74` | 13: `PL · 61 · ␣10 · 90 · ␣10 · 14 · ␣ · 0000 · ␣07 · 12 · ␣1981 · ␣28 · 74` |
| dane osobowe | NIP | `123-456-32-18` | 5: `␣123 · - · 456 · -32 · -18` | 5: `␣123 · - · 456 · -32 · -18` | 8: `123</w> · -</w> · 4 · 56</w> · -</w> · 32</w> · -</w> · 18</w>` | 5: `123 · - · 456 · -3 · 2-18` | 7: `123 · - · 456 · - · 32 · - · 18` | 14: `␣ · 1 · 2 · 3 · - · 4 · 5 · 6 · - · 3 · 2 · - · 1 · 8` | 8: `123 · - · 45 · 6 · - · 32 · - · 18` | 8: `123 · - · 45 · 6 · - · 32 · - · 18` |
| dane osobowe | KRS | `KRS 0000123456` | 6: `␣K · RS · ␣ · 0000 · 1234 · 56` | 6: `␣K · RS · ␣ · 0000 · 1234 · 56` | 6: `KR · S</w> · 0000 · 12 · 34 · 56</w>` | 5: `K · RS · ␣00001 · 234 · 56` | 7: `K · RS · ␣ · 000 · 012 · 345 · 6` | 12: `␣KRS · ␣ · 0 · 0 · 0 · 0 · 1 · 2 · 3 · 4 · 5 · 6` | 7: `K · RS · ␣ · 0000 · 123 · 45 · 6` | 7: `KR · S · ␣ · 0000 · 123 · 45 · 6` |
| dane osobowe | dowód osobisty | `ABC123456` | 3: `␣ABC · 1234 · 56` | 3: `␣ABC · 1234 · 56` | 5: `AB · C · 12 · 34 · 56</w>` | 4: `A · BC · 1234 · 56` | 3: `ABC · 123 · 456` | 7: `␣ABC · 1 · 2 · 3 · 4 · 5 · 6` | 5: `A · BC · 123 · 45 · 6` | 5: `A · BC · 123 · 45 · 6` |
| pułapka (nie PII) | kod CPV | `45233140-2` | 4: `␣45 · 233 · 140 · -2` | 4: `␣45 · 233 · 140 · -2` | 6: `45 · 23 · 3 · 140</w> · -</w> · 2</w>` | 4: `45 · 233 · 140 · -2` | 5: `452 · 331 · 40 · - · 2` | 11: `␣ · 4 · 5 · 2 · 3 · 3 · 1 · 4 · 0 · - · 2` | 6: `45 · 23 · 3 · 140 · - · 2` | 6: `45 · 23 · 3 · 140 · - · 2` |
| pułapka (nie PII) | nr ogłoszenia BZP | `2026/BZP 00123456/01` | 9: `␣20 · 26 · / · B · ZP · ␣00 · 1234 · 56 · /01` | 9: `␣20 · 26 · / · B · ZP · ␣00 · 1234 · 56 · /01` | 12: `20 · 26</w> · /</w> · B · Z · P</w> · 00 · 12 · 34 · 56</w> · /</w> · 01</w>` | 9: `20 · 26 · / · B · ZP · ␣00 · 1234 · 56 · /01` | 11: `202 · 6 · /B · Z · P · ␣ · 001 · 234 · 56 · / · 01` | 20: `␣ · 2 · 0 · 2 · 6 · / · B · ZP · ␣ · 0 · 0 · 1 · 2 · 3 · 4 · 5 · 6 · / · 0 · 1` | 12: `20 · 26 · / · B · Z · P · ␣00 · 123 · 45 · 6 · / · 01` | 12: `20 · 26 · / · B · Z · P · ␣00 · 123 · 45 · 6 · / · 01` |
| pułapka (nie PII) | znak sprawy | `ZP.271.12.2026` | 8: `␣ · ZP · . · 27 · 1 · .12. · 20 · 26` | 8: `␣ · ZP · . · 27 · 1 · .12. · 20 · 26` | 9: `Z · P</w> · .</w> · 271</w> · .</w> · 12</w> · .</w> · 20 · 26</w>` | 7: `ZP · . · 271 · . · 12. · 20 · 26` | 9: `Z · P · . · 271 · . · 12 · . · 202 · 6` | 14: `␣Z · P · . · 2 · 7 · 1 · . · 1 · 2 · . · 2 · 0 · 2 · 6` | 10: `Z · P · . · 27 · 1 · . · 12 · . · 20 · 26` | 10: `Z · P · . · 27 · 1 · . · 12 · . · 20 · 26` |
| pułapka (nie PII) | sygnatura KIO | `KIO 1234/26` | 6: `␣K · IO · ␣ · 1234 · / · 26` | 6: `␣K · IO · ␣ · 1234 · / · 26` | 6: `KI · O</w> · 12 · 34</w> · /</w> · 26</w>` | 5: `KI · O · ␣ · 1234 · /26` | 7: `K · IO · ␣ · 123 · 4 · / · 26` | 10: `␣K · IO · ␣ · 1 · 2 · 3 · 4 · / · 2 · 6` | 6: `K · IO · ␣12 · 34 · / · 26` | 6: `KI · O · ␣12 · 34 · / · 26` |
| pułapka (nie PII) | Dz.U. | `Dz. U. z 2024 r. poz. 1320` | 13: `␣Dz · . · ␣U · . · ␣z · ␣20 · 24 · ␣r · . · ␣poz · . · ␣13 · 20` | 13: `␣Dz · . · ␣U · . · ␣z · ␣20 · 24 · ␣r · . · ␣poz · . · ␣13 · 20` | 13: `Dz</w> · .</w> · U</w> · .</w> · z</w> · 20 · 24</w> · r</w> · .</w> · poz</w> · .</w> · 13 · 20</w>` | 12: `Dz · . · ␣U · . · ␣z · ␣2024 · ␣r · . · ␣poz · . · ␣13 · 20` | 15: `Dz · . · ␣U · . · ␣z · ␣ · 202 · 4 · ␣r · . · ␣poz · . · ␣ · 132 · 0` | 19: `␣Dz · . · ␣U · . · ␣z · ␣ · 2 · 0 · 2 · 4 · ␣r · . · ␣poz · . · ␣ · 1 · 3 · 2 · 0` | 12: `Dz · . · ␣U · . · ␣z · ␣2024 · ␣r · . · ␣poz · . · ␣13 · 20` | 12: `Dz · . · ␣U · . · ␣z · ␣2024 · ␣r · . · ␣poz · . · ␣13 · 20` |
| pułapka (nie PII) | kwota | `1 234 567,89 zł` | 7: `␣1 · ␣234 · ␣ · 567 · , · 89 · ␣zł` | 7: `␣1 · ␣234 · ␣ · 567 · , · 89 · ␣zł` | 7: `1</w> · 234</w> · 5 · 67</w> · ,</w> · 89</w> · zł</w>` | 6: `1 · ␣234 · ␣567 · , · 89 · ␣zł` | 8: `1 · ␣ · 234 · ␣ · 567 · , · 89 · ␣zł` | 14: `␣ · 1 · ␣ · 2 · 3 · 4 · ␣ · 5 · 6 · 7 · , · 8 · 9 · ␣zł` | 8: `1 · ␣23 · 4 · ␣5 · 67 · , · 89 · ␣zł` | 8: `1 · ␣23 · 4 · ␣5 · 67 · , · 89 · ␣zł` |
| pułapka (nie PII) | data | `2026-11-01` | 4: `␣20 · 26 · -11- · 01` | 4: `␣20 · 26 · -11- · 01` | 6: `20 · 26</w> · -</w> · 11</w> · -</w> · 01</w>` | 4: `20 · 26 · -11 · -01` | 6: `202 · 6 · - · 11 · - · 01` | 11: `␣ · 2 · 0 · 2 · 6 · - · 1 · 1 · - · 0 · 1` | 6: `20 · 26 · - · 11 · - · 01` | 6: `20 · 26 · - · 11 · - · 01` |
| pułapka (nie PII) | nr po „nr” | `umowa nr 123456789` | 6: `␣um · owa · ␣nr · ␣123 · 456 · 789` | 6: `␣um · owa · ␣nr · ␣123 · 456 · 789` | 7: `umowa</w> · nr</w> · 12 · 34 · 56 · 7 · 89</w>` | 6: `umowa · ␣nr · ␣12 · 345 · 67 · 89` | 7: `um · owa · ␣nr · ␣ · 123 · 456 · 789` | 12: `␣umowa · ␣nr · ␣ · 1 · 2 · 3 · 4 · 5 · 6 · 7 · 8 · 9` | 7: `um · owa · ␣nr · ␣123 · 45 · 67 · 89` | 8: `um · owa · ␣nr · ␣123 · 45 · 6 · 78 · 9` |
| pułapka (nie PII) | przepis | `art. 275 pkt 1` | 5: `␣art · . · ␣275 · ␣pkt · ␣1` | 5: `␣art · . · ␣275 · ␣pkt · ␣1` | 5: `art</w> · .</w> · 275</w> · pkt</w> · 1</w>` | 5: `art · . · ␣275 · ␣pkt · ␣1` | 7: `art · . · ␣ · 275 · ␣pkt · ␣ · 1` | 9: `␣art · . · ␣ · 2 · 7 · 5 · ␣pkt · ␣ · 1` | 6: `art · . · ␣27 · 5 · ␣pkt · ␣1` | 6: `art · . · ␣27 · 5 · ␣pkt · ␣1` |

## 2. Reguły `scrub_pii.py` na danych osobowych i na pułapkach przetargowych

Pułapki to identyfikatory z dokumentów przetargowych, które **nie** są danymi osobowymi (CPV, nr ogłoszenia BZP,
znak sprawy, sygnatura KIO, Dz.U., kwota, data, „nr …”). Trafienie pułapki = ryzyko niepotrzebnego zamaskowania.

| linia | nazwa | wzorzec (skrót) | trafia dane osobowe | trafia pułapki (nie PII) |
|---|---|---|---|---|
| 71 | _EMAIL_RE | `(dynamiczny) _EMAIL_START + r"[ \t]{0,3}(?:" + _EMAIL_DOMAIN + r"\.)+[^\W\d_]{2,}\b"` | — | — |
| 72 | _EMAIL_WRAP_RE | `(dynamiczny) _EMAIL_START + r"[ \t]{0,3}(?:" + _EMAIL_DOMAIN
    + r"\.)+[ \t]*\r?\n[ \t]*…` | — | — |
| 75 | _EMAIL_FRAGMENT_RE | `(dynamiczny) _EMAIL_START + r"(?=[ \t]*\r?$)"` | — | — |
| 76 | _EMAIL_LABEL_RE | `\be[ -]?mail[ \t]*:[ \t]*\Z` | — | — |
| 77 | _GLUED_WWW_RE | `(?<=[^\W\d_]{2})www\.` | — | — |
| 80 | _EDELIVERY_RE | `(dynamiczny) r"\bAE:PL" + _EDELIVERY_WRAP + r"\d{5}" + _EDELIVERY_WRAP + r"\d{5}"
        …` | — | — |
| 82 | _EPUAP_RE | `(?<![\w/])/[\w-]+/[\w-]+(?![\w/-])` | — | — |
| 83 | _EPUAP_LABEL_RE | `\b(?:e[ -]?puap\|elektroniczna[ \t]+skrzynka[ \t]+podawcza)\b[^\n/\[\]]{0,50}\Z` | — | — |
| 85 | _PIN_RE | `(?P<label>\bPIN[ \t]*[:=][ \t]*)(?P<number>[\u202a-\u202e\u2066-\u2069]*\d(?:[ \t]?\d){3,1…` | — | — |
| 106 | _IBAN_RE | `(dynamiczny) r"\b(?:" + "\|".join(
        country + r"[ \t-]*[0-9]{2}(?:[ \t-]*[A-Z0-9]){"…` | — | — |
| 113 | _ACCOUNT_RE | `\b(?:PL[ \t-]*)?(?:\d[ \t-]*){25}\d\b` | IBAN: PL61 1090 1014 0000 0712 1981 2874 | — |
| 114 | _REGON14_RE | `\b\d{14}\b` | — | — |
| 115 | _PESEL_RE | `\b\d{11}\b` | PESEL: 44051401359 \| telefon (ciągły, +48): 48601234567 | — |
| 116 | _NIP_DASH_RE | `\b(?:PL[ \t]*)?\d{3}(?:[- \t]\d{3}[- \t]\d{2}[- \t]\d{2}\|[- \t]\d{2}[- \t]\d{2}[- \t]\d{3}…` | NIP: 123-456-32-18 | — |
| 117 | _NIP_RE | `\b(?:PL[ \t]*)?\d{10}\b` | KRS: 0000123456 | — |
| 118 | _DOCUMENT_RE | `\b(?P<label>(?:dow[oó]d(?:u\|em)?[ \t]+osobist(?:y\|ego\|ym)\|(?:nr\|numer)[ \t]+dowodu\|paszpor…` | — | — |
| 131 | _LABELLED_ID_RE | `(dynamiczny) r"(?P<label>" + _LABELLED_ID_LABEL + r")"
    r"(?P<number>(?:PL[ \t]*)?(?:[0…` | — | — |
| 137 | _LAND_REGISTER_RE | `\b(?P<court>[A-Z]{2}\d[A-Z])[ \t]*[/ \t][ \t]*(?P<number>\d{1,8})[ \t]*/[ \t]*(?P<check>\d…` | — | — |
| 139 | _LAND_REGISTER_LABEL_RE | `(?:(?-i:\bKW\b)\|\bks(?:\.\|i[eęą]\w*)[ \t]+wieczyst\w*)[^\n]{0,30}\Z` | — | — |
| 157 | _LAND_REGISTER_WORDS_RE | `(dynamiczny) rf"\b(?P<court>[A-Z]{{2}}\s*(?:\d\|{_DIGIT_WORD})\s*[A-Z]){_SLASH_WORDS}"
    …` | — | — |
| 160 | _REGON9_RE | `\b\d{9}\b` | — | nr po „nr”: 123456789 |
| 167 | _NIP_LABEL_RE | `(dynamiczny) r"\bNIP\b" + _ID_LABEL_NOTE + _ID_LABEL_SKIP + _ID_LABEL_END` | — | — |
| 168 | _REGON_LABEL_RE | `(dynamiczny) r"\bREGON\b" + _ID_LABEL_NOTE + _ID_LABEL_SKIP + _ID_LABEL_END` | — | — |
| 172 | _SPLIT_RE | `(dynamiczny) r"(?<![\w\]])(?:\+[ \t]?)?\d+(?:[ \t-]?(?:\d+\|" + _BOUNDARY + r"))++(?!\w\|[.,…` | — | — |
| 173 | _SPLIT_FRAGMENT_RE | `(?:\+[ \t]?)?\d+(?:[ \t-]\d+)*` | PESEL: 44051401359 \| telefon (spacje): 601 234 567 \| telefon (ciągły, +48): +48601234567 \| telefon (kreski): 601-234-567 \| IBAN: 61 1090 1014 0000 0712 1981 2874 \| NIP: 123-456-32-18 \| KRS: 0000123456 \| dowód osobisty: 123456 | kod CPV: 45233140-2 \| nr ogłoszenia BZP: 2026 \| znak sprawy: 271 \| sygnatura KIO: 1234 \| Dz.U.: 2024 \| kwota: 1 234 567 \| data: 2026-11-01 \| nr po „nr”: 123456789 \| przepis: 275 |
| 174 | _SPLIT_LABEL_RE | `(dynamiczny) _LABELLED_ID_LABEL + r"\Z"` | — | — |
| 175 | _SPLIT_NOT_PHONE_RE | `\d{2}-\d{3}\|\d{4}-\d{2}-\d{2}\|\d{2}-\d{2}-\d{4}` | telefon (kreski): 01-234 \| NIP: 23-456 | data: 2026-11-01 |
| 177 | _KRS_RE | `\b\d{6,10}(?!\w\|[ \t-]*\d)` | KRS: 0000123456 | nr ogłoszenia BZP: 00123456 \| nr po „nr”: 123456789 |
| 179 | _KRS_LABEL_RE | `(dynamiczny) r"(?:\bKRS\b\|\bKrajow\w*[ \t]+Rejestr\w*[ \t]+S[aą]dow\w*)"
    r"(?:[ \t]{0,…` | — | — |
| 196 | _VANITY_PHONE_RE | `(?<!\w)\+1[ \t-]+\d{3}[ \t-]+(?:\d{3}-[A-Z]{4}\|[A-Z]{7})(?:[ \t]+\(\d{4,7}\))?(?!\w)` | — | — |
| 204 | _PHONE_RE | `(dynamiczny) _VANITY_PHONE_RE.pattern + r"\|(?:(?<!\w)\|(?<=telefon)\|(?<=tel)\|(?<=faks)\|(?<=…` | — | — |
| 209 | _SHORT_PHONE_LABEL_RE | `(dynamiczny) r"(?:\b(?:tel(?:efon\w*)?(?:(?:\.[ \t]*\|[ \t]+)(?:kom[oó]rk\w*\|lokaln\w*\|stac…` | — | — |
| 213 | _PHONE_LABEL_RE | `\b(?:tel(?:efon[^\W\d_]*)?\|fax\|faks(?:em)?\|kom(?:[oó]rk[^\W\d_]*)?\|gsm\|infolini[^\W\d_]*\|(…` | telefon (kreski): tel | — |
| 219 | _PHONE_BREAK_RE | `\n\|\.[ \t]+(?=\d)\|[ \t]+(?=\(?(?:[01]?\d\|2[0-3])[.:][0-5]\d\|\d{1,2}[.)][ \t]+\d{1,2}[./]\d…` | telefon (kreski): .  | Dz.U.: .  \| przepis: .  |
| 222 | _SECTION_MARKER_RE | `\d{1,2}[.)](?!\d)` | — | — |
| 223 | _PHONE_EXTENSION_RE | `(?:(?:[ \t]+,?[ \t]*\|,[ \t]*)wew(?:n(?:ętrzny)?)?\.?[ \t]*\d{1,5}\|[ \t]+do[ \t]+\d{1,3}(?=…` | — | — |
| 225 | _OTHER_NUMBER_LABEL_RE | `(dynamiczny) r"\b(?:NIP\|REGON\|PESEL\|KRS\|ISBN\|kod)\b(?:(?!" + re.escape(PERSON_TAG) + r")[^…` | — | — |
| 232 | _GROUPED_PHONE_RE | `(dynamiczny) r"(?:\+48[ \t]?)?(?:(?:" + _MOBILE_PREFIX + r")\d(?P<m>[ -])\d{3}(?P=m)\d{3}"…` | — | — |
| 235 | _PHONE_LIST_HEADING_RE | `[ \t]*(?:numery[ \t]+kontaktowe\|telefony(?:[ \t]+(?:kontaktowe\|zaufania))?\|fax\|faks\|zapisz…` | — | — |
| 239 | _CONTACT_INTRO_RE | `\b(?:kontakt\b\|zapisy\b\|zapisz[ \t]+się\b\|rejestracja\b)(?:nr\.\|[^\n.!?;]){0,75}\Z` | — | — |
| 242 | _PHONE_HEADING_RE | `(?<!\[)\b(?:tel(?:efon[^\W\d_]*)?\b\|kontakt\b\|zapisy\b\|zapisz[ \t]+się\b\|(?:za)?dzwo[ńn][^…` | — | — |
| 246 | _CONTACT_EXCLUDE_RE | `\b(?:spraw\w*\|kod\w*\|kwot\w*\|statystyk\w*\|taryf\w*)\b` | — | — |
| 247 | _PHONE_LINE_RE | `(?<!\w)\d{2,3}(?:[ \t-]\d{2,4}){2,3}(?!\w)` | telefon (spacje): 601 234 567 \| telefon (kreski): 601-234-567 \| NIP: 123-456-32-18 | — |
| 248 | _PHONE_TITLE_RE | `\b(?:film\w*\|serial\w*\|tytuł\w*\|zatytułowan\w*)\b` | — | — |
| 249 | _STAFF_ROLE_RE | `\b(?:inspektor\|referent\|koordynator\|psycholog\|księgowość\|księgowy\|księgowa\|pracownicy[ \t]…` | — | — |
| 379 | _MONEY_AFTER_RE | `(dynamiczny) r"(?:[,.][0-9]+)?" + _MONEY_GAP
    + r"(?:(?:tys\.?\|mln\|mld\|bln)\b\.?" + _MO…` | — | — |
| 384 | _MONEY_BEFORE_RE | `(dynamiczny) r"(?:\b(?:PLN\|EUR\|USD\|GBP\|CHF)\|[€$£])" + _MONEY_GAP + r"$"` | — | — |
| 737 | _PHONE_CONNECTOR_RE | `\s*(?:[,;/&\n]\|\b(?:lub\|albo\|i\|oraz\|and)\b)\s*` | — | nr ogłoszenia BZP: / \| sygnatura KIO: / \| kwota: , |
| 738 | _KEYPAD_RE | `(?<=[\d-])[A-Z]+` | — | — |
| 739 | _PHONE_CODE_RE | `\(?\+?\d{2,4}\)?` | PESEL: 4405 \| telefon (spacje): 601 \| telefon (ciągły, +48): +4860 \| telefon (kreski): 601 \| IBAN: 61 \| NIP: 123 \| KRS: 0000 \| dowód osobisty: 1234 | kod CPV: 4523 \| nr ogłoszenia BZP: 2026 \| znak sprawy: 271 \| sygnatura KIO: 1234 \| Dz.U.: 2024 \| kwota: 234 \| data: 2026 \| nr po „nr”: 1234 \| przepis: 275 |
| 740 | _PHONE_DASH_RE | `\s+[-–—]\s+` | — | — |
| 186 |  | `\b(?:\d{9}\|\d{2}-\d{3}-\d{4})(?!\w\|[ \t-]*\d)` | — | nr po „nr”: 123456789 |
| 187 |  | `(dynamiczny) r"\bD-?U-?N-?S\b(?:[ \t]?®)?(?:[ \t]{1,8}number)?" + _REGISTRY_BY + _ID_LABEL…` | — | — |
| 188 |  | `\b\d{9}(?!\w\|[ \t-]*\d)` | — | nr po „nr”: 123456789 |
| 189 |  | `(dynamiczny) r"\bBDO\b" + _REGISTRY_BY + _ID_LABEL_END` | — | — |
| 190 |  | `\b\d{12}(?!\w\|[ \t-]*\d)` | — | — |
| 191 |  | `(dynamiczny) r"(?:\bRPWDL\b\|\bksi[eę]g\w*[ \t]+rejestrow\w*)" + _REGISTRY_BY + _ID_LABEL_E…` | — | — |

Wzorce trafiające pułapki: _REGON9_RE, _SPLIT_FRAGMENT_RE, _SPLIT_NOT_PHONE_RE, _KRS_RE, _PHONE_BREAK_RE, _PHONE_CONNECTOR_RE, _PHONE_CODE_RE, linia 186, linia 188.

<!-- AGENT: poniżej dopisz 3–6 zdań prostym językiem: jakie rodziny reguł są w pliku (telefony, identyfikatory,
     e-maile…), po co każda, i które pułapki są ryzykowne. Tylko na podstawie tabel wyżej. -->

W `scrub_pii.py` jest 57 wzorców w kilku rodzinach: adresy e-mail, ePUAP i e-Doręczenia; numery kont i IBAN;
identyfikatory (PESEL, NIP, REGON 9 i 14 cyfr, KRS, dowód osobisty, księgi wieczyste); duża grupa reguł telefonów
(etykiety „tel.”, numery rozbite spacjami i kreskami, numery wewnętrzne, nagłówki list kontaktów) oraz kwoty, które mają
chronić liczby przed pomyłkowym maskowaniem. Reguły z adresami e-mail i część etykiet są budowane w kodzie dynamicznie
(21 z 57), więc bez uruchamiania pliku nie dało się ich sprawdzić. Każdą stałą regułę testowałem osobno, bez kolejności
i kontekstu z pliku, więc trafienie pułapki oznacza ryzyko do sprawdzenia, a nie pewny błąd. Najbardziej ryzykowne są:
`_KRS_RE` (łapie 8 cyfr numeru ogłoszenia BZP i 9-cyfrowy „umowa nr 123456789”), `_REGON9_RE` i reguły z linii 186
i 188 (ten sam numer umowy), `_SPLIT_NOT_PHONE_RE` (data `2026-11-01`) oraz pomocnicze `_PHONE_CODE_RE`
i `_SPLIT_FRAGMENT_RE`, które trafiają fragmenty prawie każdej liczby (CPV, BZP, znak sprawy, sygnatura KIO, Dz.U.,
kwota). Dodatkowo `_PESEL_RE` łapie też telefon `+48601234567` (11 cyfr), a `_NIP_RE` numer KRS — dane i tak zostaną
zamaskowane, ale z błędną kategorią.


Pełny raport: https://github.com/adgr3/tokenizer-tax-pl/blob/main/REGEX.md · dane: https://huggingface.co/datasets/adegier/tokenizer-fertility-pl
