import httpx
from typing import List, Dict

INFERENCE_SERVER_URL = "http://1.0.0.1:8000/infer"

async def generate_quiz_chunk(chunk: str, source: str, question_type: str, count: int) -> List[Dict]:
    """
    Generates a list of quiz questions from a single chunk of text.
    """
    prompt = f"Please generate {count} {question_type} questions from the following text. Return the output as a JSON list of objects, where each object has a 'question', 'options' (for mcq), and 'answer' key."
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
            questions = response.json().get("result", [])
            if isinstance(questions, str):
                import json
                try:
                    questions = json.loads(questions)
                except json.JSONDecodeError:
                    return [] # Return empty list if JSON is malformed
            for q in questions:
                q['source'] = source
            return questions
        except httpx.RequestError as e:
            return [{"question": "Error", "answer": f"Error connecting to inference server: {e}", "source": source}]
        except httpx.HTTPStatusError as e:
            return [{"question": "Error", "answer": f"Error from inference server: {e.response.status_code}", "source": source}]
