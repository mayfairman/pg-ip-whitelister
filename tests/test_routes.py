"""Tests for API routes."""

import json
from unittest.mock import patch, MagicMock


def test_index_route(client):
    """Test the main index route."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'IP Whitelister for Pangolin' in response.data


def test_client_ip_route(client):
    """Test the client IP detection route."""
    with patch('app.routes.request') as mock_request:
        mock_request.remote_addr = '192.168.1.1'
        
        response = client.get('/api/client-ip')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['ip'] == '192.168.1.1'


def test_client_ip_route_no_ip(client):
    """Test client IP route when IP cannot be determined."""
    with patch('app.routes.request') as mock_request:
        mock_request.remote_addr = None
        
        response = client.get('/api/client-ip')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data


@patch('app.routes.PangolinAPI')
def test_resources_route_success(mock_pangolin_api_class, client):
    """Test successful resources retrieval."""
    # Setup mock API instance
    mock_api = MagicMock()
    mock_pangolin_api_class.return_value = mock_api
    
    mock_resources = [
        {'resourceId': 1, 'name': 'Test Resource', 'whitelist': True}
    ]
    mock_api.get_resources.return_value = mock_resources
    
    response = client.get('/api/resources')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['data'] == mock_resources


@patch('app.routes.PangolinAPI')
def test_resources_route_failure(mock_pangolin_api_class, client):
    """Test resources route when API fails."""
    # Setup mock API instance
    mock_api = MagicMock()
    mock_pangolin_api_class.return_value = mock_api
    
    mock_api.get_resources.return_value = None
    
    response = client.get('/api/resources')
    assert response.status_code == 500
    
    data = json.loads(response.data)
    assert data['success'] is False
    assert 'error' in data


@patch('app.routes.PangolinAPI')
def test_check_whitelist_invalid_data(mock_pangolin_api_class, client):
    """Test whitelist check with invalid data."""
    # Setup mock API instance
    mock_api = MagicMock()
    mock_pangolin_api_class.return_value = mock_api
    
    response = client.post('/api/check-whitelist', 
                          data=json.dumps({}),
                          content_type='application/json')
    assert response.status_code == 400
    
    data = json.loads(response.data)
    assert data['success'] is False


@patch('app.routes.PangolinAPI')
def test_whitelist_invalid_ip(mock_pangolin_api_class, client):
    """Test whitelist endpoint with invalid IP."""
    # Setup mock API instance
    mock_api = MagicMock()
    mock_pangolin_api_class.return_value = mock_api
    
    response = client.post('/api/whitelist',
                          data=json.dumps({
                              'resourceId': 1,
                              'ip': 'invalid-ip'
                          }),
                          content_type='application/json')
    assert response.status_code == 400
    
    data = json.loads(response.data)
    assert data['success'] is False
    assert 'error' in data


@patch('app.routes.PangolinAPI')
def test_check_whitelist_success(mock_pangolin_api_class, client):
    """Test successful whitelist check."""
    # Setup mock API instance
    mock_api = MagicMock()
    mock_pangolin_api_class.return_value = mock_api
    
    mock_api.check_ip_whitelisted.return_value = True
    
    response = client.post('/api/check-whitelist',
                          data=json.dumps({
                              'resourceId': 1,
                              'ip': '192.168.1.1'
                          }),
                          content_type='application/json')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['isWhitelisted'] is True


@patch('app.routes.PangolinAPI')
def test_whitelist_success(mock_pangolin_api_class, client):
    """Test successful IP whitelisting."""
    # Setup mock API instance
    mock_api = MagicMock()
    mock_pangolin_api_class.return_value = mock_api
    
    mock_api.add_ip_to_whitelist.return_value = {
        'success': True,
        'message': 'IP successfully whitelisted',
        'rule': {'ruleId': 123}
    }
    
    response = client.post('/api/whitelist',
                          data=json.dumps({
                              'resourceId': 1,
                              'ip': '192.168.1.1'
                          }),
                          content_type='application/json')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'ruleId' in data['rule']


@patch('app.routes.PangolinAPI')
def test_resource_rules_success(mock_pangolin_api_class, client):
    """Test successful resource rules retrieval."""
    # Setup mock API instance
    mock_api = MagicMock()
    mock_pangolin_api_class.return_value = mock_api
    
    mock_rules = [
        {'ruleId': 1, 'action': 'ACCEPT', 'value': '192.168.1.1'}
    ]
    mock_api.get_resource_rules.return_value = mock_rules
    
    response = client.get('/api/resource/1/rules')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['data'] == mock_rules


def test_resource_rules_invalid_id(client):
    """Test resource rules with invalid resource ID."""
    response = client.get('/api/resource/0/rules')
    assert response.status_code == 400
    
    data = json.loads(response.data)
    assert data['success'] is False
    assert 'error' in data 