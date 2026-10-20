#expone el RAG con FastAPI
from fastapi import FastAPI
from pydantic import BaseModel, Field
from src.rag import answer

class QuestionRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


class Source(BaseModel):
    source: str
    page: int
    score: float

class Answer(BaseModel):
    answer: str
    sources: list[Source]

app = FastAPI(title="RAG nad technickou dokumentací")

@app.get("/health")
def health():
    return {"status": "ok"}



@app.post("/ask", response_model=Answer)
def ask(body: QuestionRequest):
    return answer(body.question)