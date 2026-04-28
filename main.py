from fastapi import FastAPI

app = FastAPI(title="LangGraph RAG API")

@app.get("/")
async def root():
    return {"message": "Welcome to the RAG-Based Technical Documentation Assistant API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
