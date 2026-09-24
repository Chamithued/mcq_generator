from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Python MCQ Generator API",
    description="AI-powered Python MCQ Generation System"
)


class ScopeRequest(BaseModel):
    scope: str


@app.get("/")
def home():
    return {
        "message": "Python MCQ Generator API is running"
    }


@app.post("/api/questions")
def generate_questions(request: ScopeRequest):

    scope = request.scope

    return {
        "received_scope": scope,
        "message": "Scope received successfully"
    }