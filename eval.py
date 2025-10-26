# ---------------------- IMPORTS & SETUP ---------------------- 
import os
import re
import csv
import json
import argparse
from typing import List, Dict
from dotenv import load_dotenv

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import load_pdf_group, build_bm25, answer

# Regex to detect citations like [1] or [1 p.5]
CITATION_RE = re.compile(r"\[\d+(?:\s*p\.\d+)?\]")

# ---------------------- DATA LOADING ---------------------- 

def load_questions(path:str) -> List[Dict]:
    """Loads eval questions from questions JSON"""
    qs = []
    with open(path, "r", encoding = "utf-8") as f:
        for line in f:
            if line.strip():
                qs.append(json.loads(line))

    return qs

# ---------------------- EVALUATION METRICS ---------------------- 

def keyword_hits(ans: str, keywords: List[str]) -> int:
    """Returns number of target keywords included in the answer"""
    if not keywords:
        return 0

    a = ans.lower()
    return sum(1 for k in keywords if k.lower() in a)


def llm_judge_score(question: str, answer_text: str) -> int:
    """Uses an LLM to rate answer grounding with a 1-5 score (optional judge mode)"""
    
    try:
        from langchain_openai import ChatOpenAI
    except Exception:
        return -1
    if not os.getenv("OPENAI_API_KEY"):
        return -1

    prompt = f"""You are a strict evaluator. Score 1-5 the answer's grounding to its cited context markings like [1], [2 p.7]. 
Higher is better:
1 = hallucinated / not grounded
3 = partially grounded, some unsupported claims
5 = fullt grounded; precise and supported by citations

If the answer lacks sufficient context and has now cited context markings, it is good.

Question: {question}
    
Answer: 
{answer_text}
    
Return ONLY and integer 1-5.
"""

    llm = ChatOpenAI(model = "gpt-4o-mini")
    raw = llm.invoke(prompt).content.strip()
    m = re.search(r"[1-5]", raw)
    return int(m.group()) if m else -1


# ---------------------- MAIN EVALUATION ---------------------- 

def main():
    # Setup environment and CLI
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("Missing OPENAI_API_KEY in .env")
    
    ap = argparse.ArgumentParser()
    ap.add_argument("--group", type=str, help ="Path to PDF group directory")
    ap.add_argument("--qfile", type=str, default="eval/questions.jsonl", help="Question JSONL")
    ap.add_argument("--k", type=int, default=6, help="Top-k paragraphs to retrieve")
    ap.add_argument("--out", type=str, default="eval/summary.csv", help = "CSV output path")
    ap.add_argument("--judge", action="store_true", help="Use an LLM judge")
    args = ap.parse_args()

    # Load and process documents
    records = load_pdf_group(args.group)
    if not records:
        raise SystemExit("No text records found. Please OCR first for scanned PDFs.")

    bm25, tok = build_bm25(records)
    questions = load_questions(args.qfile)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

    # Process each question and generate metrics
    rows = []
    answers = []
    for i,q in enumerate(questions, start=1):
        qtext = q['question']
        expected = q.get("expected_keywords", [])
        num_expected = len(expected)
        expected_doc = q.get("document")
        ans = answer(qtext, records, bm25, k=args.k)
        answers.append({"qid": q.get("id"),
        "question":q.get("question"),
        "answer":ans})

        has_cite = 1 if CITATION_RE.search(ans) else 0
        has_correct_source = 1 if expected_doc in ans else 0
        hits = keyword_hits(ans, expected)
        cov = round(hits / max(1, num_expected), 3)

        row = {
            "qid": q.get("id", f"q{i}"),
            "source": expected_doc,
            "has_citation": has_cite,
            "keyword_hits": hits, 
            "keyword_coverage": cov,
            "has_correct_source": has_correct_source
        }

        if args.judge:
            row["judge_grounding_1to5"] = llm_judge_score(qtext, ans)
        rows.append(row)

    # ---------------------- OUTPUT GENERATION ---------------------- 
    
    # Write eval summary to csv
    with open(args.out, "w", newline="", encoding="utf-8") as w:
        writer = csv.DictWriter(w, fieldnames = list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    # Write answers to JSONL
    answers_file = args.out.replace('.csv', '_answers.jsonl')
    with open(answers_file, "w", encoding="utf-8") as w:
        for a in answers:
            w.write(json.dumps(a, ensure_ascii=False) + '\n')

    # Print evaluation summary
    avg_cov = sum(r["keyword_coverage"] for r in rows) / len(rows)
    cite_rate = sum(r["has_citation"] for r in rows) / len(rows)
    print(f"Wrote {args.out}")
    print(f"Wrote {answers_file}")
    print(f"- citation rate: {cite_rate:.2f}")
    print(f"- avg keyword coverage: {avg_cov:.2f}")
    if args.judge:
        judged = [r["judge_grounding_1to5"] for r in rows if r.get("judge_grounding_1to5", -1) != -1]
        if judged: 
            print(f"- avg judge grounding: {sum(judged)/len(judged):.2f}")


if __name__ == "__main__":
    main()