Kawałek (pre-token) = kolorowe pole; tokeny wewnątrz kawałka oddzielone pionową kreską. ␣ spacja, ⏎ nowa linia.

**Tekst:** `W␣2026␣r.␣Gmina␣Łomianki␣ogłosiła␣przetarg␣nr␣ZP.271.12.2026␣na␣kwotę␣1␣234␣567,89␣zł.`

```
GPT-2                  (49 tok.)  W │ ␣20·26 │ ␣r │ . │ ␣G·min·a │ ␣�·�·om·ian·ki │ ␣o·g·ł·osi·ł·a │ ␣pr·z·et·arg │ ␣n·r │ ␣Z·P │ . │ 271 │ . │ 12 │ . │ 20·26 │ ␣na │ ␣k·w·ot·�·� │ ␣1 │ ␣234 │ ␣5·67 │ , │ 89 │ ␣z·ł │ .
GPT-4 (cl100k)         (44 tok.)  W │ ␣ │ 202 │ 6 │ ␣r │ . │ ␣G·mina │ ␣�·�·om·ian·ki │ ␣og·ł·osi·ła │ ␣prz·et·arg │ ␣nr │ ␣Z·P │ . │ 271 │ . │ 12 │ . │ 202 │ 6 │ ␣na │ ␣kw·ot·ę │ ␣ │ 1 │ ␣ │ 234 │ ␣ │ 567 │ , │ 89 │ ␣zł │ .
GPT-4o (o200k)         (42 tok.)  W │ ␣ │ 202 │ 6 │ ␣r │ . │ ␣G·mina │ ␣Ł·omi·anki │ ␣og·ł·osi·ła │ ␣prz·et·arg │ ␣nr │ ␣Z·P │ . │ 271 │ . │ 12 │ . │ 202 │ 6 │ ␣na │ ␣kw·ot·ę │ ␣ │ 1 │ ␣ │ 234 │ ␣ │ 567 │ , │ 89 │ ␣zł │ .
Llama 3.3              (44 tok.)  W │ ␣ │ 202 │ 6 │ ␣r │ . │ ␣G·mina │ ␣�·�·om·ian·ki │ ␣og·ł·osi·ła │ ␣prz·et·arg │ ␣nr │ ␣Z·P │ . │ 271 │ . │ 12 │ . │ 202 │ 6 │ ␣na │ ␣kw·ot·ę │ ␣ │ 1 │ ␣ │ 234 │ ␣ │ 567 │ , │ 89 │ ␣zł │ .
Qwen3                  (54 tok.)  W │ ␣ │ 2 │ 0 │ 2 │ 6 │ ␣r │ . │ ␣G·mina │ ␣Ł·om·ian·ki │ ␣ogł·osi·ła │ ␣prz·et·arg │ ␣nr │ ␣Z·P │ . │ 2 │ 7 │ 1 │ . │ 1 │ 2 │ . │ 2 │ 0 │ 2 │ 6 │ ␣na │ ␣kw·ot·ę │ ␣ │ 1 │ ␣ │ 2 │ 3 │ 4 │ ␣ │ 5 │ 6 │ 7 │ , │ 8 │ 9 │ ␣zł │ .
DeepSeek V3            (43 tok.)  W │ ␣ │ 202 │ 6 │ ␣r │ . │ ␣G·mina │ ␣Ł·om·ian·ki │ ␣og·ł·osi·ła │ ␣prz·et·arg │ ␣nr │ ␣Z·P │ . │ 271 │ . │ 12 │ . │ 202 │ 6 │ ␣na │ ␣kw·ot·ę │ ␣ │ 1 │ ␣ │ 234 │ ␣ │ 567 │ , │ 89 │ ␣zł │ .
Gemma 3                (54 tok.)  W·␣·2·0·2·6·␣r·.·␣G·mina·␣Ł·om·ian·ki·␣og·ł·osi·ła·␣przet·arg·␣nr·␣Z·P·.·2·7·1·.·1·2·.·2·0·2·6·␣na·␣kw·ot·ę·␣·1·␣·2·3·4·␣·5·6·7·,·8·9·␣zł·.
Mistral Nemo (Tekken)  (53 tok.)  W │ ␣ │ 2 │ 0 │ 2 │ 6 │ ␣r │ . │ ␣G·mina │ ␣Ł·om·ian·ki │ ␣ogł·osi·ła │ ␣przet·arg │ ␣nr │ ␣Z·P │ . │ 2 │ 7 │ 1 │ . │ 1 │ 2 │ . │ 2 │ 0 │ 2 │ 6 │ ␣na │ ␣kw·ot·ę │ ␣ │ 1 │ ␣ │ 2 │ 3 │ 4 │ ␣ │ 5 │ 6 │ 7 │ , │ 8 │ 9 │ ␣zł │ .
Bielik 11B v3          (56 tok.)  ␣W·␣·2·0·2·6·␣r·.·␣G·mina·␣Ł·om·ian·ki·␣og·ł·osi·ła·␣prz·et·arg·␣nr·␣Z·P·.·2·7·1·.·1·2·.·2·0·2·6·␣na·␣kw·ot·ę·␣·1·␣·2·3·4·␣·5·6·7·,·8·9·␣z·ł·.
Bielik 4.5B v3         (46 tok.)  ␣W·␣·2·0·2·6·␣r·.·␣Gmina·␣Ło·mian·ki·␣ogłosiła·␣przetarg·␣nr·␣Z·P·.·2·7·1·.·1·2·.·2·0·2·6·␣na·␣kwotę·␣·1·␣·2·3·4·␣·5·6·7·,·8·9·␣zł·.
PLLuM 12B              (53 tok.)  W │ ␣ │ 2 │ 0 │ 2 │ 6 │ ␣r │ . │ ␣G·mina │ ␣Ł·om·ian·ki │ ␣ogł·osi·ła │ ␣przet·arg │ ␣nr │ ␣Z·P │ . │ 2 │ 7 │ 1 │ . │ 1 │ 2 │ . │ 2 │ 0 │ 2 │ 6 │ ␣na │ ␣kw·ot·ę │ ␣ │ 1 │ ␣ │ 2 │ 3 │ 4 │ ␣ │ 5 │ 6 │ 7 │ , │ 8 │ 9 │ ␣zł │ .
Slayer1B               (33 tok.)  W │ ␣20·26 │ ␣r │ . │ ␣Gmina │ ␣Łom·ianki │ ␣ogłos·iła │ ␣przetarg │ ␣nr │ ␣Z·P │ . │ 27·1 │ . │ 12 │ . │ 20·26 │ ␣na │ ␣kwotę │ ␣1 │ ␣23·4 │ ␣5·67 │ , │ 89 │ ␣zł │ .
Aster-0.5B (OrisTeam)  (32 tok.)  W │ ␣2026 │ ␣r │ . │ ␣Gmina │ ␣Ło·mian·ki │ ␣ogłosiła │ ␣przetarg │ ␣nr │ ␣Z·P │ . │ 27·1 │ . │ 12 │ . │ 20·26 │ ␣na │ ␣kwotę │ ␣1 │ ␣23·4 │ ␣5·67 │ , │ 89 │ ␣zł │ .
GoLLeM (dynaword-32k)  (33 tok.)  W │ ␣2026 │ ␣r │ . │ ␣G·mina │ ␣Ło·mia·nki │ ␣ogło·siła │ ␣przetar·g │ ␣nr │ ␣Z·P │ . │ 27·1 │ . │ 12 │ . │ 2026 │ ␣na │ ␣kwotę │ ␣1 │ ␣234 │ ␣5·67 │ , │ 89 │ ␣zł │ .
NERGAL (XLM-R)         (34 tok.)  ␣W │ ␣20·26 │ ␣r·. │ ␣G·mina │ ␣Ł·omia·nki │ ␣og·ło·si·ła │ ␣przetarg │ ␣nr │ ␣·ZP·.·27·1·.12.·20·26 │ ␣na │ ␣kwotę │ ␣1 │ ␣234 │ ␣·567·,·89 │ ␣zł·.
HerBERT                (31 tok.)  W</w> │ 20·26</w> │ r</w> │ .</w> │ Gmina</w> │ Ł·omi·anki</w> │ ogłosiła</w> │ przetarg</w> │ nr</w> │ Z·P</w> │ .</w> │ 271</w> │ .</w> │ 12</w> │ .</w> │ 20·26</w> │ na</w> │ kwotę</w> │ 1</w> │ 234</w> │ 5·67</w> │ ,</w> │ 89</w> │ zł</w> │ .</w>
```

