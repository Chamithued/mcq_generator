
import os
import uuid
import logging

from threading import Lock

from dotenv import load_dotenv
from groq import APIStatusError, APIConnectionError

from fastapi import FastAPI, HTTPException

from backend.schemas import (
    ScopeRequest,
    Quiz,
    AnswerSubmission
)

from backend.question_generator import generate_quiz


# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


# Create FastAPI application
app = FastAPI(
    title="Python MCQ Generator API",
    version="0.4.0"
)


# Temporary storage for generated quizzes
quiz_store: dict[str, tuple[str, Quiz]] = {}

quiz_lock = Lock()


# ==========================================
# HOME ENDPOINT
# ==========================================

@app.get("/")
def home():

    return {
        "message": "Python MCQ API is running"
    }


# ==========================================
# GENERATE AI QUESTIONS
# ==========================================

@app.post("/api/questions")
def create_questions(request: ScopeRequest):

    # Receive knowledge concept from JSON
    scope = request.scope.strip()

    # Validate scope
    if not scope:

        raise HTTPException(
            status_code=422,
            detail="Scope cannot be empty."
        )

    # Check Groq API key
    if not os.getenv("GROQ_API_KEY"):

        raise HTTPException(
            status_code=503,
            detail="Groq API key is not configured."
        )

    # ======================================
    # GENERATE QUESTIONS USING GROQ
    # ======================================

    try:

        quiz = generate_quiz(scope)

    except APIStatusError as error:

        logger.error(
            "Groq API error: %s",
            error
        )

        if error.status_code == 429:

            raise HTTPException(
                status_code=429,
                detail="Groq API rate limit exceeded."
            ) from error

        if error.status_code in (401, 403):

            raise HTTPException(
                status_code=502,
                detail="Groq API authentication failed."
            ) from error

        if error.status_code >= 500:

            raise HTTPException(
                status_code=503,
                detail="Groq service is unavailable."
            ) from error

        raise HTTPException(
            status_code=502,
            detail="Groq API request failed."
        ) from error

    except APIConnectionError as error:

        logger.exception(
            "Could not connect to Groq."
        )

        raise HTTPException(
            status_code=503,
            detail="Could not connect to Groq."
        ) from error

    except Exception as error:

        logger.exception(
            "Question generation failed."
        )

        raise HTTPException(
            status_code=502,
            detail="Could not generate a valid quiz."
        ) from error

    # ======================================
    # STORE GENERATED QUIZ
    # ======================================

    quiz_id = str(uuid.uuid4())

    with quiz_lock:
        quiz_store[quiz_id] = (scope, quiz)

    # ======================================
    # PREPARE PUBLIC QUESTIONS
    # ======================================

    public_questions = []

    for index, question in enumerate(
        quiz.questions,
        start=1
    ):

        public_questions.append({
            "id": index,
            "question": question.question,
            "options": question.options
        })

    # ======================================
    # RETURN AI-GENERATED QUESTIONS
    # ======================================

    return {
        "quiz_id": quiz_id,
        "scope": scope,
        "questions": public_questions
    }


# ==========================================
# SUBMIT STUDENT ANSWERS
# ==========================================

@app.post("/api/submit")
def submit_answers(
    submission: AnswerSubmission
):

    quiz_id = submission.quiz_id

    # Validate answer indices
    if any(
        answer < 0 or answer > 3
        for answer in submission.answers
    ):

        raise HTTPException(
            status_code=422,
            detail="Answers must be between 0 and 3."
        )

    # Retrieve the quiz
    with quiz_lock:

        stored_quiz = quiz_store.pop(
            quiz_id,
            None
        )

    if stored_quiz is None:

        raise HTTPException(
            status_code=404,
            detail="Quiz not found or already submitted."
        )

    scope, quiz = stored_quiz

    results = []

    score = 0

    # ======================================
    # EVALUATE STUDENT ANSWERS
    # ======================================

    for index, question in enumerate(
        quiz.questions
    ):

        selected = submission.answers[index]

        is_correct = (
            selected == question.correct_index
        )

        if is_correct:
            score += 1

        results.append({
            "question_id": index + 1,
            "selected_index": selected,
            "correct_index": question.correct_index,
            "is_correct": is_correct,
            "explanation": question.explanation
        })

    # ======================================
    # RETURN STUDENT RESULTS
    # ======================================

    return {
        "quiz_id": quiz_id,
        "scope": scope,
        "score": score,
        "total": len(quiz.questions),
        "results": results
    }