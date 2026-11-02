Regex przed BPE decyduje z góry, co w ogóle może być jednym tokenem, i jest pisany pod angielski: w dużych
tokenizerach z regexem (GPT-4o, Llama 3.3, DeepSeek V3, Qwen3) ok. 95% angielskich słów to jeden token, a polskich
tylko 32–41%. Średnio po 33 tokenizerach LLM z regexem to 81% słów angielskich wobec 43% polskich. Najwięcej polskich
słów w jednym tokenie mają tokenizery uczone na polskim (polish-gpt2 80%, Aster-0.5B 74%, Slayer1B 67%), choć
używają najstarszego regexu GPT-2, więc zysk daje słownik, a nie regex. Różnice między regexami widać głównie
w liczbach i interpunkcji: „2026” to jeden kawałek w GPT-2, `202 │ 6` w GPT-4o, Llamie 3 i DeepSeeku, a `2 │ 0 │ 2 │ 6`
w Qwen3, Mistralu Nemo, PLLuM 12B, Gemmie i Bielikach v3, co ma znaczenie przy testach z matematyki. Spacja zawsze
należy do następnego słowa, dlatego „A” i „␣A” to różne tokeny: w Bielikach v3 i EuroLLM (SentencePiece), a także
w LFM i Qwen3.5 (sklejone `:A`) odpowiedź bez spacji jest w kontekście kodowana inaczej niż osobno, natomiast
w Slayer1B i Asterze — tak samo. Nowa reguła GPT-4o z grafiki tnie słowa na granicy małych i wielkich liter
(`XMLHttp │ Request`, `Mc │ Donald`); dla polskiego zmienia niewiele, bo `PESELu` zostaje jednym kawałkiem, a `ZUS-u`
rozpada się we wszystkich tokenizerach.
