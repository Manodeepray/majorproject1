import json
import re
from typing import List, Dict
import httpx
import asyncio


def extract_json_from_text(text: str) -> List[Dict[str, str]]:
    """
    Extracts and parses a JSON list of FAQs from LLM output text.
    Handles code fences, plain JSON, and lightly malformed text around JSON.
    Returns [] if parsing fails.
    """
    if not text or not isinstance(text, str):
        return []

    text = text.strip()

    # 1. Try to extract JSON from inside code fences
    match = re.search(r"```(?:json)?(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        json_candidate = match.group(1).strip()
    else:
        # 2. Try to find the first valid JSON-looking segment
        match = re.search(r"(\[.*\])", text, re.DOTALL)
        json_candidate = match.group(1).strip() if match else text

    # 3. Try parsing as JSON
    try:
        data = json.loads(json_candidate)
        if isinstance(data, list) and all(isinstance(x, dict) for x in data):
            return data
        else:
            return []
    except json.JSONDecodeError:
        # 4. Try light cleanup (remove trailing text after JSON)
        match = re.search(r"(\[.*?\])", json_candidate, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                if isinstance(data, list) and all(isinstance(x, dict) for x in data):
                    return data
            except json.JSONDecodeError:
                pass
        return []


INFERENCE_SERVER_URL = "http://127.0.0.1:8000/infer"

async def generate_faq_chunk(chunk: str, source: str) -> List[Dict[str, str]]:
    """
    Generates a list of FAQs from a single chunk of text.
    """
    prompt = f"Please generate a small list of potential questions and answers from the following text. Return the output as a JSON list of objects, where each object has a 'question' and 'answer' key.\n"
    payload = {
        "query": prompt,
        "context": chunk,
        "model": "large"
    }
    # print(payload)
    
    await asyncio.sleep(2.5)
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(INFERENCE_SERVER_URL, json=payload)
            response.raise_for_status()
            # The model should return a JSON string, so we parse it

            result = response.json().get("result", "")

            # Handle both direct JSON and text-wrapped JSON
            faqs = extract_json_from_text(result)

            # Tag each FAQ with the source
            for faq in faqs:
                faq["source"] = source

            return faqs
        except httpx.RequestError as e:
            return [{"question": "Error", "answer": f"Error connecting to inference server: {e}", "source": source}]
        except httpx.HTTPStatusError as e:
            return [{"question": "Error", "answer": f"Error from inference server: {e.response.status_code}", "source": source}]
