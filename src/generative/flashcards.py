import httpx
from typing import List, Dict

INFERENCE_SERVER_URL = "http://127.0.0.1:8000/infer"

async def generate_flashcards_chunk(chunk: str, source: str) -> List[Dict[str, str]]:
    """
    Generates a list of flashcards from a single chunk of text.
    """
    prompt = f"Please identify key term/definition pairs or core concept/explanation pairs from the following text and format them as a JSON list of objects, where each object has a 'front' and 'back' key."
    payload = {
        "query": prompt,
        "context": chunk,
        "model": "large"
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(INFERENCE_SERVER_URL, json=payload)
            response.raise_for_status()
            # The model should return a JSON string, so we parse it
            flashcards = response.json().get("result", [])
            if isinstance(flashcards, str):
                import json
                try:
                    flashcards = json.loads(flashcards)
                except json.JSONDecodeError:
                    return [] # Return empty list if JSON is malformed
            for card in flashcards:
                card['source'] = source
            return flashcards
        except httpx.RequestError as e:
            return [{"front": "Error", "back": f"Error connecting to inference server: {e}", "source": source}]
        except httpx.HTTPStatusError as e:
            return [{"front": "Error", "back": f"Error from inference server: {e.response.status_code}", "source": source}]

