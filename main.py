import os
import argparse
from typing import List, Tuple, Dict
from dotenv import load_dotenv
from rank_bm25 import BM25Okapi
from langchain_openai import ChatOpenAI

# PDF/TEXT EXTRACTION

def load_text_corpus(path:str) -> List[Dict]:
    """Load a plain text file split by blank lines; no page numbers"""
    # Read .txt path paragraphs 
    with open(path, 'r', encoding = 'utf-8') as f:
        raw = f.read()
    paras = [[p.strip() for p in raw.split('\n\n') if p.strip()]]
    return [{'text':p, 'page':None} for p in paras]

def load_pdf_corpus(pdf_path: str) -> List[Dict]:
    """Extract text per page and split into paragraphs; keep page numbers."""
    # Read .pdf file
    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    records: List[Dict] = []
    for p_idx, page in enumerate(reader.pages, start=1):
        # pypdf text in reading order; short PDFs work well
        page_text = (page.extract_text() or "").strip()
        if not page_text:
            continue
        # normalize spacing and split on blank lines
        blocks = [b.strip() for b in page_text.replace("\r", "\n").split("\n\n") if b.strip()]
        # further split longer blocks 
        for b in blocks:
            if len(b) > 1500:
                parts = [x.strip() for x in b.split("\n\n") if x.strip()]
            else:
                parts = [b]
            for part in parts:
                if len(part) < 40:
                    # Discard shorter fragments
                    continue
                records.append({'text':part, 'page':p_idx})
    return records

# RETRIEVAL

def tokenize(text:str) -> List[str]:
    return text.lower().split()

def build_bm25(records: List[Dict]) -> Tuple[BM25Okapi, List[List[str]]]:
    tokenized = [tokenize(r["text"]) for r in records]
    return BM25Okapi(tokenized), tokenized

def retrieve(bm25: BM25Okapi, records: List[Dict],
            query:str, k:int=6) -> List[Tuple[int, Dict]]:
    scores = bm25.get_scores(tokenize(query))
    idxs = sorted(range(len(scores)), key = lambda i: scores[i], reverse = True)[:k]
    return [(i, records[i]) for i in idxs]

def format_context(hits: List[Tuple[int, Dict]]) -> str:
    blocks = []
    for (i, r) in hits:
        tag = f"[{i+1}]"
        if r["page"]:
            tag = f"[{i+1}] p.{r['page']}"
        blocks.append(f"{tag} {r['text'][:1200]}")
    return "\n\n.join(blocks)"
        
PROMPT = """You are a careful analyst. Answer ONLY using the numbered context.
Cite paragraphs inline like [1] or [1 p.5]. If the answer is not in contetx, say you lack sufficient context.

Question: {q}

Context: {ctxt}

Answer with citations:
"""

# ANSWER

def answer(query: str, records: List[Dict], bm25: BM25Okapi,
tokenized_corpus: List[List[str]], k: int = 6) -> str:
    hits = retrieve(bm25, tokenized_corpus, records, query, k=k)
    ctx = format_context(hits)
    llm = ChatOpenAI(model = "gpt-40-mini")
    resp = llm.invoke(PROMPT.format(q=query, ctx=ctx)).content
    src_lines = []
    for i, r in hits:
        pg = f" p.{r['page']}" if r['page'] else ""
        src_lines.append(f"[{i+1}{pg} paragraph {i+1}]")
    return f"{resp}\n\nSources:\n" + "\n".join(src_lines)

# CLI
def cli():
    parser = argparse.ArgumentParser()
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("--pdf", type=str, help="Path to a short PDF file")
    grp.add_argument("--corpus", type=str, help="Path to a plain text file (blank-line paragraphs)")
    parser.add_argument("--ask", type=str, required=True, help = "Your Question")
    parser.add_argument("--k",type=int, default=6, help="Top-k paragraphs to retrieve")
    args = parser.parse_args

    if args.pdf:
        records = load_pdf_corpus(args.pdf)
    else:
        records = load_text_corpus(args.corpus)

    if not records:
        raise SystemExit("No extractable text found.")
    
    bm25, tok = build_bm25(records)
    print(answer(args.ask, records, bm25, tok, k=args.k))

if __name__ == "__main__":
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("Missing OPENAI_API_KEY in .env")
    cli()