**Tekst:** `PESEL␣44051401359,␣tel.␣+48␣601␣234␣567,␣e-mail:␣jan.kowalski@gmina.pl`

```
GPT-2                  (34 tok.)  P·ES·EL │ ␣4·405·14·01·359 │ , │ ␣tel │ . │ ␣+ │ 48 │ ␣601 │ ␣234 │ ␣5·67 │ , │ ␣e │ - │ mail │ : │ ␣jan │ . │ k·ow·als·ki │ @ │ g·min·a │ . │ pl
GPT-4 (cl100k)         (30 tok.)  PE·SEL │ ␣ │ 440 │ 514 │ 013 │ 59 │ , │ ␣tel │ . │ ␣+ │ 48 │ ␣ │ 601 │ ␣ │ 234 │ ␣ │ 567 │ , │ ␣e │ -mail │ : │ ␣jan │ .k·ow·als·ki │ @g·mina │ .pl
GPT-4o (o200k)         (30 tok.)  PE·SEL │ ␣ │ 440 │ 514 │ 013 │ 59 │ , │ ␣tel │ . │ ␣+ │ 48 │ ␣ │ 601 │ ␣ │ 234 │ ␣ │ 567 │ , │ ␣e │ -mail │ : │ ␣jan │ .k·ow·als·ki │ @g·mina │ .pl
Llama 3.3              (30 tok.)  PE·SEL │ ␣ │ 440 │ 514 │ 013 │ 59 │ , │ ␣tel │ . │ ␣+ │ 48 │ ␣ │ 601 │ ␣ │ 234 │ ␣ │ 567 │ , │ ␣e │ -mail │ : │ ␣jan │ .k·ow·als·ki │ @g·mina │ .pl
Qwen3                  (44 tok.)  PE·SEL │ ␣ │ 4 │ 4 │ 0 │ 5 │ 1 │ 4 │ 0 │ 1 │ 3 │ 5 │ 9 │ , │ ␣tel │ . │ ␣+ │ 4 │ 8 │ ␣ │ 6 │ 0 │ 1 │ ␣ │ 2 │ 3 │ 4 │ ␣ │ 5 │ 6 │ 7 │ , │ ␣e │ -mail │ : │ ␣jan │ .k·ow·als·ki │ @g·mina │ .pl
DeepSeek V3            (30 tok.)  P·ES·EL │ ␣ │ 440 │ 514 │ 013 │ 59 │ , │ ␣tel │ . │ ␣+ │ 48 │ ␣ │ 601 │ ␣ │ 234 │ ␣ │ 567 │ , │ ␣e │ -mail │ : │ ␣jan │ .k·ow·alski │ @g·mina │ .pl
Gemma 3                (46 tok.)  PES·EL·␣·4·4·0·5·1·4·0·1·3·5·9·,·␣tel·.·␣+·4·8·␣·6·0·1·␣·2·3·4·␣·5·6·7·,·␣e·-·mail·:·␣jan·.·kow·alski·@·g·mina·.·pl
Mistral Nemo (Tekken)  (45 tok.)  PE·SE·L │ ␣ │ 4 │ 4 │ 0 │ 5 │ 1 │ 4 │ 0 │ 1 │ 3 │ 5 │ 9 │ , │ ␣tel │ . │ ␣+ │ 4 │ 8 │ ␣ │ 6 │ 0 │ 1 │ ␣ │ 2 │ 3 │ 4 │ ␣ │ 5 │ 6 │ 7 │ , │ ␣e │ -mail │ : │ ␣jan │ .·kow·alski │ @·g·mina │ .pl
Bielik 11B v3          (47 tok.)  ␣PE·SEL·␣·4·4·0·5·1·4·0·1·3·5·9·,·␣tel·.·␣+·4·8·␣·6·0·1·␣·2·3·4·␣·5·6·7·,·␣e·-·mail·:·␣jan·.·kow·als·ki·@·g·mina·.·pl
Bielik 4.5B v3         (45 tok.)  ␣PESEL·␣·4·4·0·5·1·4·0·1·3·5·9·,·␣tel·.·␣+·4·8·␣·6·0·1·␣·2·3·4·␣·5·6·7·,·␣e·-·mail·:·␣ja·n·.·kowa·lski·@·gmina·.·pl
PLLuM 12B              (45 tok.)  PE·SE·L │ ␣ │ 4 │ 4 │ 0 │ 5 │ 1 │ 4 │ 0 │ 1 │ 3 │ 5 │ 9 │ , │ ␣tel │ . │ ␣+ │ 4 │ 8 │ ␣ │ 6 │ 0 │ 1 │ ␣ │ 2 │ 3 │ 4 │ ␣ │ 5 │ 6 │ 7 │ , │ ␣e │ -mail │ : │ ␣jan │ .·kow·alski │ @·g·mina │ .pl
Slayer1B               (36 tok.)  P·ES·EL │ ␣4·40·5·140·13·59 │ , │ ␣tel │ . │ ␣+ │ 48 │ ␣60·1 │ ␣23·4 │ ␣5·67 │ , │ ␣e │ - │ mail │ : │ ␣j·an │ . │ kow·al·ski │ @ │ g·mina │ . │ pl
Aster-0.5B (OrisTeam)  (35 tok.)  P·ES·EL │ ␣4·40·5·140·13·59 │ , │ ␣tel │ . │ ␣+ │ 48 │ ␣60·1 │ ␣23·4 │ ␣5·67 │ , │ ␣e │ - │ mail │ : │ ␣ja·n │ . │ kowa·lski │ @ │ g·mina │ . │ pl
GoLLeM (dynaword-32k)  (34 tok.)  P·ES·EL │ ␣44·05·140·13·59 │ , │ ␣te·l │ . │ ␣+ │ 48 │ ␣60·1 │ ␣234 │ ␣5·67 │ , │ ␣e │ - │ mail │ : │ ␣j·an │ . │ kowa·lski │ @ │ g·mina │ . │ pl
NERGAL (XLM-R)         (32 tok.)  ␣PE·SEL │ ␣44·05·140·13·59·, │ ␣tel·. │ ␣+·48 │ ␣·601 │ ␣234 │ ␣·567·, │ ␣e·-·mail·: │ ␣jan·.·ko·wal·ski·@·g·mina·.·pl
HerBERT                (31 tok.)  PE·SE·L</w> │ 44·05·14·0·13·59</w> │ ,</w> │ tel</w> │ .</w> │ +</w> │ 48</w> │ 601</w> │ 234</w> │ 5·67</w> │ ,</w> │ e</w> │ -</w> │ mail</w> │ :</w> │ jan</w> │ .</w> │ kow·alski</w> │ @</w> │ gmina</w> │ .</w> │ pl</w>
```

