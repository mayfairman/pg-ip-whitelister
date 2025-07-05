# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-01-05

### Added
- **IP Management Feature**: Complete management interface for whitelisted IP addresses
  - "Manage IPs" button on each resource card for easy access
  - Modal interface showing all currently whitelisted IPs for a resource
  - Individual IP removal with confirmation dialogs
  - Bulk operations: "Remove All" and "Replace with Current IP" 
  - Real-time status updates after IP changes
  - Current IP highlighting with green "Current" badge
  - Loading states and comprehensive error handling

### Backend
- **New API Endpoints**:
  - `DELETE /api/resource/{id}/rule/{rule_id}` - Remove specific IP rule
  - `DELETE /api/resource/{id}/ip-rules` - Remove all IP whitelist rules
  - `PUT /api/resource/{id}/replace-ip-whitelist` - Replace all rules with current IP
- **New PangolinAPI Methods**:
  - `delete_rule()` - Delete individual rules
  - `delete_all_ip_rules()` - Bulk delete IP rules
  - `replace_ip_whitelist()` - Atomic replace operation

### Frontend  
- Full-featured IP management modal using Alpine.js and Tailwind CSS
- Responsive design with dark mode support
- Real-time feedback and visual state management
- Confirmation dialogs for destructive operations

### Testing
- Comprehensive test suite with 19 new tests
- Full coverage of new API endpoints and edge cases
- Input validation and error handling tests

### Fixed
- Alpine.js template processing errors with inconsistent rule ID properties
- Null safety checks for whitelistedIPs array handling
- Enhanced debugging output for rule structure tracking

## [1.0.0] - 2024-12-01

### Added
- Initial release of PG IP Whitelister v3
- Self-service IP whitelisting for Pangolin-protected resources
- Automatic IP detection using external services
- Resource listing and status checking
- Bulk IP whitelisting operations
- Modern web interface with Alpine.js and Tailwind CSS
- Flask backend with RESTful API
- Direct Pangolin API integration
- Comprehensive test suite
- Docker containerization
- Pre-commit hooks for code quality

### Security
- Secure session management
- Input validation and sanitization
- Error handling without information disclosure
- CORS configuration for API endpoints
