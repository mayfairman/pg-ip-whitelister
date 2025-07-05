from unittest.mock import patch

import pytest

from app import create_app
from app.pangolin_api import PangolinAPI


class TestIPManagement:
    """Test IP management functionality."""

    @pytest.fixture
    def app(self):
        """Create test app."""
        config = {
            "TESTING": True,
            "PANGOLIN_API_URL": "http://test-api",
            "PANGOLIN_API_KEY": "test-key",
            "PANGOLIN_ORG_ID": "test-org",
        }
        return create_app(config)

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()

    @patch.object(PangolinAPI, "delete_rule")
    def test_delete_rule_success(self, mock_delete, client):
        """Test successful rule deletion."""
        mock_delete.return_value = {"success": True, "message": "Rule deleted"}

        response = client.delete("/api/resource/1/rule/123")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        mock_delete.assert_called_once_with(1, 123)

    @patch.object(PangolinAPI, "delete_rule")
    def test_delete_rule_failure(self, mock_delete, client):
        """Test rule deletion failure."""
        mock_delete.return_value = {"success": False, "message": "Rule not found"}

        response = client.delete("/api/resource/1/rule/123")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is False
        assert "Rule not found" in data["message"]

    def test_delete_rule_invalid_resource_id(self, client):
        """Test rule deletion with invalid resource ID."""
        response = client.delete("/api/resource/0/rule/123")

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "Invalid resource ID" in data["error"]

    def test_delete_rule_invalid_rule_id(self, client):
        """Test rule deletion with invalid rule ID."""
        response = client.delete("/api/resource/1/rule/0")

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "Invalid rule ID" in data["error"]

    @patch.object(PangolinAPI, "delete_all_ip_rules")
    def test_delete_all_ip_rules_success(self, mock_delete_all, client):
        """Test successful deletion of all IP rules."""
        mock_delete_all.return_value = {
            "success": True,
            "message": "Deleted 3 rules",
            "deleted_count": 3,
        }

        response = client.delete("/api/resource/1/ip-rules")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["deleted_count"] == 3
        mock_delete_all.assert_called_once_with(1)

    @patch.object(PangolinAPI, "delete_all_ip_rules")
    def test_delete_all_ip_rules_none_found(self, mock_delete_all, client):
        """Test deletion when no IP rules exist."""
        mock_delete_all.return_value = {
            "success": True,
            "message": "No IP whitelist rules to delete",
            "deleted_count": 0,
        }

        response = client.delete("/api/resource/1/ip-rules")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["deleted_count"] == 0

    @patch.object(PangolinAPI, "replace_ip_whitelist")
    def test_replace_ip_whitelist_success(self, mock_replace, client):
        """Test successful IP whitelist replacement."""
        mock_replace.return_value = {
            "success": True,
            "message": "Successfully replaced all IP rules with 192.168.1.1",
            "deleted_count": 2,
            "new_rule": {"id": 456, "value": "192.168.1.1"},
        }

        response = client.put(
            "/api/resource/1/replace-ip-whitelist",
            json={"ip": "192.168.1.1"},
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["deleted_count"] == 2
        assert "new_rule" in data
        mock_replace.assert_called_once_with(1, "192.168.1.1")

    def test_replace_ip_whitelist_no_json(self, client):
        """Test replace IP whitelist without JSON data."""
        response = client.put(
            "/api/resource/1/replace-ip-whitelist", content_type="application/json"
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "Invalid JSON data" in data["error"]

    def test_replace_ip_whitelist_invalid_ip(self, client):
        """Test replace IP whitelist with invalid IP."""
        response = client.put(
            "/api/resource/1/replace-ip-whitelist",
            json={"ip": "invalid-ip"},
            content_type="application/json",
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "Invalid IP address" in data["error"]

    def test_replace_ip_whitelist_invalid_resource_id(self, client):
        """Test replace IP whitelist with invalid resource ID."""
        response = client.put(
            "/api/resource/0/replace-ip-whitelist",
            json={"ip": "192.168.1.1"},
            content_type="application/json",
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "Invalid resource ID" in data["error"]


class TestPangolinAPIIPManagement:
    """Test PangolinAPI IP management methods."""

    @pytest.fixture
    def api(self):
        """Create PangolinAPI instance."""
        config = {
            "PANGOLIN_API_URL": "http://test-api",
            "PANGOLIN_API_KEY": "test-key",
            "PANGOLIN_ORG_ID": "test-org",
        }
        return PangolinAPI(config)

    @patch.object(PangolinAPI, "_make_request")
    def test_delete_rule_success(self, mock_request, api):
        """Test successful rule deletion."""
        mock_request.return_value = {"success": True}

        result = api.delete_rule(1, 123)

        assert result["success"] is True
        mock_request.assert_called_once_with("DELETE", "resource/1/rule/123")

    @patch.object(PangolinAPI, "_make_request")
    def test_delete_rule_failure(self, mock_request, api):
        """Test rule deletion failure."""
        mock_request.return_value = {"success": False, "message": "Rule not found"}

        result = api.delete_rule(1, 123)

        assert result["success"] is False
        assert "Rule not found" in result["message"]

    def test_delete_rule_invalid_resource_id(self, api):
        """Test delete rule with invalid resource ID."""
        result = api.delete_rule(0, 123)

        assert result["success"] is False
        assert "Invalid resource ID" in result["message"]

    def test_delete_rule_invalid_rule_id(self, api):
        """Test delete rule with invalid rule ID."""
        result = api.delete_rule(1, 0)

        assert result["success"] is False
        assert "Invalid rule ID" in result["message"]

    @patch.object(PangolinAPI, "get_resource_rules")
    @patch.object(PangolinAPI, "delete_rule")
    def test_delete_all_ip_rules_success(self, mock_delete, mock_get_rules, api):
        """Test successful deletion of all IP rules."""
        mock_get_rules.return_value = [
            {"id": 1, "match": "IP", "action": "ACCEPT", "value": "192.168.1.1"},
            {"id": 2, "match": "IP", "action": "ACCEPT", "value": "192.168.1.2"},
            {"id": 3, "match": "USER", "action": "ACCEPT", "value": "test@example.com"},
        ]
        mock_delete.return_value = {"success": True, "message": "Rule deleted"}

        result = api.delete_all_ip_rules(1)

        assert result["success"] is True
        assert result["deleted_count"] == 2
        assert mock_delete.call_count == 2

    @patch.object(PangolinAPI, "get_resource_rules")
    def test_delete_all_ip_rules_none_found(self, mock_get_rules, api):
        """Test deletion when no IP rules exist."""
        mock_get_rules.return_value = [
            {"id": 3, "match": "USER", "action": "ACCEPT", "value": "test@example.com"}
        ]

        result = api.delete_all_ip_rules(1)

        assert result["success"] is True
        assert result["deleted_count"] == 0
        assert "No IP whitelist rules to delete" in result["message"]

    @patch.object(PangolinAPI, "delete_all_ip_rules")
    @patch.object(PangolinAPI, "add_ip_to_whitelist")
    def test_replace_ip_whitelist_success(self, mock_add, mock_delete, api):
        """Test successful IP whitelist replacement."""
        mock_delete.return_value = {"success": True, "deleted_count": 2}
        mock_add.return_value = {
            "success": True,
            "rule": {"id": 456, "value": "192.168.1.1"},
        }

        result = api.replace_ip_whitelist(1, "192.168.1.1")

        assert result["success"] is True
        assert result["deleted_count"] == 2
        assert "new_rule" in result
        mock_delete.assert_called_once_with(1)
        mock_add.assert_called_once_with(1, "192.168.1.1")

    @patch.object(PangolinAPI, "delete_all_ip_rules")
    def test_replace_ip_whitelist_delete_failure(self, mock_delete, api):
        """Test IP whitelist replacement when delete fails."""
        mock_delete.return_value = {"success": False, "message": "Delete failed"}

        result = api.replace_ip_whitelist(1, "192.168.1.1")

        assert result["success"] is False
        assert "Failed to clear existing IP rules" in result["message"]

    def test_replace_ip_whitelist_invalid_ip(self, api):
        """Test replace IP whitelist with invalid IP."""
        result = api.replace_ip_whitelist(1, "invalid-ip")

        assert result["success"] is False
        assert "Invalid IP address format" in result["message"]
