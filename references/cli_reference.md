# MinerU CLI reference

Source: `E:\minerU\MinerU`, version 2.1.0. All commands below assume a working venv and are run from the source root.

## Command-line options

```text
mineru [OPTIONS]

-p, --path PATH              Input file or directory (required). pdf/png/jpg/jpeg/webp/gif.
-o, --output PATH            Output directory (required).
-m, --method [auto|txt|ocr]  Parse method; pipeline backend only. Default auto.
-b, --backend CHOICE         pipeline | vlm-transformers | vlm-sglang-engine | vlm-sglang-client. Default pipeline.
-l, --lang CHOICE            OCR language hint; pipeline only. Default ch.
-u, --url TEXT               Server URL for vlm-sglang-client, e.g. http://127.0.0.1:30000.
-s, --start INTEGER          First page, zero-based. Default 0.
-e, --end INTEGER            Last page, zero-based. Default None (all).
-f, --formula BOOLEAN        Enable formula parsing. Default True.
-t, --table BOOLEAN          Enable table parsing. Default True.
-d, --device TEXT            cpu | cuda | cuda:0 | npu | mps. pipeline only.
--vram INTEGER               Max GPU memory per process in GB. pipeline only.
--source CHOICE              huggingface | modelscope | local. Default huggingface.
-v, --version                Print version.
--help                       Show all options.
```

`--lang` choices: `ch`, `ch_server`, `ch_lite`, `en`, `korean`, `japan`, `chinese_cht`, `ta`, `te`, `ka`, `latin`, `arabic`, `east_slavic`, `cyrillic`, `devanagari`.

## Backend selection

| Backend | Hardware | Notes |
| --- | --- | --- |
| `pipeline` | CPU supported; GPU Turing+ 6 GB recommended | Most general. Uses detection + OCR + table/formula models. |
| `vlm-transformers` | Turing+ 8 GB | End-to-end <1B document VLM via transformers. |
| `vlm-sglang-engine` | Turing+ 8 GB | Faster inference through sglang engine. |
| `vlm-sglang-client` | Client needs only CPU + network | Connect to a separate `mineru-sglang-server`. |

This machine has a Quadro M520 (2 GB, Maxwell), which is below VLM requirements. Use `pipeline` with `-d cpu`.

## Model sources and download

Default source is HuggingFace. On networks where HuggingFace is unavailable, switch to ModelScope:

```bash
mineru -p <input> -o <output> --source modelscope
export MINERU_MODEL_SOURCE=modelscope
```

To pre-download models and use them offline:

```bash
mineru-models-download --help
mineru-models-download -s modelscope -m pipeline
mineru -p <input> -o <output> --source local
```

The downloader writes `~/mineru.json` with the resolved `models-dir`. The config file name can be overridden with `MINERU_TOOLS_CONFIG_JSON`. Relevant config keys:

- `models-dir.pipeline` / `models-dir.vlm` — local model directories
- `latex-delimiter-config.display` / `.inline` — custom formula delimiters
- `llm-aided-config.title_aided` — optional LLM-assisted title hierarchy
- `config_version` — e.g. `1.3.0`

## Other entry points

```bash
mineru-api                       # FastAPI service
mineru-gradio                    # Gradio web UI
mineru-sglang-server --port 30000
mineru -p <input> -o <output> -b vlm-sglang-client -u http://127.0.0.1:30000
```

Python API example: `demo/demo.py` in the source tree.

## Output files

For an input `some.pdf`, the output directory contains:

- `some.md` — primary Markdown result.
- `some_middle.json` — standardized intermediate representation with layout and reading order.
- `some_content_list.json` — ordered content list.
- `some_layout.pdf` — visualization of detected layout blocks with reading-order numbers.
- `some_model.json` — pipeline only. Per-page layout detections with `poly` coordinates and confidence.
- `some_spans.pdf` — pipeline only. Span visualization for quality checks.
- `some_model_output.txt` — VLM backends only. Raw VLM output.
- `images/` — extracted figures.

`_model.json` category IDs: 0 title, 1 plain text, 2 abandon (headers/footers/page numbers), 3 figure, 4 figure caption, 5 table, 6 table caption, 7 table footnote, 8 isolated formula, 9 formula caption, 13 inline formula, 14 isolated formula, 15 OCR text. `poly` is `[x0,y0,x1,y1,x2,y2,x3,y3]` for the four corners.

## Known issues

- Reading order may be partially wrong under extremely complex layouts.
- Vertical text support is limited.
- Tables may misalign rows/columns when highly complex.
- Code blocks are not modeled as a layout category.
- Uncommon list formats may not be recognized.
- Minor-script OCR can be inaccurate (Latin accents, Arabic lookalikes).
- Some formulas may not render in Markdown.
- Comics, art books, primary-school textbooks, and exercise books parse poorly.

Full FAQ: `docs/FAQ_zh_cn.md` in the source tree. Output details: `docs/output_file_zh_cn.md`.
