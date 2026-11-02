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
