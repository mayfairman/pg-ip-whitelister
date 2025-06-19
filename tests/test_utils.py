"""Tests for utility functions."""

from app.utils import validate_ip_address


class TestUtils:
    """Test cases for utility functions."""

    def test_validate_ip_address_valid_ipv4(self):
        """Test valid IPv4 addresses."""
        valid_ips = [
            "192.168.1.1",
            "10.0.0.1",
            "172.16.0.1",
            "127.0.0.1",
            "0.0.0.0",
            "255.255.255.255",
        ]

        for ip in valid_ips:
            assert validate_ip_address(ip) is True, f"IP {ip} should be valid"

    def test_validate_ip_address_valid_ipv6(self):
        """Test valid IPv6 addresses."""
        valid_ips = ["::1", "2001:db8::1", "fe80::1", "::ffff:192.168.1.1"]

        for ip in valid_ips:
            assert validate_ip_address(ip) is True, f"IP {ip} should be valid"

    def test_validate_ip_address_invalid(self):
        """Test invalid IP addresses."""
        invalid_ips = [
            "invalid-ip",
            "192.168.1.256",  # Invalid octet
            "192.168.1",  # Incomplete
            "192.168.1.1.1",  # Too many octets
            "192.168.1.1.1.1",  # Too many octets
            "192.168.1.1.",  # Trailing dot
            ".192.168.1.1",  # Leading dot
            "192..168.1.1",  # Double dot
            "192.168.1.1a",  # Non-numeric character
            "192.168.1.1 ",  # Trailing space
            " 192.168.1.1",  # Leading space
            "",  # Empty string
            None,  # None value
            123,  # Integer
            "localhost",  # Hostname
            "example.com",  # Domain name
        ]

        for ip in invalid_ips:
            assert validate_ip_address(ip) is False, f"IP {ip} should be invalid"

    def test_validate_ip_address_edge_cases(self):
        """Test edge cases for IP validation."""
        # Private IP ranges
        private_ips = ["10.0.0.1", "172.16.0.1", "192.168.1.1"]

        for ip in private_ips:
            assert validate_ip_address(ip) is True, f"Private IP {ip} should be valid"

        # Loopback addresses
        loopback_ips = ["127.0.0.1", "127.0.0.0", "127.255.255.255"]

        for ip in loopback_ips:
            assert validate_ip_address(ip) is True, f"Loopback IP {ip} should be valid"

        # Broadcast addresses
        broadcast_ips = ["255.255.255.255", "192.168.1.255"]

        for ip in broadcast_ips:
            assert validate_ip_address(ip) is True, f"Broadcast IP {ip} should be valid"

    def test_validate_ip_address_boundary_values(self):
        """Test boundary values for IP validation."""
        # Valid boundary values
        assert validate_ip_address("0.0.0.0") is True
        assert validate_ip_address("255.255.255.255") is True

        # Invalid boundary values
        assert validate_ip_address("0.0.0.256") is False
        assert validate_ip_address("256.0.0.0") is False
        assert validate_ip_address("-1.0.0.0") is False
