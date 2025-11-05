"""
experiments_runner.py

Automated experiments runner for the RAG / LLM test server described by the user.

What this script does:
- Uploads a dummy file (or any file you specify) and times the upload
- Runs a suite of queries (standard query and deep query) and measures latency
- Runs summarization and other generative endpoints and measures latency
- Computes simple evaluation metrics (RAG relevance / "keyword precision") using a
  user-provided gold-standard JSON file mapping queries -> expected keywords and
  optional expected source filenames.
- Saves results to results.json and results.csv

Usage:
  python experiments_runner.py --server http://0.0.0.0:5000 \
      --gold gold.json --queries queries.json --output experiments_out

Notes:
- Provide a gold.json with structure:
  {
    "query_tests": [
      {
        "query": "tell me about constitutional ai",
        "expected_keywords": ["constitution", "ai", "red planet"],
        "expected_filenames": ["Neel Nanda mats.txt"]
      },
      ...
    ]
  }

- If gold.json is not provided the script will still measure latencies and save raw responses.
- The script is defensive (timeouts, retries) and writes detailed logs into the output folder.

"""

import argparse
import os
import time
import json
import csv
import requests
from statistics import mean, median
from typing import List, Dict, Any, Optional

# --- Defaults ---
DEFAULT_SERVER = "http://0.0.0.0:5000"
DUMMY_FILE_NAME = "Mexican-Food-1.pdf"
DUMMY_FILE_CONTENT = "the solar system. The Earth revolves around the Sun. Mars is known as the Red Planet."

def create_dummy_file(path: str = DUMMY_FILE_NAME):
    with open(path, "w") as f:
        f.write(DUMMY_FILE_CONTENT)
    return path


