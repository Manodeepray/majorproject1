import httpx
from typing import List

INFERENCE_SERVER_URL = "http://127.0.0.1:8000/infer"

async def summarize_chunk(chunk: str) -> str:
    """
    Summarizes a single chunk of text using the inference server.
    """
    prompt = f"Please summarize the following text:\n\n{chunk}"
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
        except htt.HTTPStatusError as e:
            return f"Error from inference server: {e.response.status_code}"


async def summarize_final(summaries: List[str]) -> str:
    """
    Creates a final summary from a list of chunk summaries.
    """
    combined_summaries = "\n\n".join(summaries)
    prompt = f"Please create a final, coherent summary from the following summaries:\n\n{combined_summaries}"
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
