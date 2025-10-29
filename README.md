# 📚 Rag-Lite-PDF


> ⚡️ Lightweight retrieval-augmented generation over your PDF libraries with nothing more than a single Python script.

## 🧭 Table of Contents
- [✨ Features](#-features)
- [🗂️ Project Layout](#-project-layout)
- [🚀 Quickstart](#-quickstart)
- [🖼️ Use Case Walkthroughs](#-use-case-walkthroughs)
- [🧠 How It Works](#-how-it-works)
- [⚙️ CLI Options](#-cli-options)
- [🧪 Evaluation Workflow](#-evaluation-workflow)
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
- `eval.py` — evaluation system for measuring RAG performance across multiple questions.
- `requirements.txt` — minimal dependencies.
- `data/` — sample PDF manuals and reports you can query immediately.
- `data/ncert-geography-class-IX/` — NCERT Class IX Geography chapters sourced from the [official textbook page](https://ncert.nic.in/textbook.php?iess1=2-6).
- `data/project-brief.txt` — tiny plain-text corpus for demo questions.
- `data/candy-tree-story.txt` - tiny plain-text corpus for demo questions.
- `eval/questions.jsonl` — sample evaluation questions for testing.
- `results/` — evaluation outputs (CSV metrics and JSONL answers).

## 🚀 Quickstart

```bash
git clone https://github.com/raghavsharma99/Rag-Lite-PDF.git
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
python main.py --corpus data/candy-tree-story.txt --ask "How did Mira decide to keep the secret safe?"
```

![Text corpus demo](docs/screenshots/text-corpus.svg)

### 3. PDF folder mode
Batch-load multiple PDFs and search across the whole stack.

```bash
python main.py --group data/ncert-geography-class-IX --ask "What are the major physiographic divisions in India? --k 2"
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

## ⚖️ Evaluation Workflow

The project includes a comprehensive evaluation system to measure RAG performance across multiple questions and documents.

### Running Evaluations

```bash
# Evaluate on a PDF group with default questions
python eval.py --group data/ncert-geography-class-IX --k 3

# Use custom questions file
python eval.py --group data/ncert-geography-class-IX --qfile eval/custom_questions.jsonl

# Enable LLM judge for grounding assessment
python eval.py --group data/ncert-geography-class-IX --judge --k 5
```

### Evaluation Metrics

The system tracks several key metrics:

- **Citation Rate**: Percentage of answers that include proper citations `[1]`, `[1 p.5]`
- **Keyword Coverage**: How many expected keywords appear in the generated answers
- **Source Accuracy**: Whether answers reference the correct source documents
- **LLM Judge Score**: Optional 1-5 rating of answer grounding (when `--judge` flag is used)

### Output Files

Evaluations generate two output files:

1. **`results/summary.csv`** - Metrics and analysis data
2. **`results/summary_answers.jsonl`** - Raw Q&A pairs for manual review

#### Sample Output Files

**`summary.csv`** - Evaluation metrics:

| qid | source                                    | has_citation | keyword_hits | keyword_coverage | has_correct_source | judge_grounding_1to5 |
| --- | ----------------------------------------- | ------------ | ------------ | ---------------- | ------------------ | -------------------- |
| q1  | data/ncert-geography-class-IX/iess101.pdf | 1            | 1            | 1.0              | 0                  | 5                    |
| q2  | data/ncert-geography-class-IX/iess105.pdf | 1            | 5            | 1.0              | 1                  | 5                    |
| q3  | data/ncert-geography-class-IX/iess103.pdf | 1            | 0            | 0.0              | 1                  | 1                    |
| q4  | data/ncert-geography-class-IX/iess102.pdf | 1            | 2            | 0.667            | 1                  | 5                    |


**`summary_answers.jsonl`** - Raw Q&A pairs:
```json
{"qid": "q1", "question": "What is the area of India?. Cite.", "answer": "The area of India is approximately 3.28 million square kilometers, which accounts for 2.4 percent of the world's area [1 p.1].\n\nSources:\n[1 p.1 data/ncert-geography-class-IX/iess106.pdf]\n[2 p.1 data/ncert-geography-class-IX/iess104.pdf]\n[3 p.5 data/ncert-geography-class-IX/iess105.pdf]\n[4 p.10 data/ncert-geography-class-IX/iess104.pdf]\n[5 p.1 data/ncert-geography-class-IX/iess102.pdf]"}
{"qid": "q2", "question": "Waht are the types of veegation in India?", "answer": "India has several major types of natural vegetation, which are identified as follows:\n\n1. Tropical Evergreen Forests\n2. Tropical Deciduous Forests\n3. Tropical Thorn Forests and Scrubs\n4. Montane Forests\n5. Mangrove Forests [1 p.5].\n\nSources:\n[1 p.1 data/ncert-geography-class-IX/iess105.pdf]\n[2 p.9 data/ncert-geography-class-IX/iess105.pdf]\n[3 p.10 data/ncert-geography-class-IX/iess104.pdf]\n[4 p.8 data/ncert-geography-class-IX/iess103.pdf]\n[5 p.1 data/ncert-geography-class-IX/iess106.pdf]"}
```

### Question Format

Create evaluation questions in JSONL format:

```json
{"id": "q1", "question": "What shapes India's climate?", "expected_keywords": ["monsoon", "latitude", "altitude"], "document": "iess104.pdf"}
{"id": "q2", "question": "Name the major physiographic divisions", "expected_keywords": ["Himalayas", "Indo-Gangetic", "Peninsular"], "document": "iess106.pdf"}
```

## 🧪 Validation Tips
- Run a quick smoke test: `python main.py --pdf data/dell-P2018H-user-guide.pdf --ask "How do I access the OSD?"`.
- Inspect the cited paragraphs to confirm they're relevant before trusting the answer.
- Tune `--k` upwards for broader context, or down for faster responses.
- Add your own PDFs into `data/` (or point to another directory) to expand coverage.
- Use the evaluation workflow to systematically test performance across your document collection.

## 🛣️ Roadmap Ideas
- Swap BM25 with a hybrid embedding retriever for semantic matching.
- Add optional local LLM backends for offline answers.
- Stream responses token-by-token for a live terminal feel.
- Package as a small FastAPI service or Gradio demo with the same core pipeline.

## 🙌 Acknowledgements
- Built on the shoulders of [`pypdf`](https://pypi.org/project/pypdf/), [`rank-bm25`](https://pypi.org/project/rank-bm25/), and [`langchain-openai`](https://python.langchain.com/docs/integrations/chat/openai).
- Sample PDFs belong to their respective publishers; use them only for testing and educational purposes.

Enjoy building your own rapid-answer notebook! 💬✨

