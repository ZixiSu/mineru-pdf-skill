---
name: mineru-pdf
description: Convert PDF and image documents into structured Markdown, JSON, and OCR text with the local MinerU 2.1.0 installation. This skill should be used when a user asks to parse, extract, convert, or OCR a PDF; build a RAG or knowledge-base corpus from documents; extract tables or LaTeX formulas; or batch-process scanned, multi-column, or complex-layout documents. Prefer this skill when stable structured output, offline/private processing, or reproducible results matter, rather than when merely asking a few questions about a short document.
agent_created: true
---

# MinerU PDF parsing

## Overview

MinerU converts PDFs into machine-readable Markdown and JSON: it removes headers/footers, reconstructs human reading order across columns, preserves heading hierarchy, converts tables to HTML and formulas to LaTeX, and OCRs scanned pages. Use it through the local source checkout at `E:\minerU\MinerU` (version 2.1.0).

## Decide between MinerU and direct multimodal reading

- **Read the PDF directly with a vision-capable model** when the task is a few pages of Q&A, summarization, or exploratory reading, and output randomness is acceptable.
- **Use this skill** when the task involves batch processing, RAG/knowledge-base ingestion, required stable structure, coordinate-level traceability, offline/private processing, or heavy OCR/table/formula extraction. MinerU's structured output is also the preferred input for downstream embedding and fine-tuning pipelines.

## Local environment facts (verify before relying on them)

- Source: `E:\minerU\MinerU`, v2.1.0, commit `5f1175f`, on `master`.
- The bundled `venv/` is **broken**: `pyvenv.cfg` points to `C:\Python313\python.exe` and `F:\minerU\MinerU\venv`, neither of which exists here. Only `pip` is installed in `site-packages`.
- No model weights are downloaded and `~/mineru.json` does not exist yet.
- GPU is a Quadro M520 (2 GB, Maxwell). VLM backends require Turing+ and 8 GB, so VLM is not viable. Use the `pipeline` backend on **CPU**.
- System Python is 3.13.14; the project supports 3.10–3.13.
- Git operations on `E:\minerU\MinerU` need `git -c safe.directory='E:/minerU/MinerU' ...` because the directory ownership is not recorded on this filesystem. Do not change global Git config.

## Workflow

### 1. Check the environment

Always run the environment check before parsing:

```bash
python "C:/Users/30989/.workbuddy/skills/mineru-pdf/scripts/check_env.py"
```

The script reports `STATUS: READY` or `STATUS: NOT READY` with concrete fix hints. It checks the source tree, venv interpreter, CLI entry point, model config, model directories, and GPU capability.

### 2. Repair the environment when NOT READY

From Git Bash, run the setup script. It recreates the venv with the system Python, installs the pipeline extras from a China-friendly mirror, and downloads the pipeline models from ModelScope:

```bash
bash "C:/Users/30989/.workbuddy/skills/mineru-pdf/scripts/setup_env.sh"
```

Notes for running setup:

- This is a large, long-running operation (torch plus model weights, several GB). Run it in the background and wait for completion rather than polling.
- `MINERU_EXTRAS=core` can be set to install the VLM/API/Gradio extras as well, but the current GPU cannot run VLM inference.
- To use HuggingFace instead of ModelScope, set `MINERU_MODEL_SOURCE=huggingface`.
- Re-run the check script afterward and proceed only when it reports READY.

### 3. Parse documents

Use the wrapper script, which selects the pipeline backend, CPU device, and an appropriate model source automatically:

```bash
bash "C:/Users/30989/.workbuddy/skills/mineru-pdf/scripts/parse_pdf.sh" "<input_pdf_or_dir>" "<output_dir>"
```

An optional third argument selects the backend (`pipeline` by default). Input may be a single PDF/image file or a directory; supported suffixes are pdf, png, jpg, jpeg, webp, gif. Page ranges can be passed by calling the CLI directly with `-s` and `-e` (zero-based).

### 4. Verify and report

- Confirm the expected output files exist under the output directory.
- Read the `.md` result and spot-check headings, tables, formulas, and reading order.
- For quality issues, inspect `<name>_layout.pdf` and `<name>_spans.pdf`.
- Report the output path, page count if known, and any parsing limitations observed.

## Direct CLI reference

```bash
# From the source tree with a working venv
venv/Scripts/mineru.exe -p <input> -o <output> -b pipeline -d cpu --source modelscope
venv/Scripts/mineru.exe --help
venv/Scripts/mineru.exe -p <input> -o <output> -s 0 -e 4   # pages 0-4 only
venv/Scripts/mineru.exe -p <input> -o <output> -l en       # OCR language hint
```

Key options: `-p/--path`, `-o/--output`, `-m/--method auto|txt|ocr`, `-b/--backend pipeline|vlm-transformers|vlm-sglang-engine|vlm-sglang-client`, `-l/--lang`, `-s/--start`, `-e/--end`, `-f/--formula`, `-t/--table`, `-d/--device`, `--vram`, `--source huggingface|modelscope|local`. A full option table, backend guidance, output file descriptions, and config details live in `references/cli_reference.md`; load it when exact flags, output formats, or troubleshooting details are needed.

## Output expectations

Each input document produces a directory containing `<name>.md`, `<name>_middle.json`, `<name>_content_list.json`, and `<name>_layout.pdf`. The pipeline backend additionally emits `<name>_model.json` and `<name>_spans.pdf`, plus an `images/` directory for extracted figures. The VLM backend emits `<name>_model_output.txt` instead of `_model.json`.

## Known limitations

Reading order may break down in extreme layouts; vertical text support is limited; uncommon list formats and code blocks may not be recognized; complex tables can misalign rows/columns; minor scripts may produce OCR inaccuracies; some formulas may not render in Markdown. Consult `references/cli_reference.md` for the full list and FAQ pointers.

## Resources

- `scripts/check_env.py` — environment readiness report.
- `scripts/setup_env.sh` — rebuild venv, install dependencies, download pipeline models.
- `scripts/parse_pdf.sh` — parse a file or directory with safe defaults.
- `references/cli_reference.md` — detailed CLI options, backends, output schema, config, and troubleshooting.
