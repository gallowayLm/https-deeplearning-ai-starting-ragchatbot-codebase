"""
Shared fixtures and test app factory for the RAG system test suite.

The production app (app.py) mounts static files from ../frontend and initialises
heavy dependencies (ChromaDB, sentence-transformers, Anthropic) at import time.
To avoid those side-effects in tests we build a lightweight test app here that
mirrors every API endpoint but omits the static-file mount entirely.
"""

import sys
import pytest
from pathlib import Path
from typing import List, Optional
from unittest.mock import MagicMock

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

# Make backend/ importable without modifying PYTHONPATH externally.
# (pytest.ini_options pythonpath also handles this, but the explicit insert
#  keeps the test suite runnable via `python -m pytest` from any directory.)
sys.path.insert(0, str(Path(__file__).parent.parent))

# ---------------------------------------------------------------------------
# Static test data
# ---------------------------------------------------------------------------

SAMPLE_COURSE_TITLES = ["Python Fundamentals", "Machine Learning Basics"]

SAMPLE_ANALYTICS = {
    "total_courses": len(SAMPLE_COURSE_TITLES),
    "course_titles": SAMPLE_COURSE_TITLES,
}

SAMPLE_ANSWER = "Here is the answer to your question about the course material."
SAMPLE_SOURCES = ["course1_script.txt", "course2_script.txt"]


# ---------------------------------------------------------------------------
# Pydantic models
# (Mirrors app.py so the test app has identical request/response contracts.)
# ---------------------------------------------------------------------------

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    session_id: str


class CourseStats(BaseModel):
    total_courses: int
    course_titles: List[str]


# ---------------------------------------------------------------------------
# Test-app factory
# ---------------------------------------------------------------------------

def create_test_app(rag_system) -> FastAPI:
    """
    Return a FastAPI application with the same API surface as app.py but
    without static-file mounting or heavy startup events.

    ``rag_system`` is injected so tests can control its behaviour via mocks.
    """
    application = FastAPI(title="RAG System – Test")

    @application.get("/")
    async def root():
        return {"message": "Course Materials RAG System"}

    @application.post("/api/query", response_model=QueryResponse)
    async def query_documents(request: QueryRequest):
        try:
            session_id = request.session_id
            if not session_id:
                session_id = rag_system.session_manager.create_session()
            answer, sources = rag_system.query(request.query, session_id)
            return QueryResponse(answer=answer, sources=sources, session_id=session_id)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @application.get("/api/courses", response_model=CourseStats)
    async def get_course_stats():
        try:
            analytics = rag_system.get_course_analytics()
            return CourseStats(
                total_courses=analytics["total_courses"],
                course_titles=analytics["course_titles"],
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    return application


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_rag_system():
    """
    MagicMock that stands in for RAGSystem.

    Default return values cover the happy-path for every endpoint so that
    individual tests only need to override what they specifically care about.
    """
    mock = MagicMock()
    mock.session_manager.create_session.return_value = "session_1"
    mock.query.return_value = (SAMPLE_ANSWER, SAMPLE_SOURCES)
    mock.get_course_analytics.return_value = SAMPLE_ANALYTICS
    return mock


@pytest.fixture()
def app(mock_rag_system):
    """FastAPI test application wired to the mock RAG system."""
    return create_test_app(mock_rag_system)


@pytest.fixture()
def client(app):
    """Synchronous Starlette TestClient for the test application."""
    return TestClient(app)


# ---------------------------------------------------------------------------
# Reusable request/response data fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def query_payload():
    """Minimal valid payload for POST /api/query."""
    return {"query": "What topics does the Python course cover?"}


@pytest.fixture()
def query_payload_with_session():
    """Valid payload that includes an existing session_id."""
    return {
        "query": "Explain gradient descent.",
        "session_id": "existing_session_42",
    }


@pytest.fixture()
def empty_analytics():
    """Analytics dict representing an empty course catalog."""
    return {"total_courses": 0, "course_titles": []}
