# tools/pack_cros.py
# -*- coding: utf-8 -*-
import os, json, hashlib, zipfile
from datetime import datetime

INCLUDE = ["tools", "solutions", "cfg.yaml", "README.md"]
OUT_DIR = "output"

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(131072), b""):
            h.update(ch)
    return h.hexdigest()

def walk(paths):
    for path in paths:
        if os.path.isdir(path):
            for b,_,fs in os.walk(path):
                for fn in fs:
                    yield os.path.join(b, fn)
        elif os.path.isfile(path):
            yield path

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = os.path.join(OUT_DIR, f"act_cros_{ts}.zip")

    files = list(walk([OUT_DIR] + INCLUDE))
    sbom = {"timestamp": datetime.now().isoformat(timespec="seconds"),
            "files": [{"path": f, "sha256": sha256(f)} for f in files]}
    sbom_path = os.path.join(OUT_DIR, f"sbom_{ts}.json")
    with open(sbom_path, "w", encoding="utf-8") as f:
        json.dump(sbom, f, ensure_ascii=False, indent=2)
    files.append(sbom_path)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(f, os.path.relpath(f))

    with open(zip_path + ".sha256", "w", encoding="utf-8") as f:
        f.write(sha256(zip_path) + "\n")
    print("[OK] CROS pack:", zip_path)

if __name__ == "__main__":
    main()