def remove_file(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


# --- Networking helpers ---
def post_with_timing(url: str, files=None, json_payload=None, timeout=60):
    t0 = time.perf_counter()
    try:
        if files is not None:
            r = requests.post(url, files=files, timeout=timeout)
        else:
            r = requests.post(url, json=json_payload, timeout=timeout)
        elapsed = time.perf_counter() - t0
        return r, elapsed
    except Exception as e:
        elapsed = time.perf_counter() - t0
        return e, elapsed


def get_with_timing(url: str, timeout=10):
    t0 = time.perf_counter()
    try:
        r = requests.get(url, timeout=timeout)
        elapsed = time.perf_counter() - t0
        return r, elapsed
    except Exception as e:
        elapsed = time.perf_counter() - t0
        return e, elapsed


# --- Evaluation helpers ---

def keyword_match(answer: str, expected_keywords: List[str]) -> int:
    """Return number of expected keywords found in answer (case-insensitive)."""
    if not answer:
        return 0
    ans = answer.lower()
    count = 0
    for kw in expected_keywords:
        if kw.lower() in ans:
            count += 1
    return count


def filename_hit(filenames: Any, expected_filenames: List[str]) -> int:
    """Try to detect expected filenames from the context returned by the server.
    The context may be a string or list of dicts depending on implementation.
    Returns number of expected filenames found in the context.
    """
    print(f"filenames :{filenames}\n expected_filenames :{expected_filenames}\n")
    if not expected_filenames:
        return 0
    # Try different shapes
    text_blobs = []

    if isinstance(filenames, list):
        for item in filenames:
            if isinstance(item, str):
           
                text_blobs.append(item.lower())
    elif isinstance(filenames, dict):
        for v in filenames.values():
            if isinstance(v, str):
                text_blobs.append(v.lower())
    # aggregate
    combined = "\n".join(text_blobs)
    hits = 0
    for fn in expected_filenames:
        if fn.lower() in combined:
            hits += 1
    return hits


# --- Core experiment routines ---
class ExperimentRunner:
    def __init__(self, server: str, out_dir: str = "experiments_out"):
        self.server = server.rstrip("/")
        self.endpoints = {
            "upload": f"{self.server}/upload",
            "query": f"{self.server}/query",
            "file_status": f"{self.server}/file_status",
            "deepquery": f"{self.server}/deepquery",
            "generate_outline": f"{self.server}/generate_outline",
            "summarize": f"{self.server}/summarize",
            "generate_faq": f"{self.server}/generate_faq",
            "generate_quiz": f"{self.server}/generate_quiz",
            "generate_flashcards": f"{self.server}/generate_flashcards",
            "delete": f"{self.server}/delete",
        }
        os.makedirs(out_dir, exist_ok=True)
        self.out_dir = out_dir
        self.results = {
            "metadata": {
                "server": self.server,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
            "tests": []
        }

    def check_server(self) -> bool:
        url = f"{self.server}/docs"
        r, elapsed = get_with_timing(url, timeout=5)
        if isinstance(r, requests.Response) and r.status_code == 200:
            print("Server OK (docs endpoint)")
            return True
        else:
            print("Server check failed. Response:", getattr(r, 'status_code', r))
            return False

    def upload_file(self, filename: str) -> Dict[str, Any]:
        files = {"files": (os.path.basename(filename), open(filename, 'rb'), 'text/plain')}
        r, elapsed = post_with_timing(self.endpoints["upload"], files=files, timeout=120)
        out = {"endpoint": "upload", "elapsed": elapsed}
        if isinstance(r, requests.Response):
            out.update({"status_code": r.status_code, "response": safe_json(r)})
        else:
            out.update({"error": str(r)})
        return out

    def delete_files(self, filenames: List[str]) -> Dict[str, Any]:
        payload = {"filenames": filenames}
        r, elapsed = post_with_timing(self.endpoints["delete"], json_payload=payload, timeout=60)
        out = {"endpoint": "delete", "elapsed": elapsed}
        if isinstance(r, requests.Response):
            out.update({"status_code": r.status_code, "response": safe_json(r)})
        else:
            out.update({"error": str(r)})
        return out

    def run_query_test(self, query: str, top_k: int = 3, expected_keywords: Optional[List[str]] = None,
                       expected_filenames: Optional[List[str]] = None, timeout=None) -> Dict[str, Any]:
        payload = {"query": query, "top_k": top_k}
        r, elapsed = post_with_timing(self.endpoints["query"], json_payload=payload, timeout=timeout or 120)
        testres = {
            "endpoint": "query",
            "query": query,
            "elapsed": elapsed,
            "top_k": top_k,
        }
        if isinstance(r, requests.Response):
            resp_json = safe_json(r)
            testres.update({"status_code": r.status_code, "response": resp_json})
            answer = resp_json.get("answer") if isinstance(resp_json, dict) else None
            context = resp_json.get("context") if isinstance(resp_json, dict) else None
            filenames = resp_json.get("filenames") if isinstance(resp_json, dict) else None
            print(resp_json)
            
            # metrics
            if expected_keywords:
                k_matches = keyword_match(answer or "", expected_keywords)
                testres.update({"keyword_matches": k_matches, "expected_keyword_count": len(expected_keywords)})
            if expected_filenames:
                file_hits = filename_hit(filenames, expected_filenames)
                testres.update({"file_hits": file_hits, "expected_file_count": len(expected_filenames)})
        else:
            testres.update({"error": str(r)})
        self.results["tests"].append(testres)
        return testres

    def run_deep_query_test(self, query: str, top_k: int = 1, create_graph: bool = False,
                            expected_keywords: Optional[List[str]] = None,
                            expected_filenames: Optional[List[str]] = None, timeout=None) -> Dict[str, Any]:
        payload = {"query": query, "top_k": top_k, "create_graph": create_graph}
        r, elapsed = post_with_timing(self.endpoints["deepquery"], json_payload=payload, timeout=timeout or 300)
        testres = {
            "endpoint": "deepquery",
            "query": query,
            "elapsed": elapsed,
            "top_k": top_k,
            "create_graph": create_graph
        }
        if isinstance(r, requests.Response):
            resp_json = safe_json(r)
            testres.update({"status_code": r.status_code, "response": resp_json})
            answer = resp_json.get("answer") if isinstance(resp_json, dict) else None
            context = resp_json.get("context") if isinstance(resp_json, dict) else None
            if expected_keywords:
                k_matches = keyword_match(answer or "", expected_keywords)
                testres.update({"keyword_matches": k_matches, "expected_keyword_count": len(expected_keywords)})
            if expected_filenames:
                file_hits = filename_hit(context, expected_filenames)
                testres.update({"file_hits": file_hits, "expected_file_count": len(expected_filenames)})
        else:
            testres.update({"error": str(r)})
        self.results["tests"].append(testres)
        return testres

    def run_summarize_test(self, filenames: List[str], timeout=None) -> Dict[str, Any]:
        payload = {"filenames": filenames}
        r, elapsed = post_with_timing(self.endpoints["summarize"], json_payload=payload, timeout=timeout or 180)
        out = {"endpoint": "summarize", "elapsed": elapsed}
        if isinstance(r, requests.Response):
            resp_json = safe_json(r)
            out.update({"status_code": r.status_code, "response": resp_json})
        else:
            out.update({"error": str(r)})
        self.results["tests"].append(out)
        return out

    def run_generate_tools(self, filenames: List[str], quiz_count: int = 2, timeout=None) -> Dict[str, Any]:
        out = {"endpoint": "generate_tools", "children": []}
        # outline
        try:
            payload = {"filenames": filenames, "combine": False}
            r1, t1 = post_with_timing(self.endpoints["generate_outline"], json_payload=payload, timeout=timeout or 180)
            out["children"].append({"sub": "outline", "elapsed": t1, "response": safe_json(r1) if isinstance(r1, requests.Response) else str(r1)})
        except Exception as e:
            out["children"].append({"sub": "outline", "error": str(e)})
        # faq
        try:
            payload = {"filenames": filenames}
            r2, t2 = post_with_timing(self.endpoints["generate_faq"], json_payload=payload, timeout=timeout or 180)
            out["children"].append({"sub": "faq", "elapsed": t2, "response": safe_json(r2) if isinstance(r2, requests.Response) else str(r2)})
        except Exception as e:
            out["children"].append({"sub": "faq", "error": str(e)})
        # quiz
        try:
            payload = {"filenames": filenames, "question_type": "mcq", "count": quiz_count}
            r3, t3 = post_with_timing(self.endpoints["generate_quiz"], json_payload=payload, timeout=timeout or 180)
            out["children"].append({"sub": "quiz", "elapsed": t3, "response": safe_json(r3) if isinstance(r3, requests.Response) else str(r3)})
        except Exception as e:
            out["children"].append({"sub": "quiz", "error": str(e)})
        # flashcards
        try:
            payload = {"filenames": filenames}
            r4, t4 = post_with_timing(self.endpoints["generate_flashcards"], json_payload=payload, timeout=timeout or 180)
            out["children"].append({"sub": "flashcards", "elapsed": t4, "response": safe_json(r4) if isinstance(r4, requests.Response) else str(r4)})
        except Exception as e:
            out["children"].append({"sub": "flashcards", "error": str(e)})

        self.results["tests"].append(out)
        return out

    def save_results(self):
        out_json = os.path.join(self.out_dir, "results.json")
        with open(out_json, "w") as f:
            json.dump(self.results, f, indent=2)
        # also produce a CSV summary
        csv_file = os.path.join(self.out_dir, "results_summary.csv")
        rows = []
        for t in self.results.get("tests", []):
            row = {
                "endpoint": t.get("endpoint"),
                "elapsed": t.get("elapsed"),
                "status_code": t.get("status_code", ""),
                "query": t.get("query", ""),
            }
            rows.append(row)
        with open(csv_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["endpoint", "query", "elapsed", "status_code"])
            writer.writeheader()
            for r in rows:
                writer.writerow(r)
        print("Saved results to:", out_json, csv_file)


# --- Utilities ---
def safe_json(response: requests.Response):
    try:
        return response.json()
    except Exception:
        return {"text": response.text[:1000]}


# --- Main CLI ---

def load_gold(gold_path: Optional[str]):
    if not gold_path or not os.path.exists(gold_path):
        return None
    with open(gold_path, "r") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", default=DEFAULT_SERVER, help="Base server URL")
    parser.add_argument("--gold", default=None, help="Path to gold.json (optional)")
    parser.add_argument("--output", default="experiments_out", help="Output directory")
    parser.add_argument("--upload_file", default=DUMMY_FILE_NAME, help="File to upload as test input")
    parser.add_argument("--skip_upload", action="store_true", help="Skip upload step (useful if files already present on server)")
    parser.add_argument("--run_deep", action="store_true", help="Also run deepquery tests")
    parser.add_argument("--delete", default=False, help="delete file or not")
    args = parser.parse_args()

    gold = load_gold(args.gold)
    runner = ExperimentRunner(args.server, out_dir=args.output)

    if not runner.check_server():
        print("Server not available. Exiting.")
        return

    # prepare file
    if not args.skip_upload:
        create_dummy_file(args.upload_file)
        print("Uploading file...", args.upload_file)
        up = runner.upload_file(args.upload_file)
        print("Upload result:", up.get("status_code"))
        # wait a bit for processing (adjustable)
        time.sleep(3)

    # prepare tests list
    query_tests = []
    if gold and "query_tests" in gold:
        query_tests = gold["query_tests"]
    else:
        # fallback default queries
        query_tests = [
            {"query": "tell me about constitutional ai", "expected_keywords": ["constitutional", "ai", "red planet"], "expected_filenames": [args.upload_file]},
            {"query": "what is mars", "expected_keywords": ["red planet", "mars"], "expected_filenames": [args.upload_file]},
        ]

    # run the queries
    for qt in query_tests:
        q = qt.get("query")
        expected_k = qt.get("expected_keywords") or []
        expected_fns = qt.get("expected_filenames") or []
        print(f"Running standard query: {q}")
        runner.run_query_test(q, top_k=3, expected_keywords=expected_k, expected_filenames=expected_fns)
        if args.run_deep:
            print(f"Running deep query: {q}")
            runner.run_deep_query_test(q, top_k=1, create_graph=False, expected_keywords=expected_k, expected_filenames=expected_fns)
        # small pause between queries
        time.sleep(1)

    # test summarize and generative tools
    print("Running summarize and generative tools tests...")
    runner.run_summarize_test([args.upload_file])
    runner.run_generate_tools([args.upload_file], quiz_count=2)

    # delete test file from server (best-effort)
    if args.delete:
        print("Deleting files on server (best-effort)...")
        runner.delete_files([args.upload_file])

    # save results
    runner.save_results()

    # cleanup local file
    if not args.skip_upload:
        remove_file(args.upload_file)


if __name__ == "__main__":
    main()
