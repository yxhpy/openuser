"""
Shared fixtures for E2E tests.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from PIL import Image
import io

from src.api.main import app
from src.models.base import Base, get_db


# Use in-memory database for E2E tests
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create test database tables for the entire test session."""
    # Override the database dependency
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    # Clean up override
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    """Create test client."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def test_image():
    """Create a test image file."""
    img = Image.new("RGB", (100, 100), color="blue")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes


@pytest.fixture
def authenticated_user(client):
    """Create and authenticate a test user with a unique username."""
    import uuid

    unique_id = str(uuid.uuid4())[:8]
    register_data = {
        "username": f"testuser_{unique_id}",
        "email": f"test_{unique_id}@example.com",
        "password": "SecurePass123!",
    }
    response = client.post("/api/v1/auth/register", json=register_data)
    if response.status_code not in [200, 201]:
        # If registration fails, try to login instead
        login_data = {
            "username": register_data["username"],
            "password": register_data["password"],
        }
        response = client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code in [200, 201]
    tokens = response.json()
    return tokens["access_token"]
