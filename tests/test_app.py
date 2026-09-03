import sys
import os
import io

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "backend")
    )
)

from app import app


def test_health():
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "healthy"


def test_get_documents():
    client = app.test_client()

    response = client.get("/api/documents")

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, list)


def test_add_document_without_name():
    client = app.test_client()

    response = client.post(
        "/api/documents",
        data={
            "category": "Test",
            "description": "Test document",
            "file": (
                io.BytesIO(b"test file"),
                "test.txt"
            )
        },
        content_type="multipart/form-data"
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Document name is required"


def test_add_document_without_file():
    client = app.test_client()

    response = client.post(
        "/api/documents",
        data={
            "name": "Test Document",
            "category": "Test",
            "description": "Test document"
        },
        content_type="multipart/form-data"
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "File is required"

def test_add_document_success():
    client = app.test_client()

    response = client.post(
        "/api/documents",
        data={
            "name": "Test Upload",
            "category": "Test",
            "description": "Testing successful upload",
            "file": (
                io.BytesIO(b"test file content"),
                "test_upload.txt"
            )
        },
        content_type="multipart/form-data"
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["message"] == "Document added successfully"
    assert data["file_name"] == "test_upload.txt"
    assert "id" in data


def test_delete_document_success():
    client = app.test_client()

    # First create a document
    response = client.post(
        "/api/documents",
        data={
            "name": "Document To Delete",
            "category": "Test",
            "description": "This document will be deleted",
            "file": (
                io.BytesIO(b"delete test"),
                "delete_test.txt"
            )
        },
        content_type="multipart/form-data"
    )

    assert response.status_code == 201

    document_id = response.get_json()["id"]

    # Now delete it
    response = client.delete(
        f"/api/documents/{document_id}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Document deleted successfully"