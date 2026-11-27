# mineru-pdf

A [WorkBuddy](https://www.workbuddy.cn/) skill that converts PDFs into structured Markdown / JSON using a local [MinerU 2.1.0](https://github.com/opendatalab/MinerU) installation.

## What it does

MinerU turns layout-heavy PDFs into machine-readable data: it removes headers/footers, reconstructs reading order, preserves heading hierarchy, converts tables to HTML and formulas to LaTeX, and OCRs scanned pages. This skill wraps that capability so an agent can invoke it reliably, including environment checks and repair.

## Files

- `SKILL.md` - skill definition, trigger conditions, decision guidance, and workflow
- `scripts/check_env.py` - environment readiness report (READY / NOT READY with fixes)
- `scripts/setup_env.sh` - rebuild venv, install dependencies, download pipeline models
- `scripts/parse_pdf.sh` - parse a file or directory with safe defaults
- `references/cli_reference.md` - CLI options, backends, output schema, config, troubleshooting

## Install

Copy this folder into `~/.workbuddy/skills/mineru-pdf/` (user-level) or `<project>/.workbuddy/skills/mineru-pdf/` (project-level).

## Environment notes

The skill was authored against a Windows machine with MinerU 2.1.0 at `E://minerU//MinerU`, system Python 3.13, and a Quadro M520 (2 GB). Paths and hardware notes in the skill are machine-specific; adjust `MINERU_DIR` and backend selection for your own setup. The `pipeline` backend on CPU is the safest default; VLM backends need Turing+ and 8 GB VRAM.

## License

The skill code is provided as-is. MinerU itself is AGPL-3.0 licensed.
