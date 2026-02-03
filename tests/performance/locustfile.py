"""
Load testing scenarios using Locust.

Run with: locust -f tests/performance/locustfile.py --host=http://localhost:8000

This file defines load testing scenarios for the OpenUser API.
"""

import random

from locust import HttpUser, between, task


class OpenUserUser(HttpUser):
    """Simulated user for load testing."""

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    token = None

    def on_start(self):
        """Start a simulated user."""
        # Register and login
        username = f"loadtest_{random.randint(1000, 9999)}"
        email = f"{username}@example.com"
        password = "TestPass123!"

        # Register
        self.client.post(
            "/api/v1/auth/register",
            json={"username": username, "email": email, "password": password},
        )

        # Login
        response = self.client.post(
            "/api/v1/auth/login", json={"username": username, "password": password}
        )

        if response.status_code == 200:
            self.token = response.json()["access_token"]

    @task(10)
    def health_check(self):
        """Check API health (high frequency)."""
        self.client.get("/health")

    @task(5)
    def get_root(self):
        """Get root endpoint (medium frequency)."""
        self.client.get("/")

    @task(3)
    def get_user_info(self):
        """Get current user info (medium frequency)."""
        if self.token:
            self.client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {self.token}"})

    @task(2)
    def list_agents(self):
        """List agents (low frequency)."""
        if self.token:
            self.client.get(
                "/api/v1/agents/list", headers={"Authorization": f"Bearer {self.token}"}
            )

    @task(1)
    def create_agent(self):
        """Create an agent (low frequency)."""
        if self.token:
            agent_name = f"agent_{random.randint(1000, 9999)}"
            self.client.post(
                "/api/v1/agents/create",
                json={
                    "name": agent_name,
                    "system_prompt": "You are a helpful assistant",
                    "capabilities": ["chat"],
                },
                headers={"Authorization": f"Bearer {self.token}"},
            )


class AuthenticationUser(HttpUser):
    """User focused on authentication endpoints."""

    wait_time = between(1, 2)

    @task
    def register_and_login(self):
        """Register and login flow."""
        username = f"authtest_{random.randint(1000, 9999)}"
        email = f"{username}@example.com"
        password = "TestPass123!"

        # Register
        self.client.post(
            "/api/v1/auth/register",
            json={"username": username, "email": email, "password": password},
        )

        # Login
        self.client.post("/api/v1/auth/login", json={"username": username, "password": password})


class ReadOnlyUser(HttpUser):
    """User that only performs read operations."""

    wait_time = between(0.5, 1.5)
    token = None

    def on_start(self):
        """Login with existing user."""
        # Use a pre-created user for read-only operations
        response = self.client.post(
            "/api/v1/auth/login", json={"username": "readonly", "password": "TestPass123!"}
        )

        if response.status_code == 200:
            self.token = response.json()["access_token"]

    @task(5)
    def health_check(self):
        """Check API health."""
        self.client.get("/health")

    @task(3)
    def get_user_info(self):
        """Get user info."""
        if self.token:
            self.client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {self.token}"})

    @task(2)
    def list_agents(self):
        """List agents."""
        if self.token:
            self.client.get(
                "/api/v1/agents/list", headers={"Authorization": f"Bearer {self.token}"}
            )

    @task(1)
    def list_tasks(self):
        """List scheduled tasks."""
        if self.token:
            self.client.get(
                "/api/v1/scheduler/list", headers={"Authorization": f"Bearer {self.token}"}
            )
