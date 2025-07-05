# IP Whitelister for Pangolin

A self-service web application that allows authenticated users to whitelist their IP addresses for direct access to Pangolin-protected services.

## Features

- 🔐 **Secure Authentication**: Integrates with Pangolin's SSO authentication
- 🌐 **IP Detection**: Automatically detects user's direct IP address
- 📋 **Resource Management**: Lists available resources from Pangolin API
- ✅ **Whitelist Status**: Shows which resources already have user's current IP whitelisted
- 🎯 **Bulk Operations**: Select multiple resources for whitelisting
- 📊 **Real-time Feedback**: Immediate status updates and error handling

## Architecture

- **Backend**: Flask web application with RESTful API
- **Frontend**: Single-page application using Alpine.js and Tailwind CSS
- **Integration**: Direct integration with Pangolin API
- **Deployment**: Containerized for easy deployment alongside Pangolin
- **Security**: The Pangolin Integration API should **not** be exposed to the public internet. It only needs to be accessible locally (e.g., via `pangolin` docker bridge network or the VPS's private network interface). The whitelister app communicates with Pangolin over the local network, ensuring your API credentials and traffic remain secure and internal.

## Quick Start


### 1. Enable the integartion server
As per https://docs.fossorial.io/Pangolin/API/integration-api#enable-integration-api

Update the Pangolin config file (config.yml):
```yaml
  server:
    integration_port: 3003

  flags:
    enable_integration_api: true
```
Do not follow the rest of that guide - as it later exposes to the external web, which you dont need for this.

### 2. Create Pangolin API Key
Pangolin -> Server Admin -> API Keys -> Create a new Key with these minimum permissions:-
* List Resources
* Create Resource Rule
* List Resource Rules
* Update Resource Rule

### 3. Create .env on VPS
```bash
mkdir pg-ip-whitelister
cd pg-ip-whitelister
# Create .env file
cat > .env << EOF
PANGOLIN_API_URL=http://pangolin:3003/v1
PANGOLIN_API_KEY=your_api_key
PANGOLIN_ORG_ID=your_org_id
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
LOG_LEVEL=INFO
EOF
```

###4. Copy docker-compose.yml to your VPS 
assumption that your pangolin is installed via docker and on bridge network 'pangolin'. Alter if not.
```yaml
version: '3.8'

services:
  pg-ip-whitelister:
    container_name: pg-ip-whitelister
    image: pmylward/pg-ip-whitelister:v1.1.0
    ports:
      - "5000:5000"
    environment:
      # Pangolin API Configuration from .env
      - PANGOLIN_API_URL=${PANGOLIN_API_URL}
      - PANGOLIN_API_KEY=${PANGOLIN_API_KEY}
      - PANGOLIN_ORG_ID=${PANGOLIN_ORG_ID}

      # Flask Configuration
      - SECRET_KEY=${SECRET_KEY}
      - FLASK_ENV=${FLASK_ENV:-production}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}

    volumes:
      # Mount logs directory for persistence
      - ./logs:/app/logs

    restart: unless-stopped
    
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/client-ip"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    
    networks:
      - pg-network

networks:
  pg-network:
    name: pangolin 
    external: true
```

### 5. Start the service
```bash
docker-compose up -d
```

### 6. Set up pg-ip-whitelister in pangolin as a local resource, HTTP pointing to hostname to ip.yourdomain.com (or whatever you would like to call it)
```pg-ip-whitelister```
Which is derived from the docker hostname
port
```5000```
And make sure it is behind SSO (Or your chosen auth pattern)

### 7. visit ip.domain.com and see the site, check your IP adress and add it to whitelist

## Development
### Setup Development Environment

```bash
uv sync --dev
```

### Code Quality

```bash
# Format code
uv run black .

# Lint code
uv run flake8 .

# Type checking
uv run mypy .
```

### Testing

```bash
pytest
```
OR
```bash
./run_tests.sh
```

## Security Considerations

- All API endpoints require proper authentication
- IP addresses are validated before processing
- Error messages don't expose sensitive information
- Session cookies are configured securely
- CORS is enabled for API endpoints

## Logging

The application logs to:
- Console (development)
- `logs/pg_ip_whitelister.log` (production)

Log levels can be configured via `LOG_LEVEL` environment variable.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license information here]

## Deployment Notes

- **pg-ip-whitelister** is designed to run on the same VPS as your Pangolin API instance.
- The Pangolin API should **not** be exposed to the public internet. It only needs to be accessible locally (e.g., via `localhost` or the VPS's private network interface).
- The whitelister app communicates with Pangolin over the local network, ensuring your API credentials and traffic remain secure and internal.

**Example Pangolin API URL for local-only access:**
```
PANGOLIN_API_URL=http://localhost:3001
```
or, if using Docker Compose:
```
PANGOLIN_API_URL=http://pangolin:3001
```
(where `pangolin` is the Docker service name)

> **Do not expose your Pangolin API port to the public.**  
> Only the whitelister app's web interface should be accessible externally.

## Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com/) to ensure code quality and security.

### Setup

1. **Install pre-commit in your uv environment:**
   ```bash
   uv add pre-commit
   ```

2. **Install the pre-commit hooks:**
   ```bash
   uv run pre-commit install
   ```

3. **(Optional) Run all hooks on all files:**
   ```bash
   uv run pre-commit run --all-files
   ```

### Hooks Used

- **black**: Code formatter
- **isort**: Import sorter (configured for Black compatibility)
- **flake8**: Linter (line length ignored, handled by Black)
- **bandit**: Security linter (uses `bandit.yaml` config)
- **detect-private-key**: Prevents accidental commits of secrets

Bandit uses a custom configuration file (`bandit.yaml`) in this project. Adjust it as needed for your security policies.
