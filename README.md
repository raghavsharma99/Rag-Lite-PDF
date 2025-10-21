# 📚 Rag-Lite-PDF


> ⚡️ Lightweight retrieval-augmented generation over your PDF libraries with nothing more than a single Python script.

## 🧭 Table of Contents
- [✨ Features](#-features)
- [🗂️ Project Layout](#-project-layout)
- [🚀 Quickstart](#-quickstart)
- [🖼️ Use Case Walkthroughs](#-use-case-walkthroughs)
- [🧠 How It Works](#-how-it-works)
- [⚙️ CLI Options](#-cli-options)
- [🧪 Validation Tips](#-validation-tips)
- [🛣️ Roadmap Ideas](#-roadmap-ideas)
- [🙌 Acknowledgements](#-acknowledgements)

## ✨ Features
- 🔍 Reliable BM25 retrieval keeps the referenced paragraphs grounded and transparent.
- 🧾 Paragraph-aware PDF loader preserves page numbers, documents, and inline citations.
- 🗃️ Three ingestion modes (`--pdf`, `--corpus`, `--group`) cover single files, plain-text notes, or folders of PDFs.
- 🤖 Powered by `ChatOpenAI` with GPT-4o Mini for concise, cited answers.
- 🛠️ Zero-framework footprint: one CLI script, readable pipeline, ready to extend.

## 🗂️ Project Layout
- `main.py` — complete CLI workflow (loading, retrieval, LLM answer).
- `requirements.txt` — minimal dependencies.
- `data/` — sample PDF manuals and reports you can query immediately.
- `data/ncert-geography-class-IX/` — NCERT Class IX Geography chapters sourced from the [official textbook page](https://ncert.nic.in/textbook.php?iess1=2-6).
- `data/project-brief.txt` — tiny plain-text corpus for demo questions.
- `data/candy-tree-story.txt` - tiny plain-text corpus for demo questions.

## 🚀 Quickstart

```bash
git clone <repo-url>
cd Rag-Lite-PDF
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file containing your OpenAI key (never commit it):

```dotenv
OPENAI_API_KEY=sk-your-key-here
```

Now ask questions with any of the supported ingestion modes:

```bash
python main.py --pdf data/ncert-geography-class-IX/iess104.pdf --ask "What shapes India's climate?"
```

> 💡 Tip: extraction works best on short to medium PDFs with selectable text. Scanned documents should be OCR’d first.

## 🖼️ Use Case Walkthroughs

### 1. Single PDF mode
Ask focused questions against one document.

```bash
python main.py --pdf data/ncert-geography-class-IX/iess104.pdf --ask "What is the focus of Chapter 4?"
```

![Single PDF demo](docs/screenshots/single-pdf.svg)

### 2. Plain-text corpus mode
Point the CLI at a blank-line-separated text file (see `examples/corpus/product-brief.txt`).

```bash
python main.py --corpus examples/corpus/product-brief.txt --ask "Who benefits from this tool?"
```

![Text corpus demo](docs/screenshots/text-corpus.svg)

### 3. PDF folder mode
Batch-load multiple PDFs and search across the whole stack.

```bash
python main.py --group data/ncert-geography-class-IX --ask "What are the major physiographic divisions in India?"
```

![PDF group demo](docs/screenshots/pdf-group.svg)

## 🧠 How It Works
- **Load** — PDFs are scanned page by page; paragraphs shorter than 40 characters are skipped to reduce noise.
- **Chunk** — Long blocks are split further, with page numbers and document paths preserved for citations.
- **Index** — Tokens are lowercased and indexed with BM25 for fast lexical retrieval.
- **Generate** — Context is formatted into a numbered prompt and passed to GPT-4o Mini via LangChain with inline citation instructions.
- **Report** — Answers include a source appendix so you can trace every sentence back to a page.

## ⚙️ CLI Options

| Flag | Description |
| --- | --- |
| `--pdf PATH` | Query a single PDF file. |
| `--corpus PATH` | Query a plain-text file, split by blank lines. |
| `--group DIR` | Query every PDF inside a directory. |
| `--ask "QUESTION"` | (Required) The natural-language question to answer. |
| `--k N` | Top-k paragraphs to blend into the prompt (default: `6`). |

> Exactly one of `--pdf`, `--corpus`, or `--group` must be supplied.

## 🧪 Validation Tips
- Run a quick smoke test: `python main.py --pdf data/dell-P2018H-user-guide.pdf --ask "How do I access the OSD?"`.
- Inspect the cited paragraphs to confirm they're relevant before trusting the answer.
- Tune `--k` upwards for broader context, or down for faster responses.
- Add your own PDFs into `data/` (or point to another directory) to expand coverage.

## 🛣️ Roadmap Ideas
- Swap BM25 with a hybrid embedding retriever for semantic matching.
- Add optional local LLM backends for offline answers.
- Stream responses token-by-token for a live terminal feel.
- Package as a small FastAPI service or Gradio demo with the same core pipeline.

## 🙌 Acknowledgements
- Built on the shoulders of [`pypdf`](https://pypi.org/project/pypdf/), [`rank-bm25`](https://pypi.org/project/rank-bm25/), and [`langchain-openai`](https://python.langchain.com/docs/integrations/chat/openai).
- Sample PDFs belong to their respective publishers; use them only for testing and educational purposes.

Enjoy building your own rapid-answer notebook! 💬✨

