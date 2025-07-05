import logging

from flask import Blueprint, Response, jsonify, render_template, request

from app.pangolin_api import PangolinAPI
from app.utils import get_real_ip, validate_ip_address

main = Blueprint("main", __name__)
logger = logging.getLogger(__name__)


@main.route("/")
def index():
    """Render the main application page"""
    return render_template("index.html")


@main.route("/api/client-ip", methods=["GET"])
def client_ip():
    """Return the client's real IP address using external IP services"""
    try:
        # Get the real client IP address using ipify and fallbacks
        ip = get_real_ip(request, depth=0)  # Adjust depth as needed

        if not ip:
            logger.warning("Could not determine client IP from external services")
            return (
                jsonify(
                    {"success": False, "error": "Could not determine client IP address"}
                ),
                400,
            )

        logger.info(f"Client IP detected: {ip}")
        return jsonify({"success": True, "ip": ip})

    except Exception as e:
        logger.error(f"Error detecting client IP: {e}")
        return jsonify({"success": False, "error": "Failed to detect IP address"}), 500


@main.route("/api/resources", methods=["GET"])
def resources():
    """Get all resources from Pangolin API."""
    try:
        pangolin_api = PangolinAPI()
        resources = pangolin_api.get_resources()

        if resources is None:
            logger.error("PangolinAPI.get_resources() returned None")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Failed to fetch resources from Pangolin API",
                    }
                ),
                500,
            )

        # Sanitise resource data before logging
        resource_count = len(resources) if isinstance(resources, list) else 0
        logger.info(f"Retrieved {resource_count} resources from Pangolin API")

        return jsonify({"success": True, "data": resources})

    except Exception as e:
        logger.error(f"Error fetching resources: {e}")
        return jsonify({"success": False, "error": "Failed to fetch resources"}), 500


@main.route("/api/resource/<int:resource_id>/rules", methods=["GET"])
def resource_rules(resource_id: int) -> Response | tuple[Response, int]:
    """Get rules for a specific resource"""
    try:
        # Validate resource_id
        if resource_id <= 0 or resource_id > 999999999:
            logger.warning(f"Invalid resource_id: {resource_id}")
            return jsonify({"success": False, "error": "Invalid resource ID"}), 400

        pangolin_api = PangolinAPI()
        rules = pangolin_api.get_resource_rules(resource_id)

        if rules is None:
            logger.error(f"Failed to fetch rules for resource {resource_id}")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Failed to fetch rules from Pangolin API",
                    }
                ),
                500,
            )

        rule_count = len(rules) if isinstance(rules, list) else 0
        logger.info(f"Retrieved {rule_count} rules for resource {resource_id}")

        return jsonify({"success": True, "data": rules})

    except Exception as e:
        logger.error(f"Error fetching rules for resource {resource_id}: {e}")
        return (
            jsonify({"success": False, "error": "Failed to fetch resource rules"}),
            500,
        )


@main.route("/api/check-whitelist", methods=["POST"])
def check_whitelist() -> Response | tuple[Response, int]:
    """Check if an IP is already whitelisted for a resource."""
    try:
        data = request.get_json()

        if not data:
            logger.error("No JSON data provided to check-whitelist endpoint")
            return jsonify({"success": False, "error": "No JSON data provided"}), 400

        pangolin_api = PangolinAPI()
        resource_id = data.get("resourceId")
        ip = data.get("ip")

        # Input validation
        try:
            if resource_id is not None:
                resource_id = int(resource_id)
            if not resource_id or resource_id <= 0:
                logger.error(
                    f"Invalid resource_id: {resource_id} (type: {type(resource_id)})"
                )
                return jsonify({"success": False, "error": "Invalid resource ID"}), 400
        except (ValueError, TypeError):
            logger.error(f"Invalid resource_id format: {data.get('resourceId')}")
            return (
                jsonify({"success": False, "error": "Invalid resource ID format"}),
                400,
            )

        if not ip or not validate_ip_address(ip):
            logger.error(f"Invalid IP address: {ip}")
            return jsonify({"success": False, "error": "Invalid IP address"}), 400

        is_whitelisted = pangolin_api.check_ip_whitelisted(resource_id, ip)

        logger.info(
            f"Checked whitelist status for IP {ip} on resource {resource_id}: {is_whitelisted}"
        )

        return jsonify({"success": True, "isWhitelisted": is_whitelisted})

    except Exception as e:
        logger.error(f"Error checking whitelist status: {e}")
        return (
            jsonify({"success": False, "error": "Failed to check whitelist status"}),
            500,
        )


