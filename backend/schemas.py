from pydantic import BaseModel, Field


class ScopeRequest(BaseModel):
    scope: str = Field(min_length=2, max_length=120)


class MCQ(BaseModel):
    question: str = Field(min_length=5)

    options: list[str] = Field(
        min_length=4,
        max_length=4
    )

    correct_index: int = Field(
        ge=0,
        le=3
    )

    explanation: str = Field(min_length=5)


class Quiz(BaseModel):
    questions: list[MCQ] = Field(
        min_length=5,
        max_length=5
    )


class AnswerSubmission(BaseModel):
    quiz_id: str

    answers: list[int] = Field(
        min_length=5,
        max_length=5
    )