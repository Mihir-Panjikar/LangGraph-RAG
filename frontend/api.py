import httpx

API_BASE_URL = "http://localhost:8000"

async def query_backend_stream(query: str):
    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream("POST", f"{API_BASE_URL}/query", json={"query": query}) as response:
            response.raise_for_status()
            async for chunk in response.aiter_text():
                yield chunk

async def ingest_document(file_name: str, file_content: bytes):
    async with httpx.AsyncClient() as client:
        files = {"file": (file_name, file_content)}
        response = await client.post(f"{API_BASE_URL}/documents/ingest", files=files)
        response.raise_for_status()
        return response.json()

async def get_documents():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/documents")
        response.raise_for_status()
        return response.json()

async def submit_feedback(query_id: str, rating: int):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_BASE_URL}/feedback", json={"query_id": query_id, "rating": rating})
        response.raise_for_status()
        return response.json()