**Tekst:** `He's␣here.␣They'LL␣go!␣XMLHttpRequest,␣McDonald,␣PESELu,␣ZUS-u`

```
GPT-2                  (24 tok.)  He │ 's │ ␣here │ . │ ␣They │ ' │ LL │ ␣go │ ! │ ␣XML·Http·Request │ , │ ␣McDonald │ , │ ␣P·ES·EL·u │ , │ ␣Z·US │ - │ u
GPT-4 (cl100k)         (20 tok.)  He │ 's │ ␣here │ . │ ␣They │ '·LL │ ␣go │ ! │ ␣XMLHttpRequest │ , │ ␣McDonald │ , │ ␣PE·SEL·u │ , │ ␣Z·US │ -u
GPT-4o (o200k)         (21 tok.)  He's │ ␣here │ . │ ␣They·'·LL │ ␣go │ ! │ ␣XMLHttp │ Request │ , │ ␣Mc │ Donald │ , │ ␣PE·SE·Lu │ , │ ␣Z·US │ -u
Llama 3.3              (20 tok.)  He │ 's │ ␣here │ . │ ␣They │ '·LL │ ␣go │ ! │ ␣XMLHttpRequest │ , │ ␣McDonald │ , │ ␣PE·SEL·u │ , │ ␣Z·US │ -u
Qwen3                  (20 tok.)  He │ 's │ ␣here │ . │ ␣They │ '·LL │ ␣go │ ! │ ␣XMLHttpRequest │ , │ ␣McDonald │ , │ ␣PE·SEL·u │ , │ ␣Z·US │ -u
DeepSeek V3            (23 tok.)  He │ 's │ ␣here │ . │ ␣They │ '·LL │ ␣go │ ! │ ␣XML·Http·Request │ , │ ␣McDonald │ , │ ␣P·ES·EL·u │ , │ ␣Z·US │ -u
Gemma 3                (22 tok.)  He·'·s·␣here·.·␣They·'·LL·␣go·!·␣XMLHttpRequest·,·␣McDonald·,·␣PES·EL·u·,·␣Z·US·-·u
Mistral Nemo (Tekken)  (22 tok.)  He │ 's │ ␣here │ . │ ␣They │ '·LL │ ␣go │ ! │ ␣XMLHttp │ Request │ , │ ␣Mc │ Donald │ , │ ␣PE·SE·Lu │ , │ ␣Z·US │ -u
Bielik 11B v3          (24 tok.)  ␣He·'·s·␣here·.·␣They·'·LL·␣go·!·␣XML·Http·Request·,·␣McDonald·,·␣PE·SEL·u·,·␣Z·US·-·u
Bielik 4.5B v3         (29 tok.)  ␣He·'·s·␣here·.·␣They·'·L·L·␣go·!·␣X·M·L·H·ttp·Re·que·st·,·␣McD·onald·,·␣PESEL·u·,·␣ZUS·-·u
PLLuM 12B              (22 tok.)  He │ 's │ ␣here │ . │ ␣They │ '·LL │ ␣go │ ! │ ␣XMLHttp │ Request │ , │ ␣Mc │ Donald │ , │ ␣PE·SE·Lu │ , │ ␣Z·US │ -u
Slayer1B               (26 tok.)  He │ 's │ ␣here │ . │ ␣They │ ' │ L·L │ ␣go │ ! │ ␣XML·H·ttp·Request │ , │ ␣McD·onald │ , │ ␣P·ES·EL·u │ , │ ␣ZUS │ - │ u
Aster-0.5B (OrisTeam)  (29 tok.)  He │ 's │ ␣here │ . │ ␣The·y │ ' │ LL │ ␣go │ ! │ ␣X·ML·H·ttp·Re·que·st │ , │ ␣Mc·D·onald │ , │ ␣PES·E·Lu │ , │ ␣ZUS │ - │ u
GoLLeM (dynaword-32k)  (30 tok.)  He │ 's │ ␣here │ . │ ␣The·y │ ' │ LL │ ␣go │ ! │ ␣X·M·L·H·ttp·Re·qu·est │ , │ ␣Mc·Donald │ , │ ␣P·ES·E·Lu │ , │ ␣ZUS │ - │ u
NERGAL (XLM-R)         (27 tok.)  ␣He·'·s │ ␣here·. │ ␣They·'·LL │ ␣go·! │ ␣XML·H·tt·p·Re·quest·, │ ␣McDonald·, │ ␣PE·SEL·u·, │ ␣Z·US·-·u
HerBERT                (33 tok.)  He</w> │ '</w> │ s</w> │ here</w> │ .</w> │ The·y</w> │ '</w> │ L·L</w> │ go</w> │ !</w> │ X·M·L·H·tt·p·Re·que·st</w> │ ,</w> │ Mc·Donald</w> │ ,</w> │ PE·SE·L·u</w> │ ,</w> │ ZUS</w> │ -</w> │ u</w>
```

