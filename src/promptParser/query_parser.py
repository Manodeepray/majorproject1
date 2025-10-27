import httpx
from typing import List

# This should be the same as in server.py
INFERENCE_SERVER_URL = "http://127.0.0.1:8000/infer"

async def break_down_query(query: str) -> List[str]:
    """
    Breaks down a complex query into a series of simpler, answerable questions.
    """
    prompt = f"""
    As an intelligent assistant, your task is to deconstruct a given user query into a series of clear and concise sub-queries. These sub-queries should be formulated to collectively address the user's information needs and guide a systematic search through a vector store.

    User Query: "{query}"

    Your decomposition should aim to:
    1.  Identify and isolate distinct components or aspects of the user's query.
    2.  Generate a sequence of questions that build upon each other, if necessary, to explore the topic comprehensively.
    3.  Ensure that each sub-query is specific enough to be answered effectively by retrieving relevant text chunks.

    Provide the sub-queries as a numbered list len < 10.
    """

    payload = {
        "query": prompt,
        "context": "",
        "model": "large"
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(INFERENCE_SERVER_URL, json=payload)
            response.raise_for_status()
            result = response.json().get("result", "")

        # The model will return a numbered list as a string.
        # We need to parse it into a list of strings.
        sub_queries = [q.strip() for q in result.split('\n') if q.strip() and q.strip()[0].isdigit()]
        # remove the leading number and dot
        sub_queries = [q.split('.', 1)[1].strip() for q in sub_queries]

        if not sub_queries:
            # If the breakdown fails, just use the original query
            return [query]

        return sub_queries
    except Exception as e:
        print(f"Error breaking down query: {e}")
        return [query] # Fallback to original query
