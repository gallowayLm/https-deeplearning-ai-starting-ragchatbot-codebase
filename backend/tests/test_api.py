"""
API endpoint tests for the RAG chatbot.

Coverage:
  GET  /               – root / health
  POST /api/query      – query processing
  GET  /api/courses    – course statistics
"""

from conftest import SAMPLE_ANSWER, SAMPLE_SOURCES, SAMPLE_COURSE_TITLES


# ===========================================================================
# GET /
# ===========================================================================

class TestRootEndpoint:
    def test_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_response_body(self, client):
        data = client.get("/").json()
        assert data == {"message": "Course Materials RAG System"}


# ===========================================================================
# POST /api/query
# ===========================================================================

class TestQueryEndpoint:
    # --- happy path --------------------------------------------------------

    def test_success_returns_answer_and_sources(self, client, query_payload):
        response = client.post("/api/query", json=query_payload)

        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == SAMPLE_ANSWER
        assert data["sources"] == SAMPLE_SOURCES

    def test_success_response_includes_session_id(self, client, query_payload):
        data = client.post("/api/query", json=query_payload).json()
        assert "session_id" in data
        assert data["session_id"]  # non-empty

    def test_creates_session_when_none_provided(self, client, mock_rag_system, query_payload):
        """Omitting session_id must trigger session creation."""
        client.post("/api/query", json=query_payload)
        mock_rag_system.session_manager.create_session.assert_called_once()

    def test_uses_provided_session_id(self, client, mock_rag_system, query_payload_with_session):
        """A supplied session_id must be forwarded to rag_system.query."""
        response = client.post("/api/query", json=query_payload_with_session)

        assert response.status_code == 200
        assert response.json()["session_id"] == query_payload_with_session["session_id"]
        # session creation must NOT be called
        mock_rag_system.session_manager.create_session.assert_not_called()

    def test_rag_query_called_with_correct_args(self, client, mock_rag_system, query_payload):
        client.post("/api/query", json=query_payload)
        mock_rag_system.query.assert_called_once()
        call_args = mock_rag_system.query.call_args[0]
        assert call_args[0] == query_payload["query"]

    def test_empty_sources_list(self, client, mock_rag_system, query_payload):
        """Endpoint must handle an empty sources list from the RAG system."""
        mock_rag_system.query.return_value = ("An answer.", [])
        data = client.post("/api/query", json=query_payload).json()
        assert data["sources"] == []

    # --- validation errors -------------------------------------------------

    def test_missing_query_field_returns_422(self, client):
        response = client.post("/api/query", json={})
        assert response.status_code == 422

    def test_invalid_json_returns_422(self, client):
        response = client.post(
            "/api/query",
            content="not-json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422

    def test_null_query_returns_422(self, client):
        response = client.post("/api/query", json={"query": None})
        assert response.status_code == 422

    # --- server errors -----------------------------------------------------

    def test_rag_system_exception_returns_500(self, client, mock_rag_system, query_payload):
        mock_rag_system.query.side_effect = RuntimeError("vector store unavailable")
        response = client.post("/api/query", json=query_payload)
        assert response.status_code == 500

    def test_500_detail_contains_error_message(self, client, mock_rag_system, query_payload):
        mock_rag_system.query.side_effect = RuntimeError("vector store unavailable")
        detail = client.post("/api/query", json=query_payload).json()["detail"]
        assert "vector store unavailable" in detail

    def test_session_creation_error_returns_500(self, client, mock_rag_system, query_payload):
        mock_rag_system.session_manager.create_session.side_effect = RuntimeError("session store full")
        response = client.post("/api/query", json=query_payload)
        assert response.status_code == 500


# ===========================================================================
# GET /api/courses
# ===========================================================================

class TestCoursesEndpoint:
    # --- happy path --------------------------------------------------------

    def test_success_returns_200(self, client):
        assert client.get("/api/courses").status_code == 200

    def test_returns_correct_total_courses(self, client):
        data = client.get("/api/courses").json()
        assert data["total_courses"] == len(SAMPLE_COURSE_TITLES)

    def test_returns_correct_course_titles(self, client):
        data = client.get("/api/courses").json()
        assert data["course_titles"] == SAMPLE_COURSE_TITLES

    def test_response_schema_keys(self, client):
        data = client.get("/api/courses").json()
        assert set(data.keys()) == {"total_courses", "course_titles"}

    def test_empty_catalog(self, client, mock_rag_system, empty_analytics):
        """Zero courses is a valid state – endpoint must return 200."""
        mock_rag_system.get_course_analytics.return_value = empty_analytics
        data = client.get("/api/courses").json()
        assert data["total_courses"] == 0
        assert data["course_titles"] == []

    def test_total_courses_matches_titles_length(self, client):
        data = client.get("/api/courses").json()
        assert data["total_courses"] == len(data["course_titles"])

    # --- server errors -----------------------------------------------------

    def test_rag_system_exception_returns_500(self, client, mock_rag_system):
        mock_rag_system.get_course_analytics.side_effect = RuntimeError("db connection failed")
        response = client.get("/api/courses")
        assert response.status_code == 500

    def test_500_detail_contains_error_message(self, client, mock_rag_system):
        mock_rag_system.get_course_analytics.side_effect = RuntimeError("db connection failed")
        detail = client.get("/api/courses").json()["detail"]
        assert "db connection failed" in detail