@main.route("/api/whitelist", methods=["POST"])
def whitelist() -> Response | tuple[Response, int]:
    """Add IP to whitelist for a resource."""
    try:
        data = request.get_json()

        if not data:
            logger.error("No JSON data provided to whitelist endpoint")
            return jsonify({"success": False, "error": "No JSON data provided"}), 400

        pangolin_api = PangolinAPI()
        resource_id = data.get("resourceId")
        ip = data.get("ip")

        # Input validation
        try:
            if resource_id is not None:
                resource_id = int(resource_id)
            if not resource_id or resource_id <= 0:
                logger.error(
                    f"Invalid resource_id: {resource_id} (type: {type(resource_id)})"
                )
                return jsonify({"success": False, "error": "Invalid resource ID"}), 400
        except (ValueError, TypeError):
            logger.error(f"Invalid resource_id format: {data.get('resourceId')}")
            return (
                jsonify({"success": False, "error": "Invalid resource ID format"}),
                400,
            )

        if not ip or not validate_ip_address(ip):
            logger.error(f"Invalid IP address: {ip}")
            return jsonify({"success": False, "error": "Invalid IP address"}), 400

        result = pangolin_api.add_ip_to_whitelist(resource_id, ip)

        if result.get("success"):
            logger.info(f"Successfully whitelisted IP {ip} for resource {resource_id}")
        else:
            logger.warning(
                f"Failed to whitelist IP {ip} for resource {resource_id}: {result.get('message')}"
            )

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error adding IP to whitelist: {e}")
        return (
            jsonify({"success": False, "error": "Failed to add IP to whitelist"}),
            500,
        )


@main.route("/api/resource/<int:resource_id>/rule/<int:rule_id>", methods=["DELETE"])
def delete_rule(resource_id: int, rule_id: int) -> Response | tuple[Response, int]:
    """Delete a specific rule from a resource."""
    try:
        # Validate resource_id
        if resource_id <= 0 or resource_id > 999999999:
            logger.warning(f"Invalid resource_id: {resource_id}")
            return jsonify({"success": False, "error": "Invalid resource ID"}), 400

        # Validate rule_id
        if rule_id <= 0 or rule_id > 999999999:
            logger.warning(f"Invalid rule_id: {rule_id}")
            return jsonify({"success": False, "error": "Invalid rule ID"}), 400

        pangolin_api = PangolinAPI()
        result = pangolin_api.delete_rule(resource_id, rule_id)

        if result.get("success"):
            logger.info(
                f"Successfully deleted rule {rule_id} from resource {resource_id}"
            )
        else:
            logger.warning(
                f"Failed to delete rule {rule_id} from resource {resource_id}: {result.get('message')}"
            )

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error deleting rule {rule_id} from resource {resource_id}: {e}")
        return (
            jsonify({"success": False, "error": "Failed to delete rule"}),
            500,
        )


@main.route("/api/resource/<int:resource_id>/ip-rules", methods=["DELETE"])
def delete_all_ip_rules(resource_id: int) -> Response | tuple[Response, int]:
    """Delete all IP whitelist rules from a resource."""
    try:
        # Validate resource_id
        if resource_id <= 0 or resource_id > 999999999:
            logger.warning(f"Invalid resource_id: {resource_id}")
            return jsonify({"success": False, "error": "Invalid resource ID"}), 400

        pangolin_api = PangolinAPI()
        result = pangolin_api.delete_all_ip_rules(resource_id)

        if result.get("success"):
            deleted_count = result.get("deleted_count", 0)
            logger.info(
                f"Successfully deleted {deleted_count} IP rules from resource {resource_id}"
            )
        else:
            logger.warning(
                f"Failed to delete IP rules from resource {resource_id}: {result.get('message')}"
            )

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error deleting IP rules from resource {resource_id}: {e}")
        return (
            jsonify({"success": False, "error": "Failed to delete IP rules"}),
            500,
        )


@main.route("/api/resource/<int:resource_id>/replace-ip-whitelist", methods=["PUT"])
def replace_ip_whitelist(resource_id: int) -> Response | tuple[Response, int]:
    """Replace all IP whitelist rules with current IP."""
    try:
        try:
            data = request.get_json()
        except Exception as e:
            logger.error(f"Failed to parse JSON data: {e}")
            return jsonify({"success": False, "error": "Invalid JSON data"}), 400

        if not data:
            logger.error("No JSON data provided to replace-ip-whitelist endpoint")
            return jsonify({"success": False, "error": "No JSON data provided"}), 400

        # Validate resource_id
        if resource_id <= 0 or resource_id > 999999999:
            logger.warning(f"Invalid resource_id: {resource_id}")
            return jsonify({"success": False, "error": "Invalid resource ID"}), 400

        ip = data.get("ip")
        if not ip or not validate_ip_address(ip):
            logger.error(f"Invalid IP address: {ip}")
            return jsonify({"success": False, "error": "Invalid IP address"}), 400

        pangolin_api = PangolinAPI()
        result = pangolin_api.replace_ip_whitelist(resource_id, ip)

        if result.get("success"):
            deleted_count = result.get("deleted_count", 0)
            logger.info(
                f"Successfully replaced IP whitelist for resource {resource_id} (deleted {deleted_count} rules, added {ip})"
            )
        else:
            logger.warning(
                f"Failed to replace IP whitelist for resource {resource_id}: {result.get('message')}"
            )

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error replacing IP whitelist for resource {resource_id}: {e}")
        return (
            jsonify({"success": False, "error": "Failed to replace IP whitelist"}),
            500,
        )
