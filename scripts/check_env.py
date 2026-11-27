#!/usr/bin/env python3
"""Report whether the local MinerU installation is ready to parse PDFs."""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_ROOT = r"E:\minerU\MinerU"


def run(cmd, cwd=None, timeout=60):
    try:
        proc = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True,
            timeout=timeout, encoding="utf-8", errors="replace",
        )
        return proc.returncode, (proc.stdout or "").strip(), (proc.stderr or "").strip()
    except FileNotFoundError:
        return 127, "", "executable not found"
    except subprocess.TimeoutExpired:
        return 124, "", "timed out"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mineru-dir", default=os.environ.get("MINERU_DIR", DEFAULT_ROOT))
    args = parser.parse_args()

    root = Path(args.mineru_dir)
    issues = []
    print(f"MinerU root: {root}")

    if not root.is_dir():
        print("[MISSING] source directory")
        print("STATUS: NOT READY")
        return 1

    version = "unknown"
    version_file = root / "mineru" / "version.py"
    if version_file.exists():
        for line in version_file.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("__version__"):
                version = line.split("=", 1)[1].strip().strip('"').strip("'")
                break
    print(f"[OK] source tree, version {version}")

    is_windows = os.name == "nt"
    venv_py = root / "venv" / ("Scripts/python.exe" if is_windows else "bin/python")
    cli = root / "venv" / ("Scripts/mineru.exe" if is_windows else "bin/mineru")

    if not venv_py.exists():
        print("[MISSING] venv interpreter")
        issues.append("recreate venv with scripts/setup_env.sh")
    else:
        code, out, err = run([str(venv_py), "-c", "import sys; print(sys.executable)"], cwd=str(root))
        if code == 0:
            print(f"[OK] venv interpreter: {out.splitlines()[0] if out else venv_py}")
        else:
            print(f"[BROKEN] venv interpreter: {err[:200]}")
            issues.append("recreate venv with scripts/setup_env.sh")

    if cli.exists():
        code, out, err = run([str(cli), "--version"], cwd=str(root))
        if code == 0:
            print(f"[OK] CLI entry point: {out}")
        else:
            print(f"[BROKEN] CLI entry point: {err[:200]}")
            issues.append("reinstall mineru into the venv")
    else:
        print("[MISSING] CLI entry point (venv/Scripts/mineru.exe)")
        issues.append("install mineru into the venv")

    if venv_py.exists():
        code, out, err = run(
            [str(venv_py), "-c", "import torch, transformers, click; print('deps ok')"],
            cwd=str(root),
        )
        if code == 0:
            print("[OK] core dependencies importable")
        else:
            last = err.strip().splitlines()[-1][:160] if err.strip() else "unknown error"
            print(f"[MISSING] core dependencies: {last}")
            issues.append("run pip install -e .[pipeline] inside the venv")

    cfg_name = os.getenv("MINERU_TOOLS_CONFIG_JSON", "mineru.json")
    cfg = Path.home() / cfg_name
    if cfg.exists():
        try:
            data = json.loads(cfg.read_text(encoding="utf-8"))
            pipeline_dir = data.get("models-dir", {}).get("pipeline", "")
            if pipeline_dir and Path(pipeline_dir).exists():
                print(f"[OK] pipeline models configured: {pipeline_dir}")
            else:
                print("[MISSING] models-dir.pipeline is empty or missing")
                issues.append("run mineru-models-download -s modelscope -m pipeline")
        except Exception as exc:
            print(f"[BROKEN] config file {cfg}: {exc}")
            issues.append("remove and regenerate ~/mineru.json")
    else:
        print(f"[MISSING] model config {cfg}")
        issues.append("run mineru-models-download -s modelscope -m pipeline")

    if shutil.which("nvidia-smi"):
        code, out, err = run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"]
        )
        print(f"[INFO] GPU: {out if code == 0 else 'nvidia-smi failed'}")
        print("[INFO] VLM backends need Turing+ and 8 GB; use pipeline on CPU here")
    else:
        print("[INFO] no nvidia-smi found; CPU pipeline only")

    if issues:
        print("\nFIXES:")
        for item in dict.fromkeys(issues):
            print(f"  - {item}")
        print("\nSTATUS: NOT READY")
        return 1

    print("\nSTATUS: READY")
    return 0


if __name__ == "__main__":
    sys.exit(main())
