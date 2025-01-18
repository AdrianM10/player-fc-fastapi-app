import pytest
from fastapi.testclient import TestClient
from datetime import date
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to the Players FC API!",
        "description": "More than just a Game"
    }
