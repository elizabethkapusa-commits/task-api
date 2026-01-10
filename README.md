# Task API

A simple REST API built with FastAPI that demonstrates basic backend concepts
including routing, request validation, error handling, and interactive
documentation.

## Features
- Health check endpoint
- Create, list, and delete tasks
- Input validation using Pydantic
- Interactive API docs with Swagger UI

## Tech Stack
- Python 3.12
- FastAPI
- Uvicorn

## How to Run
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi "uvicorn[standard]"
uvicorn main:app --reload
Open:
http://127.0.0.1:8000/docs
