"""
Tests for authentication API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.main import create_app
from src.api.auth import set_db_manager, router as auth_router
from src.models.base import Base, DatabaseManager
from src.models.user import User
from src.api.auth_utils import get_password_hash


@pytest.fixture
def db_manager():
    """Create test database manager."""
    # Use check_same_thread=False for SQLite in tests
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    db_manager = DatabaseManager("sqlite:///:memory:", echo=False)
    db_manager.engine = engine
    db_manager.SessionLocal = sessionmaker(bind=engine)
    return db_manager


@pytest.fixture
def app(db_manager):
    """Create test FastAPI application."""
    app = create_app()
    app.include_router(auth_router)
    set_db_manager(db_manager)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def test_user(db_manager):
    """Create test user in database."""
    session = db_manager.get_session()
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=get_password_hash("TestPassword123"),
        is_active=True,
        is_superuser=False
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    session.close()
    return user


class TestUserRegistration:
    """Test user registration endpoint."""

    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "NewPassword123"
            }
        )

        assert response.status_code == 201
        data = response.json()
        # Register now returns TokenResponse with user info
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert "user" in data
        # Check user info
        user = data["user"]
        assert user["username"] == "newuser"
        assert user["email"] == "newuser@example.com"
        assert user["is_active"] is True
        assert user["is_superuser"] is False
        assert "id" in user
        assert "created_at" in user

    def test_register_duplicate_username(self, client, test_user):
        """Test registration with duplicate username."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",  # Already exists
                "email": "different@example.com",
                "password": "NewPassword123"
            }
        )

        assert response.status_code == 400
        assert "Username already registered" in response.json()["detail"]

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "differentuser",
                "email": "test@example.com",  # Already exists
                "password": "NewPassword123"
            }
        )

        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_register_invalid_email(self, client):
        """Test registration with invalid email."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "invalid-email",
                "password": "NewPassword123"
            }
        )

        assert response.status_code == 422  # Validation error

    def test_register_weak_password(self, client):
        """Test registration with weak password."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "weak"  # Too short
            }
        )

        assert response.status_code == 422  # Validation error

    def test_register_password_no_uppercase(self, client):
        """Test registration with password missing uppercase."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123"  # No uppercase
            }
        )

        assert response.status_code == 422
        assert "uppercase" in str(response.json()).lower()

    def test_register_password_no_lowercase(self, client):
        """Test registration with password missing lowercase."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "PASSWORD123"  # No lowercase
            }
        )

        assert response.status_code == 422
        assert "lowercase" in str(response.json()).lower()

    def test_register_password_no_digit(self, client):
        """Test registration with password missing digit."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "PasswordOnly"  # No digit
            }
        )

        assert response.status_code == 422
        assert "digit" in str(response.json()).lower()


class TestUserLogin:
    """Test user login endpoint."""

    def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "TestPassword123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0

    def test_login_with_email(self, client, test_user):
        """Test login using email instead of username."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "test@example.com",  # Using email
                "password": "TestPassword123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "WrongPassword123"
            }
        )

        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "nonexistent",
                "password": "TestPassword123"
            }
        )

        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_inactive_user(self, client, db_manager):
        """Test login with inactive user."""
        # Create inactive user
        session = db_manager.get_session()
        user = User(
            username="inactive",
            email="inactive@example.com",
            password_hash=get_password_hash("TestPassword123"),
            is_active=False,
            is_superuser=False
        )
        session.add(user)
        session.commit()
        session.close()

        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "inactive",
                "password": "TestPassword123"
            }
        )

        assert response.status_code == 403
        assert "Inactive user" in response.json()["detail"]


class TestTokenRefresh:
    """Test token refresh endpoint."""

    def test_refresh_token_success(self, client, test_user):
        """Test successful token refresh."""
        # First login to get tokens
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "TestPassword123"
            }
        )
        refresh_token = login_response.json()["refresh_token"]

        # Refresh token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_token_invalid(self, client):
        """Test refresh with invalid token."""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid.token.here"}
        )

        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]

    def test_refresh_token_inactive_user(self, client, db_manager, test_user):
        """Test refresh token with inactive user."""
        # Login first
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "TestPassword123"
            }
        )
        refresh_token = login_response.json()["refresh_token"]

        # Deactivate user
        session = db_manager.get_session()
        user = session.query(User).filter(User.username == "testuser").first()
        user.is_active = False
        session.commit()
        session.close()

        # Try to refresh
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )

        assert response.status_code == 401
        assert "inactive" in response.json()["detail"].lower()

    def test_refresh_token_without_username(self, client):
        """Test refresh token with token missing username in payload."""
        from src.api.auth_utils import create_refresh_token

        # Create refresh token without 'sub' field
        token = create_refresh_token(data={"other_field": "value"})

        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": token}
        )

        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]


class TestGetCurrentUser:
    """Test get current user endpoint."""

    def test_get_me_success(self, client, test_user):
        """Test getting current user information."""
        # Login first
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "TestPassword123"
            }
        )
        access_token = login_response.json()["access_token"]

        # Get current user
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data

    def test_get_me_no_token(self, client):
        """Test getting current user without token."""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 401

    def test_get_me_invalid_token(self, client):
        """Test getting current user with invalid token."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )

        assert response.status_code == 401

    def test_get_me_inactive_user(self, client, db_manager, test_user):
        """Test getting current user when user is inactive."""
        # Login first
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "TestPassword123"
            }
        )
        access_token = login_response.json()["access_token"]

        # Deactivate user
        session = db_manager.get_session()
        user = session.query(User).filter(User.username == "testuser").first()
        user.is_active = False
        session.commit()
        session.close()

        # Try to get current user
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 403
        assert "Inactive user" in response.json()["detail"]

    def test_get_me_token_without_username(self, client, test_user):
        """Test getting current user with token missing username in payload."""
        from src.api.auth_utils import create_access_token

        # Create token without 'sub' field
        token = create_access_token(data={"other_field": "value"})

        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]

    def test_get_me_user_not_found(self, client, db_manager):
        """Test getting current user when user doesn't exist in database."""
        from src.api.auth_utils import create_access_token

        # Create valid token for non-existent user
        token = create_access_token(data={"sub": "nonexistent_user"})

        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]

    def test_get_db_not_configured(self):
        """Test get_db when database manager is not configured."""
        from src.api.auth import get_db, set_db_manager

        # Clear database manager
        set_db_manager(None)

        # Try to get database session
        with pytest.raises(RuntimeError, match="Database manager not configured"):
            next(get_db())
