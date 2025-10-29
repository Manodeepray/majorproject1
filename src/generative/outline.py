import httpx
from typing import List, Dict

INFERENCE_SERVER_URL = "http://127.0.0.1:8000/infer"

async def generate_outline_chunk(chunk: str) -> str:
    """
    Generates an outline for a single chunk of text.
    """
    prompt = f"Please create a hierarchical outline of the main topics and sub-topics from the following text:"
    payload = {
        "query": prompt,
        "context": chunk,
        "model": "large"
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(INFERENCE_SERVER_URL, json=payload)
            response.raise_for_status()
            return response.json().get("result", "")
        except httpx.RequestError as e:
            return f"Error connecting to inference server: {e}"
        except httpx.HTTPStatusError as e:
            return f"Error from inference server: {e.response.status_code}"

async def combine_outlines(outlines: List[str]) -> str:
    """
    Combines multiple outlines into a single, coherent hierarchical outline.
    """
    combined_outlines = "\n\n".join(outlines)
    prompt = f"Please combine the following outlines into a single, coherent, hierarchical outline:\n\n{combined_outlines}"
    payload = {
        "query": prompt,
        "context": "",
        "model": "large"
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(INFERENCE_SERVER_URL, json=payload)
            response.raise_for_status()
            return response.json().get("result", "")
        except httpx.RequestError as e:
            return f"Error connecting to inference server: {e}"
        except httpx.HTTPStatusError as e:
            return f"Error from inference server: {e.response.status_code}"
