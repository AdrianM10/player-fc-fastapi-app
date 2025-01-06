import os
import sys
from pathlib import Path

# Get the absolute path of the project root directory
root_dir = Path(__file__).parent.absolute()

# Add both the project root and app directory to Python path
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / "app"))

import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)