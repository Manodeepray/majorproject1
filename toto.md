✓  WriteFile Writing to src/generative/engine.py                                                                                                                    │
│                                                                                                                                                                     │
│     1 - # /generate_quiz                                                                                                                                            │
│     1 + import json                                                                                                                                                 │
│     2 + from pathlib import Path                                                                                                                                    │
│     3 + from typing import List, Dict                                                                                                                               │
│     4 + import asyncio                                                                                                                                              │
│     5 + from .summarize import summarize_chunk, summarize_final                                                                                                     │
│     6                                                                                                                                                               │
│     3 - # What it does: Takes a document_name and parameters like question_type ("mcq", "short_answer") and count. It generates a list of quiz questions and their  │
│       answers (with citations!) based on the content.                                                                                                               │
│     7 + # Define paths                                                                                                                                              │
│     8 + project_root = Path(__file__).parent.parent.parent                                                                                                          │
│     9 + LOGS_DIR = project_root / "database" / "logs"                                                                                                               │
│    10 + DATA_WAREHOUSE_DIR = project_root / "database" / "data_warehouse"                                                                                           │
│    11 + CHUNK_SIZE = 2000  # characters                                                                                                                             │
│    12                                                                                                                                                               │
│     5 - # Why: This is a fantastic "active recall" tool. Users can upload lecture notes and instantly get a practice test to check their understanding.             │
│    ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════ │
│    13 + def load_json(path):                                                                                                                                        │
│    14 +     if path.exists():                                                                                                                                       │
│    15 +         with open(path, 'r') as f:                                                                                                                          │
│    16 +             try:                                                                                                                                            │
│    17 +                 return json.load(f)                                                                                                                         │
│    18 +             except json.JSONDecodeError:                                                                                                                    │
│    19 +                 return {}                                                                                                                                   │
│    20 +     return {}                                                                                                                                               │
│    21                                                                                                                                                               │
│     7 - # /generate_flashcards                                                                                                                                      │
│    ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════ │
│    22 + def get_document_content(filename: str) -> str:                                                                                                             │
│    23 +     """                                                                                                                                                     │
│    24 +     Loads the content of a document from the data warehouse.                                                                                                │
│    25 +     """                                                                                                                                                     │
│    26 +     file_path = DATA_WAREHOUSE_DIR / filename                                                                                                               │
│    27 +     if file_path.exists():                                                                                                                                  │
│    28 +         with open(file_path, 'r', encoding='utf-8') as f:                                                                                                   │
│    29 +             return f.read()                                                                                                                                 │
│    30 +     return ""                                                                                                                                               │
│    31                                                                                                                                                               │
│     9 - # What it does: Takes a document_name. It identifies key term/definition pairs or core concept/explanation pairs and formats them as a list of {"front":    │
│       "Term", "back": "Definition"} objects, ready to be imported into a flashcard app.                                                                             │
│    ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════ │
│    32 + async def run_summarization(filenames: List[str]) -> List[Dict[str, str]]:                                                                                  │
│    33 +     """                                                                                                                                                     │
│    34 +     Orchestrates the summarization process for a list of files.                                                                                             │
│    35 +     """                                                                                                                                                     │
│    36 +     file_status_path = LOGS_DIR / "file_status.json"                                                                                                        │
│    37 +     file_status = load_json(file_status_path)                                                                                                               │
│    38                                                                                                                                                               │
│    11 - # Why: Provides another popular, proven study method directly from the source materia                                                                       │
│    ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════ │
│    39 +     results = []                                                                                                                                            │
│    40                                                                                                                                                               │
│    13 - # /generate_quiz                                                                                                                                            │
│    ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════ │
│    41 +     for filename in filenames:                                                                                                                              │
│    42 +         if filename not in file_status or file_status[filename].get('status') != 'processed':                                                               │
│    43 +             results.append({"filename": filename, "summary": "File not found or not processed."})                                                           │
│    44 +             continue                                                                                                                                        │
│    45                                                                                                                                                               │
│    15 - # What it does: Takes a document_name and parameters like question_type ("mcq", "short_answer") and count. It generates a list of quiz questions and their  │
│       answers (with citations!) based on the content.                                                                                                               │
│    ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════ │
│    46 +         content = get_document_content(filename)                                                                                                            │
│    47 +         if not content:                                                                                                                                     │
│    48 +             results.append({"filename": filename, "summary": "Could not read file content."})                                                               │
│    49 +             continue                                                                                                                                        │
│    50                                                                                                                                                               │
│    17 - # Why: This is a fantastic "active recall" tool. Users can upload lecture notes and instantly get a practice test to check their understanding.             │
│    ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════ │
│    51 +         # Break document into chunks                                                                                                                        │
│    52 +         chunks = [content[i:i + CHUNK_SIZE] for i in range(0, len(content), CHUNK_SIZE)]                                                                    │
│    53                                                                                                                                                               │
│    19 - # /generate_flashcards                                                                                                                                      │
│    ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════ │
│    54 +         # Summarize each chunk concurrently                                                                                                                 │
│    55 +         chunk_summaries = await asyncio.gather(*[summarize_chunk(chunk) for chunk in chunks])                                                               │
│    56                                                                                                                                                               │
│    21 - # What it does: Takes a document_name. It identifies key term/definition pairs or core concept/explanation pairs and formats them as a list of {"front":    │
│       "Term", "back": "Definition"} objects, ready to be imported into a flashcard app.                                                                             │
│    ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════ │
│    57 +         # Create a final summary                                                                                                                            │
│    58 +         final_summary = await summarize_final(chunk_summaries)                                                                                              │
│    59                                                                                                                                                               │
│    23 - # Why: Provides another popular, proven study method directly from the source materia                                                                       │
│    ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════ │
│    60 +         results.append({"filename": filename, "summary": final_summary})                                                                                    │
│    61                                                                                                                                                               │
│    25 - # /summarize                                                                                                                                                │
│    26 -                                                                                                                                                             │
│    27 - # What it does: Takes a document_name as input and returns a comprehensive summary of that single document. This is often the first thing a user wants.     │
│    28 -                                                                                                                                                             │
│    29 - # /generate_faq                                                                                                                                             │
│    30 -                                                                                                                                                             │
│    31 - # What it does: Takes a document_name and generates a list of potential questions and answers from its content. This is fantastic for creating study        │
│       guides.                                                                                                                                                       │
│    32 -                                                                                                                                                             │
│    33 - # /generate_outline                                                                                                                                         │
│    34 -                                                                                                                                                             │
│    35 - # What it does: Analyzes a document and returns a hierarchical outline of its main topics and sub-topics.                                                   │
│    36 -                                                                                                                                                             │
│    37 - # /identify_themes                                                                                                                                          │
│    38 -                                                                                                                                                             │
│    39 - # What it does: This is more advanced. It queries the entire RAG (all docs) to find common themes, concepts, or arguments that appear across multiple       │
│       sources.                                                                                                                                                      │
│    ═══════════════════












