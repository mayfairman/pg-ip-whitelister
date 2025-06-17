"""Integration tests for the full application workflow."""

import json
import pytest
from unittest.mock import patch, MagicMock


class TestIntegration:
    """Integration test cases for the full application workflow."""

    def test_full_whitelist_workflow(self, client):
        """Test the complete whitelisting workflow."""
        # Mock the PangolinAPI responses
        mock_resources = [
            {
                'resourceId': 1,
                'name': 'Test Resource 1',
                'enabled': True,
                'whitelist': True,
                'fullDomain': 'test1.example.com'
            },
            {
                'resourceId': 2,
                'name': 'Test Resource 2',
                'enabled': True,
                'whitelist': False,
                'fullDomain': 'test2.example.com'
            }
        ]
        
        mock_rules = [
            {
                'match': 'IP',
                'action': 'ACCEPT',
                'value': '192.168.1.1',
                'enabled': True,
                'priority': 1
            }
        ]
        
        with patch('app.routes.PangolinAPI') as MockPangolinAPI:
            # Setup mock API
            mock_api = MagicMock()
            MockPangolinAPI.return_value = mock_api
            
            # Mock get_resources
            mock_api.get_resources.return_value = mock_resources
            
            # Mock check_ip_whitelisted
            mock_api.check_ip_whitelisted.side_effect = [False, True]  # First resource not whitelisted, second is
            
            # Mock add_ip_to_whitelist
            mock_api.add_ip_to_whitelist.return_value = {
                'success': True,
                'message': 'IP successfully whitelisted',
                'rule': {'ruleId': 123}
            }
            
            # Test 1: Get resources
            response = client.get('/api/resources')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert len(data['data']) == 2
            
            # Test 2: Get client IP
            with patch('app.routes.request') as mock_request:
                mock_request.remote_addr = '192.168.1.1'
                response = client.get('/api/client-ip')
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
                assert data['ip'] == '192.168.1.1'
            
            # Test 3: Check whitelist status
            response = client.post('/api/check-whitelist',
                                 data=json.dumps({
                                     'resourceId': 1,
                                     'ip': '192.168.1.1'
                                 }),
                                 content_type='application/json')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['isWhitelisted'] is False
            
            # Test 4: Add IP to whitelist
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

    def test_error_handling_workflow(self, client):
        """Test error handling in the workflow."""
        with patch('app.routes.PangolinAPI') as MockPangolinAPI:
            # Setup mock API to simulate failures
            mock_api = MagicMock()
            MockPangolinAPI.return_value = mock_api
            
            # Test API failure
            mock_api.get_resources.return_value = None
            
            response = client.get('/api/resources')
            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'error' in data

    def test_invalid_input_handling(self, client):
        """Test handling of invalid input throughout the workflow."""
        # Test invalid resource ID
        response = client.post('/api/check-whitelist',
                             data=json.dumps({
                                 'resourceId': 'invalid',
                                 'ip': '192.168.1.1'
                             }),
                             content_type='application/json')
        assert response.status_code == 400
        
        # Test invalid IP
        response = client.post('/api/whitelist',
                             data=json.dumps({
                                 'resourceId': 1,
                                 'ip': 'invalid-ip'
                             }),
                             content_type='application/json')
        assert response.status_code == 400
        
        # Test missing data
        response = client.post('/api/whitelist',
                             data=json.dumps({}),
                             content_type='application/json')
        assert response.status_code == 400

    def test_frontend_integration_simulation(self, client):
        """Simulate frontend integration by testing the complete API flow."""
        with patch('app.routes.PangolinAPI') as MockPangolinAPI:
            mock_api = MagicMock()
            MockPangolinAPI.return_value = mock_api
            
            # Setup realistic API responses
            mock_api.get_resources.return_value = [
                {
                    'resourceId': 1,
                    'name': 'Plex',
                    'enabled': True,
                    'whitelist': True,
                    'fullDomain': 'plex.example.com'
                }
            ]
            
            mock_api.check_ip_whitelisted.return_value = False
            mock_api.add_ip_to_whitelist.return_value = {
                'success': True,
                'message': 'IP successfully whitelisted',
                'rule': {'ruleId': 456}
            }
            
            # Simulate frontend workflow
            # 1. Load resources
            response = client.get('/api/resources')
            assert response.status_code == 200
            
            # 2. Get client IP
            with patch('app.routes.request') as mock_request:
                mock_request.remote_addr = '10.0.0.1'
                response = client.get('/api/client-ip')
                assert response.status_code == 200
                client_ip = json.loads(response.data)['ip']
            
            # 3. Check whitelist status
            response = client.post('/api/check-whitelist',
                                 data=json.dumps({
                                     'resourceId': 1,
                                     'ip': client_ip
                                 }),
                                 content_type='application/json')
            assert response.status_code == 200
            assert json.loads(response.data)['isWhitelisted'] is False
            
            # 4. Whitelist IP
            response = client.post('/api/whitelist',
                                 data=json.dumps({
                                     'resourceId': 1,
                                     'ip': client_ip
                                 }),
                                 content_type='application/json')
            assert response.status_code == 200
            assert json.loads(response.data)['success'] is True

    def test_concurrent_requests(self, client):
        """Test handling of concurrent requests."""
        import threading
        import time
        
        results = []
        
        def make_request():
            with patch('app.routes.PangolinAPI') as MockPangolinAPI:
                mock_api = MagicMock()
                MockPangolinAPI.return_value = mock_api
                mock_api.get_resources.return_value = [{'resourceId': 1, 'name': 'Test'}]
                
                response = client.get('/api/resources')
                results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 5 