**Tekst:** `Odpowiedź:␣A⏎Answer:A␣(B)␣„cytat”␣—␣ok…`

```
GPT-2                  (25 tok.)  O·dp·ow·ied·�·� │ : │ ␣A │ ⏎ │ Answer │ : │ A │ ␣( │ B │ ) │ ␣�·� │ cy·t·at │ �·� │ ␣— │ ␣ok │ …
GPT-4 (cl100k)         (19 tok.)  O·dp·owied·ź │ : │ ␣A │ ⏎ │ Answer │ :A │ ␣( │ B │ ) │ ␣„ │ cy·tat │ ” │ ␣— │ ␣ok │ …
GPT-4o (o200k)         (19 tok.)  O·dp·owied·ź │ : │ ␣A │ ⏎ │ Answer │ :A │ ␣( │ B │ ) │ ␣„ │ cy·tat │ ” │ ␣— │ ␣ok │ …
Llama 3.3              (19 tok.)  O·dp·owied·ź │ : │ ␣A │ ⏎ │ Answer │ :A │ ␣( │ B │ ) │ ␣„ │ cy·tat │ ” │ ␣— │ ␣ok │ …
Qwen3                  (19 tok.)  O·dp·owied·ź │ : │ ␣A │ ⏎ │ Answer │ :A │ ␣( │ B │ ) │ ␣„ │ cy·tat │ ” │ ␣— │ ␣ok │ …
DeepSeek V3            (20 tok.)  O·dp·ow·ied·ź │ : │ ␣A │ ⏎ │ Answer │ :A │ ␣( │ B │ ) │ ␣„ │ cy·tat │ ” │ ␣— │ ␣ok │ …
Gemma 3                (19 tok.)  Od·powied·ź·:·␣A·⏎·Answer·:·A·␣(·B·)·␣„·cyt·at·”·␣—·␣ok·…
Mistral Nemo (Tekken)  (21 tok.)  O·dp·ow·ied·ź │ : │ ␣A │ ⏎ │ Answer │ :A │ ␣( │ B │ ) │ ␣„ │ c·yt·at │ ” │ ␣— │ ␣ok │ …
Bielik 11B v3          (22 tok.)  ␣O·dp·ow·ied·ź·:·␣A·<0x0A>·An·swer·:·A·␣(·B·)·␣„·cy·tat·”·␣—·␣ok·…
Bielik 4.5B v3         (29 tok.)  ␣Odpowiedź·:·␣A·<0x0A>·A·ns·wer·:·A·␣(·B·)·␣·<0xE2>·<0x80>·<0x9E>·cy·tat·<0xE2>·<0x80>·<0x9D>·␣·<0xE2>·<0x80>·<0x94>·␣ok·<0xE2>·<0x80>·<0xA6>
PLLuM 12B              (21 tok.)  O·dp·ow·ied·ź │ : │ ␣A │ ⏎ │ Answer │ :A │ ␣( │ B │ ) │ ␣„ │ c·yt·at │ ” │ ␣— │ ␣ok │ …
Slayer1B               (18 tok.)  Odpowie·dź │ : │ ␣A │ ⏎ │ Answer │ : │ A │ ␣( │ B │ ) │ ␣„ │ cyt·at │ ” │ ␣— │ ␣ok │ …
Aster-0.5B (OrisTeam)  (20 tok.)  Odpowie·dź │ : │ ␣A │ ⏎ │ A·ns·wer │ : │ A │ ␣( │ B │ ) │ ␣„ │ cy·tat │ ” │ ␣— │ ␣ok │ …
GoLLeM (dynaword-32k)  (20 tok.)  Odpowie·dź │ : │ ␣A │ ⏎ │ A·ns·wer │ : │ A │ ␣( │ B │ ) │ ␣„ │ cy·tat │ ” │ ␣— │ ␣ok │ …
NERGAL (XLM-R)         (17 tok.)  ␣Od·powiedź·: │ ␣A │ ␣Answer·:·A │ ␣(·B·) │ ␣„·cy·tat·” │ ␣— │ ␣ok·...
HerBERT                (17 tok.)  Odpowiedź</w> │ :</w> │ A</w> │ An·swe·r</w> │ :</w> │ A</w> │ (</w> │ B</w> │ )</w> │ „</w> │ cytat</w> │ ”</w> │ —</w> │ ok</w> │ …</w>
```

