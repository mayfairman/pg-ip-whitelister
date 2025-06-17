"""Tests for PangolinAPI class."""

import pytest
from unittest.mock import patch, MagicMock
from app.pangolin_api import PangolinAPI, PangolinAPIError


class TestPangolinAPI:
    """Test cases for PangolinAPI class."""

    def test_init_with_config(self):
        """Test PangolinAPI initialization with config."""
        config = {
            'PANGOLIN_API_URL': 'https://test-api.com/v1',
            'PANGOLIN_API_KEY': 'test-key',
            'PANGOLIN_ORG_ID': 'test-org'
        }
        
        api = PangolinAPI(config)
        
        assert api.base_url == 'https://test-api.com/v1'
        assert api.api_key == 'test-key'
        assert api.org_id == 'test-org'
        assert 'Authorization' in api.headers
        assert api.headers['Authorization'] == 'Bearer test-key'

    def test_init_without_config(self):
        """Test PangolinAPI initialization without config."""
        api = PangolinAPI()
        
        assert api.base_url == ''
        assert api.api_key == ''
        assert api.org_id == ''

    @patch('app.pangolin_api.requests.Session')
    def test_make_request_success(self, mock_session):
        """Test successful API request."""
        mock_response = MagicMock()
        mock_response.json.return_value = {'success': True, 'data': 'test'}
        mock_response.raise_for_status.return_value = None
        
        mock_session_instance = MagicMock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        api = PangolinAPI({
            'PANGOLIN_API_URL': 'https://test-api.com/v1',
            'PANGOLIN_API_KEY': 'test-key',
            'PANGOLIN_ORG_ID': 'test-org'
        })
        
        result = api._make_request('GET', 'test/endpoint')
        
        assert result == {'success': True, 'data': 'test'}
        mock_session_instance.request.assert_called_once()

    @patch('app.pangolin_api.requests.Session')
    def test_make_request_http_error(self, mock_session):
        """Test API request with HTTP error."""
        from requests.exceptions import HTTPError
        
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = HTTPError('404 Not Found')
        
        mock_session_instance = MagicMock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        api = PangolinAPI()
        
        with pytest.raises(PangolinAPIError, match='API request failed'):
            api._make_request('GET', 'test/endpoint')

    @patch('app.pangolin_api.requests.Session')
    def test_make_request_json_error(self, mock_session):
        """Test API request with JSON parsing error."""
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError('Invalid JSON')
        mock_response.raise_for_status.return_value = None
        
        mock_session_instance = MagicMock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        api = PangolinAPI()
        
        with pytest.raises(PangolinAPIError, match='Invalid JSON response'):
            api._make_request('GET', 'test/endpoint')

    @patch.object(PangolinAPI, '_make_request')
    def test_get_resources_success(self, mock_make_request):
        """Test successful resources retrieval."""
        mock_make_request.return_value = {
            'success': True,
            'data': {'resources': [{'id': 1, 'name': 'Test'}]}
        }
        
        api = PangolinAPI({'PANGOLIN_ORG_ID': 'test-org'})
        result = api.get_resources()
        
        assert result == [{'id': 1, 'name': 'Test'}]
        mock_make_request.assert_called_once_with('GET', 'org/test-org/resources')

    @patch.object(PangolinAPI, '_make_request')
    def test_get_resources_failure(self, mock_make_request):
        """Test resources retrieval failure."""
        mock_make_request.return_value = {'success': False}
        
        api = PangolinAPI({'PANGOLIN_ORG_ID': 'test-org'})
        result = api.get_resources()
        
        assert result is None

    @patch.object(PangolinAPI, '_make_request')
    def test_get_resources_api_error(self, mock_make_request):
        """Test resources retrieval with API error."""
        mock_make_request.side_effect = PangolinAPIError('API Error')
        
        api = PangolinAPI({'PANGOLIN_ORG_ID': 'test-org'})
        result = api.get_resources()
        
        assert result is None

    @patch.object(PangolinAPI, '_make_request')
    def test_get_resource_rules_success(self, mock_make_request):
        """Test successful resource rules retrieval."""
        mock_make_request.return_value = {
            'success': True,
            'data': {'rules': [{'id': 1, 'action': 'ACCEPT'}]}
        }
        
        api = PangolinAPI()
        result = api.get_resource_rules(1)
        
        assert result == [{'id': 1, 'action': 'ACCEPT'}]
        mock_make_request.assert_called_once_with('GET', 'resource/1/rules')

    def test_get_resource_rules_invalid_id(self):
        """Test resource rules with invalid ID."""
        api = PangolinAPI()
        
        # Should return None for invalid IDs (not raise ValueError)
        result = api.get_resource_rules(0)
        assert result is None
        
        result = api.get_resource_rules(-1)
        assert result is None

    @patch.object(PangolinAPI, 'get_resource_rules')
    def test_check_ip_whitelisted_true(self, mock_get_rules):
        """Test IP whitelist check - IP is whitelisted."""
        mock_get_rules.return_value = [
            {
                'match': 'IP',
                'action': 'ACCEPT',
                'value': '192.168.1.1',
                'enabled': True
            }
        ]
        
        api = PangolinAPI()
        result = api.check_ip_whitelisted(1, '192.168.1.1')
        
        assert result is True

    @patch.object(PangolinAPI, 'get_resource_rules')
    def test_check_ip_whitelisted_false(self, mock_get_rules):
        """Test IP whitelist check - IP is not whitelisted."""
        mock_get_rules.return_value = [
            {
                'match': 'IP',
                'action': 'ACCEPT',
                'value': '192.168.1.2',
                'enabled': True
            }
        ]
        
        api = PangolinAPI()
        result = api.check_ip_whitelisted(1, '192.168.1.1')
        
        assert result is False

    def test_check_ip_whitelisted_invalid_ip(self):
        """Test IP whitelist check with invalid IP."""
        api = PangolinAPI()
        result = api.check_ip_whitelisted(1, 'invalid-ip')
        
        assert result is False

    @patch.object(PangolinAPI, 'get_resource_rules')
    def test_get_next_priority(self, mock_get_rules):
        """Test next priority calculation."""
        mock_get_rules.return_value = [
            {'priority': 1},
            {'priority': 3},
            {'priority': 5}
        ]
        
        api = PangolinAPI()
        result = api.get_next_priority(1)
        
        assert result == 6

    @patch.object(PangolinAPI, 'get_resource_rules')
    def test_get_next_priority_no_rules(self, mock_get_rules):
        """Test next priority calculation with no existing rules."""
        mock_get_rules.return_value = []
        
        api = PangolinAPI()
        result = api.get_next_priority(1)
        
        assert result == 1

    @patch.object(PangolinAPI, '_make_request')
    def test_add_ip_to_whitelist_success(self, mock_make_request):
        """Test successful IP whitelisting."""
        mock_make_request.return_value = {
            'success': True,
            'data': {'ruleId': 123}
        }
        
        api = PangolinAPI()
        result = api.add_ip_to_whitelist(1, '192.168.1.1')
        
        assert result['success'] is True
        assert 'ruleId' in result['rule']

    @patch.object(PangolinAPI, '_make_request')
    def test_add_ip_to_whitelist_failure(self, mock_make_request):
        """Test IP whitelisting failure."""
        mock_make_request.return_value = {
            'success': False,
            'message': 'Failed to whitelist IP'
        }
        
        api = PangolinAPI()
        result = api.add_ip_to_whitelist(1, '192.168.1.1')
        
        assert result['success'] is False 