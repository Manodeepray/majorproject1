import json
from pathlib import Path
from typing import List, Dict
import asyncio
import PyPDF2
import docx
from .summarize import summarize_chunk, summarize_final
from .outline import generate_outline_chunk, combine_outlines
from .faq import generate_faq_chunk
from .quiz import generate_quiz_chunk
from .flashcards import generate_flashcards_chunk

# Define paths
project_root = Path(__file__).parent.parent.parent
LOGS_DIR = project_root / "database" / "logs"
DATA_WAREHOUSE_DIR = project_root / "database" / "data_warehouse"
CHUNK_SIZE = 2000  # characters

def load_json(path):
    if path.exists():
        with open(path, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def get_document_content(filename: str) -> str:
    """
    Loads the content of a document from the data warehouse.
    Handles .txt, .pdf, and .docx files.
    """
    file_path = DATA_WAREHOUSE_DIR / filename
    if not file_path.exists():
        return ""

    content = ""
    try:
        extension = Path(filename).suffix.lower()
        if extension == '.pdf':
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        content += page_text
        elif extension == '.docx':
            doc = docx.Document(file_path)
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            content = '\n'.join(full_text)
        elif extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        # Note: .doc files are not supported by the python-docx library.
        # An alternative library would be needed for .doc file support.
        else:
            # For other file types, try to read as text, but this might fail for binary files.
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except (UnicodeDecodeError, IOError):
                print(f"Warning: Could not read {filename} as a text file. Unsupported file type.")
                return ""

    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return ""
    return content

async def run_summarization(filenames: List[str]) -> List[Dict[str, str]]:
    """
    Orchestrates the summarization process for a list of files.
    """
    file_status_path = LOGS_DIR / "file_status.json"
    file_status = load_json(file_status_path)
    
    results = []

    for filename in filenames:
        if filename not in file_status or file_status[filename].get('status') != 'processed':
            results.append({"filename": filename, "summary": "File not found or not processed."})
            continue

        content = get_document_content(filename)
        if not content:
            results.append({"filename": filename, "summary": "Could not read file content."})
            continue

        # Break document into chunks
        chunks = [content[i:i + CHUNK_SIZE] for i in range(0, len(content), CHUNK_SIZE)]
        
        # Summarize each chunk concurrently
        chunk_summaries = await asyncio.gather(*[summarize_chunk(chunk) for chunk in chunks])

        # Create a final summary
        final_summary = await summarize_final(chunk_summaries)
        
        results.append({"filename": filename, "summary": final_summary})

    return results

async def run_outline_generation(filenames: List[str], combine: bool) -> Dict:
    """
    Orchestrates the outline generation process for a list of files.
    """
    file_status_path = LOGS_DIR / "file_status.json"
    file_status = load_json(file_status_path)
    
    all_outlines = []
    individual_outlines = {}

    for filename in filenames:
        print(file_status[filename])
        if filename not in file_status or file_status[filename].get('status') != 'processed':
            
            individual_outlines[filename] = "File not found or not processed."
            continue

        content = get_document_content(filename)
        if not content:
            individual_outlines[filename] = "Could not read file content."
            continue

        chunks = [content[i:i + CHUNK_SIZE] for i in range(0, len(content), CHUNK_SIZE)]
        print(f"[PROCESSING] working on {len(chunks)} chunks")
        chunk_outlines = await asyncio.gather(*[generate_outline_chunk(chunk) for chunk in chunks])
        
        if combine:
            all_outlines.extend(chunk_outlines)
        else:
            individual_outlines[filename] = "\n\n".join(chunk_outlines)

    if combine:
        combined_outline = await combine_outlines(all_outlines)
        return {"combined_outline": combined_outline}
    else:
        return {"individual_outlines": individual_outlines}

async def run_faq_generation(filenames: List[str]) -> List[Dict[str, str]]:
    """
    Orchestrates the FAQ generation process for a list of files.
    """
    file_status_path = LOGS_DIR / "file_status.json"
    file_status = load_json(file_status_path)
    
    all_faqs = []

    for filename in filenames:
        print(file_status[filename])
        if filename not in file_status or file_status[filename].get('status') != 'processed':
            continue

        content = get_document_content(filename)
        if not content:
            continue

        chunks = [content[i:i + CHUNK_SIZE] for i in range(0, len(content), CHUNK_SIZE)]
        print(f"[PROCESSING] working on {len(chunks)} chunks")
        chunk_faqs_lists = await asyncio.gather(*[generate_faq_chunk(chunk, filename) for chunk in chunks])
        
        for faq_list in chunk_faqs_lists:
            all_faqs.extend(faq_list)

    return all_faqs

async def run_quiz_generation(filenames: List[str], question_type: str, count: int) -> List[Dict]:
    """
    Orchestrates the quiz generation process for a list of files.
    """
    file_status_path = LOGS_DIR / "file_status.json"
    file_status = load_json(file_status_path)
    
    all_questions = []

    for filename in filenames:
        if filename not in file_status or file_status[filename].get('status') != 'processed':
            continue

        content = get_document_content(filename)
        if not content:
            continue

        chunks = [content[i:i + CHUNK_SIZE] for i in range(0, len(content), CHUNK_SIZE)]
        print(f"[PROCESSING] working on {len(chunks)} chunks")
        # Distribute the count of questions among chunks
        questions_per_chunk = max(1, count // len(chunks))

        chunk_questions_lists = await asyncio.gather(*[generate_quiz_chunk(chunk, filename, question_type, questions_per_chunk) for chunk in chunks])
        
        for questions_list in chunk_questions_lists:
            all_questions.extend(questions_list)

    return all_questions

async def run_flashcards_generation(filenames: List[str]) -> List[Dict[str, str]]:
    """
    Orchestrates the flashcard generation process for a list of files.
    """
    file_status_path = LOGS_DIR / "file_status.json"
    file_status = load_json(file_status_path)
    
    all_flashcards = []

    for filename in filenames:
        if filename not in file_status or file_status[filename].get('status') != 'processed':
            continue

        content = get_document_content(filename)
        if not content:
            continue

        chunks = [content[i:i + CHUNK_SIZE] for i in range(0, len(content), CHUNK_SIZE)]
        
        chunk_flashcards_lists = await asyncio.gather(*[generate_flashcards_chunk(chunk, filename) for chunk in chunks])
        
        for flashcards_list in chunk_flashcards_lists:
            all_flashcards.extend(flashcards_list)

    return all_flashcards

