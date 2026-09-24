# Packages

fastapi - Build the Python backend API
uvicorn - Run the backend server; included with FastAPI's standard installation
google-genai - Connect to Gemini
python-dotenv - Load API key from a .env file


# Python MCQ Generator

An AI-powered question generation system for Python programming.

## Project Overview

This system receives a Python knowledge concept as JSON
and uses the Gemini API to generate multiple-choice questions.

Each generated quiz will contain:
- 5 MCQ questions
- 4 answer options per question
- 1 correct answer per question
- An explanation for each answer

## Technologies

- Python
- FastAPI
- Gemini API
- HTML, CSS, JavaScript

## Input Example

{
  "scope": "Python for loops"
}

## Setup

1. Create a Python virtual environment.
2. Activate the virtual environment.
3. Install requirements:

   pip install -r requirements.txt

4. Create a .env file using .env.example.
5. Run the backend:

   uvicorn backend.main:app --reload

## Development Status

Initial project setup and API development.