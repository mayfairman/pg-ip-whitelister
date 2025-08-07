import logging
import os
from typing import Any, Dict, List, Optional

import requests
from flask import current_app

from app.utils import validate_ip_address

logger = logging.getLogger(__name__)


class PangolinAPIError(Exception):
    """Custom exception for Pangolin API errors."""

    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code


class PangolinAPI:
    """Client for interacting with the Pangolin API."""

    def __init__(self, config=None):
        """
        Initialize Pangolin API client.

        Args:
            config: Optional configuration object. If None, uses Flask app config.
        """
        if config is None and current_app:
            config = current_app.config
        logger.debug(f"Pangolin API config at time of instantiation: {config}")

        # Fallback to environment variables if no config provided
        if config is None:
            config = {
                "PANGOLIN_API_URL": os.getenv("PANGOLIN_API_URL", ""),
                "PANGOLIN_API_KEY": os.getenv("PANGOLIN_API_KEY", ""),
                "PANGOLIN_ORG_ID": os.getenv("PANGOLIN_ORG_ID", ""),
            }
        logger.debug(f"Pangolin API config after instantiation: {config}")

        self.base_url = config.get("PANGOLIN_API_URL", "")
        self.api_key = config.get("PANGOLIN_API_KEY", "")
        self.org_id = config.get("PANGOLIN_ORG_ID", "")

        # Validate required configuration
        if not self.api_key:
            logger.warning("Pangolin API key not configured")
        if not self.org_id:
            logger.warning("Pangolin organization ID not configured")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "PG-IP-Whitelister/1.0",
        }

        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request to Pangolin API with error handling.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests

        Returns:
            Dict containing API response

        Raises:
            PangolinAPIError: If API request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = None

        try:
            response = self.session.request(method, url, timeout=10, **kwargs)
            response.raise_for_status()

            result = response.json()
            return result

        except requests.exceptions.RequestException as e:
            status_code = e.response.status_code if e.response is not None else None
            logger.error(f"API request failed with status {status_code}: {e}")
            raise PangolinAPIError(f"API request failed: {e}", status_code=status_code)
        except ValueError as e:
            logger.error(f"Invalid JSON response: {e}")
            if response:
                logger.error(f"Response content: {response.text}")
            else:
                logger.error("No response object available")
            raise PangolinAPIError(f"Invalid JSON response: {e}", status_code=500)

    def get_resources(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get list of resources from Pangolin API.

        Returns:
            List of resource dictionaries or None if failed
        """
        try:
            result = self._make_request("GET", f"org/{self.org_id}/resources")

            if result.get("success", False) and "data" in result:
                resources = result["data"].get("resources", [])
                logger.info(f"Retrieved {len(resources)} resources")
                return resources
            else:
                logger.error(f"API returned unsuccessful response: {result}")
                return None

        except PangolinAPIError as e:
            logger.error(f"Failed to fetch resources: {e}")
            return None

    def get_resource_rules(self, resource_id: int) -> Optional[List[Dict[str, Any]]]:
        """
        Get rules for a specific resource.

        Args:
            resource_id: ID of the resource

        Returns:
            List of rule dictionaries or None if failed
        """
        try:
            if not isinstance(resource_id, int) or resource_id <= 0:
                raise ValueError(f"Invalid resource ID: {resource_id}")

            result = self._make_request("GET", f"resource/{resource_id}/rules")

            if result.get("success", False) and "data" in result:
                rules = result["data"].get("rules", [])
                logger.info(f"Retrieved {len(rules)} rules for resource {resource_id}")
                return rules
            else:
                logger.error(
                    f"API returned unsuccessful response for resource {resource_id}: {result}"
                )
                return None

        except (PangolinAPIError, ValueError) as e:
            logger.error(f"Failed to fetch rules for resource {resource_id}: {e}")
            return None

    def check_ip_whitelisted(self, resource_id: int, ip: str) -> bool:
        """
        Check if the given IP is already whitelisted for the resource.

        Args:
            resource_id: ID of the resource
            ip: IP address to check

        Returns:
            True if IP is whitelisted, False otherwise
        """
        try:
            if not validate_ip_address(ip):
                logger.warning(f"Invalid IP address provided: {ip}")
                return False

            rules = self.get_resource_rules(resource_id)
            if rules is None:
                return False

            for rule in rules:
                if (
                    rule.get("match") == "IP"
                    and rule.get("action") == "ACCEPT"
                    and rule.get("value") == ip
                    and rule.get("enabled", True)
                ):
                    logger.info(
                        f"IP {ip} is already whitelisted for resource {resource_id}"
                    )
                    return True

            logger.info(f"IP {ip} is not whitelisted for resource {resource_id}")
            return False

        except Exception as e:
            logger.error(
                f"Error checking whitelist status for IP {ip} on resource {resource_id}: {e}"
            )
            return False

    def get_next_priority(self, resource_id: int) -> int:
        """
        Calculate the next available priority number for a resource.

        Args:
            resource_id: ID of the resource

        Returns:
            Next available priority number
        """
        try:
            rules = self.get_resource_rules(resource_id)
            if not rules:
                return 1  # Start with priority 1 if no rules exist

            # Find the highest priority and add 1
            highest_priority = max(
                (rule.get("priority", 0) for rule in rules), default=0
            )
            next_priority = highest_priority + 1

            logger.debug(f"Next priority for resource {resource_id}: {next_priority}")
            return next_priority

        except Exception as e:
            logger.error(
                f"Error calculating next priority for resource {resource_id}: {e}"
            )
            return 1  # Fallback to priority 1

    def delete_rule(self, resource_id: int, rule_id: int) -> Dict[str, Any]:
        """
        Delete a specific rule from a resource.

        Args:
            resource_id: ID of the resource
            rule_id: ID of the rule to delete

        Returns:
            Dictionary containing operation result
        """
        try:
            # Input validation
            if not isinstance(resource_id, int) or resource_id <= 0:
                return {
                    "success": False,
                    "message": "Invalid resource ID",
                    "error": "INVALID_RESOURCE_ID",
                }

            if not isinstance(rule_id, int) or rule_id <= 0:
                return {
                    "success": False,
                    "message": "Invalid rule ID",
                    "error": "INVALID_RULE_ID",
                }

            logger.info(f"Deleting rule {rule_id} from resource {resource_id}")

            result = self._make_request(
                "DELETE", f"resource/{resource_id}/rule/{rule_id}"
            )

            if result.get("success", False):
                logger.info(
                    f"Successfully deleted rule {rule_id} from resource {resource_id}"
                )
                return {
                    "success": True,
                    "message": "Rule successfully deleted",
                }
            else:
                error_msg = result.get("message", "Failed to delete rule")
                logger.error(
                    f"Failed to delete rule {rule_id} from resource {resource_id}: {error_msg}"
                )
                return {
                    "success": False,
                    "message": error_msg,
                    "error": result.get("error", "API_ERROR"),
                }

        except PangolinAPIError as e:
            if e.status_code == 404:
                logger.warning(
                    f"Rule {rule_id} not found for resource {resource_id} during deletion. Assuming already deleted."
                )
                return {"success": True, "message": "Rule not found, assumed deleted"}

            logger.error(
                f"API error deleting rule {rule_id} from resource {resource_id}: {e}"
            )
            return {
                "success": False,
                "message": f"Failed to delete rule: {str(e)}",
                "error": "API_ERROR",
            }
        except Exception as e:
            logger.error(
                f"Unexpected error deleting rule {rule_id} from resource {resource_id}: {e}"
            )
            return {
                "success": False,
                "message": f"Failed to delete rule: {str(e)}",
                "error": "UNEXPECTED_ERROR",
            }

    def delete_all_ip_rules(self, resource_id: int) -> Dict[str, Any]:
        """
        Delete all IP whitelist rules from a resource.

        Args:
            resource_id: ID of the resource

        Returns:
            Dictionary containing operation result
        """
        try:
            # Input validation
            if not isinstance(resource_id, int) or resource_id <= 0:
                return {
                    "success": False,
                    "message": "Invalid resource ID",
                    "error": "INVALID_RESOURCE_ID",
                }

            # Get all rules for the resource
            rules = self.get_resource_rules(resource_id)
            if rules is None:
                return {
                    "success": False,
                    "message": "Failed to fetch resource rules",
                    "error": "FETCH_RULES_ERROR",
                }

            # Filter for IP whitelist rules
            ip_rules = [
                rule
                for rule in rules
                if rule.get("match") == "IP" and rule.get("action") == "ACCEPT"
            ]

            if not ip_rules:
                logger.info(f"No IP whitelist rules found for resource {resource_id}")
                return {
                    "success": True,
                    "message": "No IP whitelist rules to delete",
                    "deleted_count": 0,
                }

            logger.info(
                f"Deleting {len(ip_rules)} IP whitelist rules from resource {resource_id}"
            )

            # Delete each IP rule
            deleted_count = 0
            failed_deletes = []

            for rule in ip_rules:
                rule_id = rule.get("id") or rule.get("ruleId")
                if not rule_id:
                    logger.warning(f"Rule missing ID, skipping: {rule}")
                    continue

                delete_result = self.delete_rule(resource_id, rule_id)
                if delete_result.get("success"):
                    deleted_count += 1
                else:
                    failed_deletes.append(
                        {
                            "rule_id": rule_id,
                            "ip": rule.get("value"),
                            "error": delete_result.get("message"),
                        }
                    )

            if failed_deletes:
                logger.warning(
                    f"Failed to delete {len(failed_deletes)} rules from resource {resource_id}"
                )
                return {
                    "success": False,
                    "message": f"Deleted {deleted_count} rules, failed to delete {len(failed_deletes)} rules",
                    "deleted_count": deleted_count,
                    "failed_deletes": failed_deletes,
                }
            else:
                logger.info(
                    f"Successfully deleted all {deleted_count} IP whitelist rules from resource {resource_id}"
                )
                return {
                    "success": True,
                    "message": f"Successfully deleted {deleted_count} IP whitelist rules",
                    "deleted_count": deleted_count,
                }

        except Exception as e:
            logger.error(
                f"Unexpected error deleting all IP rules from resource {resource_id}: {e}"
            )
            return {
                "success": False,
                "message": f"Failed to delete IP rules: {str(e)}",
                "error": "UNEXPECTED_ERROR",
            }

    def replace_ip_whitelist(self, resource_id: int, ip: str) -> Dict[str, Any]:
        """
        Replace all IP whitelist rules with a single IP.

        Args:
            resource_id: ID of the resource
            ip: IP address to whitelist

        Returns:
            Dictionary containing operation result
        """
        try:
            # Input validation
            if not validate_ip_address(ip):
                return {
                    "success": False,
                    "message": "Invalid IP address format",
                    "error": "INVALID_IP",
                }

            if not isinstance(resource_id, int) or resource_id <= 0:
                return {
                    "success": False,
                    "message": "Invalid resource ID",
                    "error": "INVALID_RESOURCE_ID",
                }

            logger.info(
                f"Replacing all IP whitelist rules for resource {resource_id} with {ip}"
            )

            # Step 1: Delete all existing IP rules
            delete_result = self.delete_all_ip_rules(resource_id)
            if not delete_result.get("success"):
                logger.error(
                    f"Failed to delete existing IP rules for resource {resource_id}: {delete_result.get('message')}"
                )
                return {
                    "success": False,
                    "message": f"Failed to clear existing IP rules: {delete_result.get('message')}",
                    "error": "DELETE_FAILED",
                }

            # Step 2: Add the new IP
            add_result = self.add_ip_to_whitelist(resource_id, ip)
            if not add_result.get("success"):
                logger.error(
                    f"Failed to add new IP {ip} for resource {resource_id}: {add_result.get('message')}"
                )
                return {
                    "success": False,
                    "message": f"Cleared existing rules but failed to add new IP: {add_result.get('message')}",
                    "error": "ADD_FAILED",
                    "deleted_count": delete_result.get("deleted_count", 0),
                }

            logger.info(
                f"Successfully replaced IP whitelist for resource {resource_id} with {ip}"
            )
            return {
                "success": True,
                "message": f"Successfully replaced all IP rules with {ip}",
                "deleted_count": delete_result.get("deleted_count", 0),
                "new_rule": add_result.get("rule", {}),
            }

        except Exception as e:
            logger.error(
                f"Unexpected error replacing IP whitelist for resource {resource_id}: {e}"
            )
            return {
                "success": False,
                "message": f"Failed to replace IP whitelist: {str(e)}",
                "error": "UNEXPECTED_ERROR",
            }

    def add_ip_to_whitelist(self, resource_id: int, ip: str) -> Dict[str, Any]:
        """
        Add an IP address to the whitelist for a specific resource.

        Args:
            resource_id: ID of the resource
            ip: IP address to whitelist

        Returns:
            Dictionary containing operation result
        """
        try:
            # Input validation
            if not validate_ip_address(ip):
                return {
                    "success": False,
                    "message": "Invalid IP address format",
                    "error": "INVALID_IP",
                }

            if not isinstance(resource_id, int) or resource_id <= 0:
                return {
                    "success": False,
                    "message": "Invalid resource ID",
                    "error": "INVALID_RESOURCE_ID",
                }

            # Check if IP is already whitelisted
            if self.check_ip_whitelisted(resource_id, ip):
                return {
                    "success": True,
                    "message": "IP is already whitelisted",
                    "alreadyExists": True,
                }

            # Get next priority
            priority = self.get_next_priority(resource_id)

            # Prepare the rule payload
            rule_data = {
                "action": "ACCEPT",
                "match": "IP",
                "value": ip,
                "priority": priority,
                "enabled": True,
            }

            logger.info(
                f"Adding IP {ip} to whitelist for resource {resource_id} with priority {priority}"
            )

            result = self._make_request(
                "PUT", f"resource/{resource_id}/rule", json=rule_data
            )

            if result.get("success", False):
                logger.info(
                    f"Successfully whitelisted IP {ip} for resource {resource_id}"
                )
                return {
                    "success": True,
                    "message": "IP successfully whitelisted",
                    "rule": result.get("data", {}),
                }
            else:
                error_msg = result.get("message", "Failed to whitelist IP")
                logger.error(
                    f"Failed to whitelist IP {ip} for resource {resource_id}: {error_msg}"
                )
                return {
                    "success": False,
                    "message": error_msg,
                    "error": result.get("error", "API_ERROR"),
                }

        except PangolinAPIError as e:
            logger.error(
                f"API error adding IP {ip} to whitelist for resource {resource_id}: {e}"
            )
            return {
                "success": False,
                "message": f"Failed to whitelist IP: {str(e)}",
                "error": "API_ERROR",
            }
        except Exception as e:
            logger.error(
                f"Unexpected error adding IP {ip} to whitelist for resource {resource_id}: {e}"
            )
            return {
                "success": False,
                "message": f"Failed to whitelist IP: {str(e)}",
                "error": "UNEXPECTED_ERROR",
            }
