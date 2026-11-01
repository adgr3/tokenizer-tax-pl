"""Dane i konfiguracja testowe: sztuczny SIB-200 (25 języków × 204 zdania) i atrapy tokenizerów."""
import json, random, shutil, sys
from pathlib import Path

work = Path(sys.argv[1]); cfg = work / "config"
shutil.rmtree(work, ignore_errors=True)
(work / "data" / "sib200").mkdir(parents=True); cfg.mkdir(parents=True)
root = Path(__file__).resolve().parent.parent
shutil.copy(root / "config" / "languages.yaml", cfg)
shutil.copy(root / "config" / "polish_sources.yaml", cfg)
import yaml
langs = yaml.safe_load(open(cfg / "languages.yaml", encoding="utf-8"))["languages"]
rng = random.Random(1)
alph = {"łaciński": "abcdefghijklmnoprstuwyząęółśżźćń", "cyrylica": "абвгдежзийклмнопрстуфхцчшщюя", "grecki": "αβγδεζηθικλμνξοπρστυφχψω"}
for i, l in enumerate(langs):
    # języki dalej na liście mają dłuższe słowa → więcej tokenów na słowo (jak w danych prawdziwych)
    mean_len = 4 + i * 0.12
    a = alph[l["script"]]
    with open(work / "data" / "sib200" / f"{l['code']}.jsonl", "w", encoding="utf-8") as f:
        for idx in range(204):
            words = ["".join(rng.choice(a) for _ in range(max(1, int(rng.gauss(mean_len, 2))))) for _ in range(rng.randint(12, 30))]
            f.write(json.dumps({"index_id": idx, "text": " ".join(words) + "."}, ensure_ascii=False) + "\n")
toks = [
  {"id": "llama4_maverick", "label": "Llama 4 Maverick", "kind": "mock", "repo": "m", "chars_per_token": 4, "group": "global", "origin": "USA", "calibration": "Llama 4 Maverick"},
  {"id": "qwen3", "label": "Qwen3", "kind": "mock", "repo": "m", "chars_per_token": 3, "group": "global", "origin": "Chiny", "calibration": "Qwen3 32B"},
  {"id": "gpt4o", "label": "GPT-4o (o200k)", "kind": "mock", "repo": "m", "chars_per_token": 5, "group": "global", "origin": "USA", "calibration": "GPT-4o"},
  {"id": "mistral_nemo", "label": "Mistral Nemo", "kind": "mock", "repo": "m", "chars_per_token": 6, "group": "eu", "origin": "UE"},
  {"id": "pllum_12b", "label": "PLLuM 12B", "kind": "mock", "repo": "m", "chars_per_token": 6, "group": "pl", "origin": "Polska", "polish_model": True},
  {"id": "slayer1b", "label": "Slayer1B", "kind": "mock", "repo": "m", "chars_per_token": 7, "group": "pl", "origin": "Polska", "polish_model": True, "bench_ref": True},
  {"id": "eurollm", "label": "EuroLLM", "kind": "mock", "repo": "m", "chars_per_token": 2, "group": "eu", "origin": "UE", "bench_ref": True},
  {"id": "broken", "label": "Zepsuty", "kind": "hf", "repo": "nie/istnieje", "group": "global", "origin": "USA"},
  {"id": "nergal", "label": "NERGAL (XLM-R)", "kind": "mock", "repo": "m", "chars_per_token": 3.5, "group": "encoder", "origin": "Polska"},
  {"id": "herbert", "label": "HerBERT", "kind": "mock", "repo": "m", "chars_per_token": 4.5, "group": "encoder", "origin": "Polska"},
]
yaml.safe_dump({"tokenizers": toks}, open(cfg / "tokenizers.yaml", "w", encoding="utf-8"), allow_unicode=True, sort_keys=False)
yaml.safe_dump({"models": []}, open(cfg / "api_models.yaml", "w", encoding="utf-8"))
print("ok", work)
