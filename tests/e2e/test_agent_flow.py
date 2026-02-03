"""
End-to-end tests for agent management workflow.

Tests the complete agent lifecycle:
1. User authentication
2. Create agent
3. List agents
4. Get agent details
5. Update agent
6. Delete agent
"""

import pytest


@pytest.mark.e2e
class TestAgentManagementWorkflow:
    """Test complete agent management workflow."""

    def test_complete_agent_lifecycle(self, client, authenticated_user):
        """
        Test complete agent lifecycle:
        1. Create agent
        2. List agents
        3. Get agent details
        4. Update agent
        5. Delete agent
        """
        headers = {"Authorization": f"Bearer {authenticated_user}"}

        # Step 1: Create agent
        agent_data = {
            "name": "test-agent",
            "system_prompt": "You are a helpful assistant",
            "capabilities": ["chat", "analysis"],
        }
        response = client.post("/api/v1/agents/create", headers=headers, json=agent_data)
        assert response.status_code in [200, 201]
        agent = response.json()
        assert agent["name"] == "test-agent"
        assert agent["system_prompt"] == "You are a helpful assistant"
        assert "chat" in agent["capabilities"]

        # Step 2: List agents
        response = client.get("/api/v1/agents/list", headers=headers)
        assert response.status_code == 200
        agents = response.json()
        assert len(agents) >= 1
        assert any(a["name"] == "test-agent" for a in agents)

        # Step 3: Get agent details
        response = client.get("/api/v1/agents/test-agent", headers=headers)
        assert response.status_code == 200
        agent_details = response.json()
        assert agent_details["name"] == "test-agent"
        assert agent_details["system_prompt"] == "You are a helpful assistant"

        # Step 4: Update agent
        update_data = {
            "system_prompt": "You are an advanced AI assistant",
            "capabilities": ["chat", "analysis", "coding"],
        }
        response = client.put(
            "/api/v1/agents/test-agent", headers=headers, json=update_data
        )
        assert response.status_code == 200
        updated_agent = response.json()
        assert updated_agent["system_prompt"] == "You are an advanced AI assistant"
        assert "coding" in updated_agent["capabilities"]

        # Step 5: Delete agent
        response = client.delete("/api/v1/agents/test-agent", headers=headers)
        assert response.status_code == 200

        # Verify deletion
        response = client.get("/api/v1/agents/test-agent", headers=headers)
        assert response.status_code == 404

    def test_create_duplicate_agent(self, client, authenticated_user):
        """Test creating agent with duplicate name."""
        headers = {"Authorization": f"Bearer {authenticated_user}"}

        # Create first agent
        agent_data = {
            "name": "duplicate-agent",
            "system_prompt": "Test",
            "capabilities": ["chat"],
        }
        response = client.post("/api/v1/agents/create", headers=headers, json=agent_data)
        assert response.status_code in [200, 201]

        # Try to create duplicate
        response = client.post("/api/v1/agents/create", headers=headers, json=agent_data)
        assert response.status_code == 400

        # Cleanup
        client.delete("/api/v1/agents/duplicate-agent", headers=headers)

    def test_unauthorized_agent_access(self, client):
        """Test accessing agent endpoints without authentication."""
        # Try to create without auth
        agent_data = {
            "name": "test",
            "system_prompt": "Test",
            "capabilities": ["chat"],
        }
        response = client.post("/api/v1/agents/create", json=agent_data)
        assert response.status_code == 401

        # Try to list without auth
        response = client.get("/api/v1/agents/list")
        assert response.status_code == 401

        # Try to get without auth
        response = client.get("/api/v1/agents/test")
        assert response.status_code == 401

        # Try to update without auth
        response = client.put("/api/v1/agents/test", json={"system_prompt": "Test"})
        assert response.status_code == 401

        # Try to delete without auth
        response = client.delete("/api/v1/agents/test")
        assert response.status_code == 401

    def test_invalid_agent_operations(self, client, authenticated_user):
        """Test invalid agent operations."""
        headers = {"Authorization": f"Bearer {authenticated_user}"}

        # Try to get non-existent agent
        response = client.get("/api/v1/agents/non-existent", headers=headers)
        assert response.status_code == 404

        # Try to update non-existent agent
        response = client.put(
            "/api/v1/agents/non-existent",
            headers=headers,
            json={"system_prompt": "Test"},
        )
        assert response.status_code == 404

        # Try to delete non-existent agent
        response = client.delete("/api/v1/agents/non-existent", headers=headers)
        assert response.status_code == 404

    def test_agent_capability_management(self, client, authenticated_user):
        """Test managing agent capabilities."""
        headers = {"Authorization": f"Bearer {authenticated_user}"}

        # Create agent with initial capabilities
        agent_data = {
            "name": "capability-agent",
            "system_prompt": "Test",
            "capabilities": ["chat"],
        }
        response = client.post("/api/v1/agents/create", headers=headers, json=agent_data)
        assert response.status_code in [200, 201]

        # Update to add more capabilities
        update_data = {"capabilities": ["chat", "analysis", "coding", "search"]}
        response = client.put(
            "/api/v1/agents/capability-agent", headers=headers, json=update_data
        )
        assert response.status_code == 200
        agent = response.json()
        assert len(agent["capabilities"]) == 4
        assert all(cap in agent["capabilities"] for cap in update_data["capabilities"])

        # Update to remove capabilities
        update_data = {"capabilities": ["chat"]}
        response = client.put(
            "/api/v1/agents/capability-agent", headers=headers, json=update_data
        )
        assert response.status_code == 200
        agent = response.json()
        assert len(agent["capabilities"]) == 1
        assert agent["capabilities"][0] == "chat"

        # Cleanup
        client.delete("/api/v1/agents/capability-agent", headers=headers)
