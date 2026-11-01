"""Test całego toru bez sieci: sztuczne dane, atrapy tokenizerów, udawany serwer API.

    python tests/run_offline_test.py

Kończy się „TEST OK” i kodem 0. Nie dotyka prawdziwych wyników (pracuje w katalogu tymczasowym).
"""
import json
import os
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def count(t, cpt):
    return sum(len(range(0, len(w), max(1, int(cpt)))) for w in t.split())


CPT = {"model-a": 4, "model-b": 2.5, "vendor/free-c:free": 3}


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        data = {"data": [{"id": "model-a", "pricing": {"input": 0.1}}, {"id": "model-b", "pricing": {"input": 0.15}},
                         {"id": "vendor/free-c:free", "pricing": {"prompt": "0", "completion": "0"}}]}
        self._send(200, data)

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        t, m = body["messages"][0]["content"], body["model"]
        if body["max_tokens"] < 16 and m == "model-b":
            return self._send(400, {"error": "max_tokens must be >= 16"})
        self._send(200, {"choices": [{"message": {"content": "a"}}], "usage": {"prompt_tokens": 7 + count(t, CPT[m]), "completion_tokens": 1}})

    def _send(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.end_headers()
        self.wfile.write(b)

    def log_message(self, *a):
        pass


def run(env, *args):
    r = subprocess.run([sys.executable, *args], cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8")
    if r.returncode not in (0,):
        print(r.stdout[-2000:], r.stderr[-3000:])
        raise SystemExit(f"BŁĄD: {' '.join(args)} → kod {r.returncode}")
    return r.stdout


def main():
    work = Path(tempfile.mkdtemp(prefix="tt_test_"))
    srv = HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_port}/v1"
    env = {**os.environ, "TT_WORKDIR": str(work), "TT_CONFIG": str(work / "config"), "PYTHONUTF8": "1",
           "AIHUBMIX_BASE_URL": base, "OPENROUTER_BASE_URL": base, "AIHUBMIX_API_KEY": "x", "OPENROUTER_API_KEY": "y",
           "AIHUBMIX_MAX_SPEND_USD": "1"}
    run(env, "tests/make_fake.py", str(work))
    (work / "config" / "api_models.yaml").write_text(
        "models:\n"
        "  - {id: api_a, label: 'Model A', provider: aihubmix, model: model-a, input_usd_per_m: 0.10, origin: USA}\n"
        "  - {id: api_b, label: 'Model B', provider: aihubmix, model: model-b, input_usd_per_m: 0.15, origin: USA}\n"
        "  - {id: api_x, label: 'Drogi', provider: aihubmix, model: model-x, input_usd_per_m: 3, origin: USA}\n"
        "  - {id: api_c, label: 'Free C', provider: openrouter, model: 'vendor/free-c:free', input_usd_per_m: 0, origin: Chiny}\n",
        encoding="utf-8")
    run(env, "-m", "tt.data")
    run(env, "-m", "tt.measure_local")
    # kalibracja: plik referencyjny z naszych wyników (± szum)
    import random
    import yaml
    names = {l["code"]: l["name_en"] for l in yaml.safe_load(open(work / "config" / "languages.yaml", encoding="utf-8"))["languages"]}
    rng = random.Random(2)
    with open(work / "ref.csv", "w", encoding="utf-8") as f:
        f.write("model,language,fertility,domain,source\n")
        for p in (work / "results" / "local").glob("*.json"):
            r = json.loads(p.read_text(encoding="utf-8"))
            if r.get("calibration"):
                for c, l in r["languages"].items():
                    f.write(f"{r['calibration']},{names[c]},{l['fertility'] + rng.uniform(-0.01, 0.01):.3f},news,SIB-200\n")
    run(env, "-m", "tt.calibrate", "--reference", str(work / "ref.csv"))
    run(env, "-m", "tt.subsample")
    run(env, "-m", "tt.api_models")
    run(env, "-c", "import tt.measure_api as m; m.PROVIDERS['openrouter']['sleep']=0; m.PROVIDERS['aihubmix']['sleep']=0; raise SystemExit(m.main([]))")
    run(env, "-m", "tt.analyze")
    run(env, "-m", "tt.charts")
    run(env, "-m", "tt.report")
    s = json.loads((work / "results" / "summary.json").read_text(encoding="utf-8"))
    assert s["aliases"].get("pllum_12b") == "mistral_nemo", s["aliases"]
    assert s["aliases"].get("api_a") == "llama4_maverick", s["aliases"]
    assert "api_x" not in s["aliases"] and not (work / "results" / "apisum" / "api_x.json").exists(), "model za drogi nie może być mierzony"
    assert "broken" in s["skipped"]
    assert s["calibration"]["passed"]
    assert (work / "README.md").exists() and (work / "publish" / "hf" / "README.md").exists()
    assert len(list((work / "charts").glob("*.png"))) >= 7
    print("TEST OK —", work)
    srv.shutdown()


if __name__ == "__main__":
    main()
