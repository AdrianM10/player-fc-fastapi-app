from fastapi.testclient import TestClient

from app.main import app
from app.routers.players import router as players_router
from app.models.players import Player, UpdatePlayer


client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200

