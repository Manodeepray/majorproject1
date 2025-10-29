import httpx
from typing import List, Dict

INFERENCE_SERVER_URL = "http://127.0.0.1:8000/infer"

async def generate_faq_chunk(chunk: str, source: str) -> List[Dict[str, str]]:
    """
    Generates a list of FAQs from a single chunk of text.
    """
    prompt = f"Please generate a list of potential questions and answers from the following text. Return the output as a JSON list of objects, where each object has a 'question' and 'answer' key.\n\nText:\n{chunk}"
    payload = {
        "query": prompt,
        "context": "",
        "model": "large"
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(INFERENCE_SERVER_URL, json=payload)
            response.raise_for_status()
            # The model should return a JSON string, so we parse it
            faqs = response.json().get("result", [])
            if isinstance(faqs, str):
                import json
                try:
                    faqs = json.loads(faqs)
                except json.JSONDecodeError:
                    return [] # Return empty list if JSON is malformed
            for faq in faqs:
                faq['source'] = source
            return faqs
        except httpx.RequestError as e:
            return [{"question": "Error", "answer": f"Error connecting to inference server: {e}", "source": source}]
        except httpx.HTTPStatusError as e:
            return [{"question": "Error", "answer": f"Error from inference server: {e.response.status_code}", "source": source}]