**Tekst:** `def␣f(x):⏎␣␣␣␣␣␣␣␣return␣x␣␣#␣ok`

```
GPT-2                  (18 tok.)  def │ ␣f │ ( │ x │ ): │ ⏎·␣·␣·␣·␣·␣·␣·␣ │ ␣return │ ␣x │ ␣ │ ␣# │ ␣ok
GPT-4 (cl100k)         (10 tok.)  def │ ␣f │ (x │ ):⏎ │ ␣␣␣␣␣␣␣ │ ␣return │ ␣x │ ␣ │ ␣# │ ␣ok
GPT-4o (o200k)         (10 tok.)  def │ ␣f │ (x │ ):⏎ │ ␣␣␣␣␣␣␣ │ ␣return │ ␣x │ ␣ │ ␣# │ ␣ok
Llama 3.3              (10 tok.)  def │ ␣f │ (x │ ):⏎ │ ␣␣␣␣␣␣␣ │ ␣return │ ␣x │ ␣ │ ␣# │ ␣ok
Qwen3                  (10 tok.)  def │ ␣f │ (x │ ):⏎ │ ␣␣␣␣␣␣␣ │ ␣return │ ␣x │ ␣ │ ␣# │ ␣ok
DeepSeek V3            (10 tok.)  def │ ␣f │ (x │ ):⏎ │ ␣␣␣␣␣␣␣ │ ␣return │ ␣x │ ␣ │ ␣# │ ␣ok
Gemma 3                (12 tok.)  def·␣f·(·x·):·⏎·␣␣␣␣␣␣␣␣·return·␣x·␣␣·#·␣ok
Mistral Nemo (Tekken)  (10 tok.)  def │ ␣f │ (x │ ):⏎ │ ␣␣␣␣␣␣␣ │ ␣return │ ␣x │ ␣ │ ␣# │ ␣ok
Bielik 11B v3          (12 tok.)  ␣def·␣f·(·x·):·<0x0A>·␣␣␣␣␣␣␣·␣return·␣x·␣·␣#·␣ok
Bielik 4.5B v3         (19 tok.)  ␣de·f·␣f·(·x·):·<0x0A>·␣·␣·␣·␣·␣·␣·␣·␣return·␣x·␣·␣#·␣ok
PLLuM 12B              (10 tok.)  def │ ␣f │ (x │ ):⏎ │ ␣␣␣␣␣␣␣ │ ␣return │ ␣x │ ␣ │ ␣# │ ␣ok
Slayer1B               (11 tok.)  def │ ␣f │ ( │ x │ ): │ ⏎␣␣␣␣␣␣␣ │ ␣return │ ␣x │ ␣ │ ␣# │ ␣ok
Aster-0.5B (OrisTeam)  (15 tok.)  de·f │ ␣f │ ( │ x │ ): │ ⏎·␣␣␣␣␣␣␣ │ ␣re·tur·n │ ␣x │ ␣ │ ␣# │ ␣ok
GoLLeM (dynaword-32k)  (11 tok.)  def │ ␣f │ ( │ x │ ): │ ⏎␣␣␣␣␣␣␣ │ ␣return │ ␣x │ ␣ │ ␣# │ ␣ok
NERGAL (XLM-R)         (10 tok.)  ␣de·f │ ␣f·(·x·): │ ␣return │ ␣x │ ␣# │ ␣ok
HerBERT                (13 tok.)  de·f</w> │ f</w> │ (</w> │ x</w> │ )</w> │ :</w> │ re·tur·n</w> │ x</w> │ #</w> │ ok</w>
```
