from flask import Blueprint, render_template, request, jsonify, current_app
from app.pangolin_api import PangolinAPI
from app.utils import validate_ip_address
import logging

main = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

@main.route('/')
def index():
    """Render the main application page"""
    return render_template('index.html')

@main.route('/api/client-ip', methods=['GET'])
def client_ip():
    """Return the client's direct IP address"""
    try:
        # Get the direct client IP address without relying on headers
        ip = request.remote_addr
        
        if not ip or ip == 'unknown':
            return jsonify({
                'success': False,
                'error': 'Could not determine client IP address'
            }), 400
        
        logger.info(f"Client IP detected: {ip}")
        return jsonify({
            'success': True,
            'ip': ip
        })
        
    except Exception as e:
        logger.error(f"Error detecting client IP: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to detect IP address'
        }), 500
        
@main.route('/api/resources', methods=['GET'])
def resources():
    """Get all resources from Pangolin API."""
    try:
        pangolin_api = PangolinAPI()
        resources = pangolin_api.get_resources()
        
        if resources is None:
            logger.error("PangolinAPI.get_resources() returned None")
            return jsonify({
                'success': False,
                'error': 'Failed to fetch resources from Pangolin API'
            }), 500
        
        logger.info(f"Retrieved {len(resources)} resources from Pangolin API")
        return jsonify({
            'success': True,
            'data': resources
        })
        
    except Exception as e:
        logger.error(f"Error fetching resources: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch resources'
        }), 500

@main.route('/api/resource/<int:resource_id>/rules', methods=['GET'])
def resource_rules(resource_id):
    """Get rules for a specific resource"""
    try:
        if resource_id <= 0:
            return jsonify({
                'success': False,
                'error': 'Invalid resource ID'
            }), 400
        
        pangolin_api = PangolinAPI()
        rules = pangolin_api.get_resource_rules(resource_id)
        
        if rules is None:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch rules from Pangolin API'
            }), 500
        
        logger.info(f"Retrieved {len(rules)} rules for resource {resource_id}")
        return jsonify({
            'success': True,
            'data': rules
        })
        
    except Exception as e:
        logger.error(f"Error fetching rules for resource {resource_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch resource rules'
        }), 500

@main.route('/api/check-whitelist', methods=['POST'])
def check_whitelist():
    """Check if an IP is already whitelisted for a resource."""
    try:
        data = request.get_json()
        
        if not data:
            logger.error("No JSON data provided to check-whitelist endpoint")
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        pangolin_api = PangolinAPI()
        resource_id = data.get('resourceId')
        ip = data.get('ip')
        
        # Input validation
        try:
            if resource_id is not None:
                resource_id = int(resource_id)
            if not resource_id or resource_id <= 0:
                logger.error(f"Invalid resource_id: {resource_id} (type: {type(resource_id)})")
                return jsonify({
                    'success': False,
                    'error': 'Invalid resource ID'
                }), 400
        except (ValueError, TypeError):
            logger.error(f"Invalid resource_id format: {data.get('resourceId')}")
            return jsonify({
                'success': False,
                'error': 'Invalid resource ID format'
            }), 400
        
        if not ip or not validate_ip_address(ip):
            logger.error(f"Invalid IP address: {ip}")
            return jsonify({
                'success': False,
                'error': 'Invalid IP address'
            }), 400
        
        is_whitelisted = pangolin_api.check_ip_whitelisted(resource_id, ip)
        
        logger.info(f"Checked whitelist status for IP {ip} on resource {resource_id}: {is_whitelisted}")
        
        result = {
            'success': True,
            'isWhitelisted': is_whitelisted
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error checking whitelist status: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to check whitelist status'
        }), 500

@main.route('/api/whitelist', methods=['POST'])
def whitelist():
    """Add IP to whitelist for a resource."""
    try:
        data = request.get_json()
        
        if not data:
            logger.error("No JSON data provided to whitelist endpoint")
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        pangolin_api = PangolinAPI()
        resource_id = data.get('resourceId')
        ip = data.get('ip')
        
        # Input validation
        try:
            if resource_id is not None:
                resource_id = int(resource_id)
            if not resource_id or resource_id <= 0:
                logger.error(f"Invalid resource_id: {resource_id} (type: {type(resource_id)})")
                return jsonify({
                    'success': False,
                    'error': 'Invalid resource ID'
                }), 400
        except (ValueError, TypeError):
            logger.error(f"Invalid resource_id format: {data.get('resourceId')}")
            return jsonify({
                'success': False,
                'error': 'Invalid resource ID format'
            }), 400
        
        if not ip or not validate_ip_address(ip):
            logger.error(f"Invalid IP address: {ip}")
            return jsonify({
                'success': False,
                'error': 'Invalid IP address'
            }), 400
        
        result = pangolin_api.add_ip_to_whitelist(resource_id, ip)
        
        if result.get('success'):
            logger.info(f"Successfully whitelisted IP {ip} for resource {resource_id}")
        else:
            logger.warning(f"Failed to whitelist IP {ip} for resource {resource_id}: {result.get('message')}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error adding IP to whitelist: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to add IP to whitelist'
        }), 500