# IP Whitelister for Pangolin

A self-service web application that allows authenticated users to whitelist their IP addresses for direct access to Pangolin-protected services.

The application is designed to be run on the same VPS as your Pangolin instance, and the Pangolin API should not be exposed to the public internet.

## Setup

Follow these steps to get the IP Whitelister running.

### 1. Prepare Pangolin

First, you need to enable the integration API in Pangolin and create an API key.

**Enable Integration API:**

In your Pangolin `config.yml`, add the following:

```yaml
server:
  integration_port: 3003

flags:
  enable_integration_api: true
```

**Create API Key:**

In the Pangolin UI, go to `Server Admin` > `API Keys` and create a new key with the following minimum permissions:

*   `List Resources`
*   `Create Resource Rule`
*   `List Resource Rules`
*   `Update Resource Rule`

### 2. Deploy on VPS with Docker Compose

Next, deploy the whitelister application on your VPS.

**Create `.env` file:**

Create a `.env` file with your Pangolin details. The `SECRET_KEY` is for Flask's session management.

```bash
mkdir -p pg-ip-whitelister
cd pg-ip-whitelister

cat > .env << EOF
PANGOLIN_API_URL=http://pangolin:3003/v1
PANGOLIN_API_KEY=your_pangolin_api_key
PANGOLIN_ORG_ID=your_pangolin_org_id
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
LOG_LEVEL=INFO
EOF
```

**Create `docker-compose.yml` file:**

This assumes your Pangolin container is on a Docker bridge network named `pangolin`.

```yaml
version: '3.8'

services:
  pg-ip-whitelister:
    container_name: pg-ip-whitelister
    image: pmylward/pg-ip-whitelister:v1.1.0
    ports:
      - "5000:5000"
    environment:
      - PANGOLIN_API_URL=${PANGOLIN_API_URL}
      - PANGOLIN_API_KEY=${PANGOLIN_API_KEY}
      - PANGOLIN_ORG_ID=${PANGOLIN_ORG_ID}
      - SECRET_KEY=${SECRET_KEY}
      - FLASK_ENV=${FLASK_ENV:-production}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    volumes:
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

**Start the service:**

```bash
docker-compose up -d
```

### 3. Configure in Pangolin

Finally, add the whitelister application as a new resource in Pangolin so it's accessible to your users.

1.  Go to `Resources` in Pangolin and create a new resource.
2.  Set the `Location` to `http://pg-ip-whitelister:5000`.
3.  Ensure the resource is protected by your desired authentication pattern (e.g., SSO).

Users can now visit the URL for this new resource to whitelist their IP addresses.
