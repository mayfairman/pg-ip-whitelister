# Deployment Guide

This guide covers how to deploy the PG IP Whitelister using Docker.

## Prerequisites

- Docker installed on your system
- Pangolin API credentials
- Port 5000 available (or change in docker-compose.yml)

## Quick Start

### 1. Environment Configuration

Create a `.env` file in the project root:

```bash
# Pangolin API Configuration
PANGOLIN_API_URL=local-address-of-pangolin-server:3001
PANGOLIN_API_KEY=your-api-key-here
PANGOLIN_ORG_ID=your-org-id-here

# Flask Configuration
SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=production

# Logging
LOG_LEVEL=INFO
```

### 2. Deploy with Script

```bash
# Make script executable (if not already)
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### 3. Deploy with Docker Compose

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### 4. Manual Docker Deployment

```bash
# Build image
docker build -t pg-ip-whitelister .

# Run container
docker run -d \
    --name pg-ip-whitelister \
    --env-file .env \
    -p 5000:5000 \
    -v $(pwd)/logs:/app/logs \
    --restart unless-stopped \
    pg-ip-whitelister
```

**Note**: The application uses a `wsgi.py` file as the WSGI entry point, which is the standard approach for Flask applications in production.

## Production Deployment

### Using Docker Compose (Recommended)

1. **Configure environment variables** in your `.env` file
2. **Build and start**:
   ```bash
   docker-compose up -d --build
   ```
3. **Monitor logs**:
   ```bash
   docker-compose logs -f pg-ip-whitelister
   ```

### Using Docker Swarm

```bash
# Initialize swarm (if not already)
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml pg-whitelister
```

### Using Kubernetes

Create a deployment YAML:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pg-ip-whitelister
spec:
  replicas: 2
  selector:
    matchLabels:
      app: pg-ip-whitelister
  template:
    metadata:
      labels:
        app: pg-ip-whitelister
    spec:
      containers:
      - name: pg-ip-whitelister
        image: pg-ip-whitelister:latest
        ports:
        - containerPort: 5000
        env:
        - name: PANGOLIN_API_URL
          value: "local-address-of-pangolin-server:3001"
        - name: PANGOLIN_API_KEY
          valueFrom:
            secretKeyRef:
              name: pangolin-secrets
              key: api-key
        - name: PANGOLIN_ORG_ID
          valueFrom:
            secretKeyRef:
              name: pangolin-secrets
              key: org-id
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: secret-key
```

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `PANGOLIN_API_URL` | Pangolin API base URL | No | `local-address-of-pangolin-server:3001` |
| `PANGOLIN_API_KEY` | Pangolin API authentication key | **Yes** | - |
| `PANGOLIN_ORG_ID` | Pangolin organization ID | **Yes** | - |
| `SECRET_KEY` | Flask secret key for sessions | **Yes** | - |
| `FLASK_ENV` | Flask environment | No | `production` |
| `LOG_LEVEL` | Logging level | No | `INFO` |

## Security Considerations

1. **Use strong SECRET_KEY** in production
2. **Store sensitive data** in Docker secrets or Kubernetes secrets
3. **Use HTTPS** in production (configure reverse proxy)
4. **Limit container resources** if needed
5. **Regular security updates** for base images

## Monitoring

### Health Checks

The container includes health checks:
```bash
# Check container health
docker ps

# View health check logs
docker inspect pg-ip-whitelister | grep -A 10 Health
```

### Logs

```bash
# View application logs
docker logs pg-ip-whitelister

# Follow logs in real-time
docker logs -f pg-ip-whitelister

# View logs from host
tail -f logs/pg_ip_whitelister.log
```

### Metrics

The application logs to:
- **Container logs**: Application events and errors
- **Host logs**: `./logs/pg_ip_whitelister.log` (mounted volume)

## Troubleshooting

### Container Won't Start

1. **Check environment variables**:
   ```bash
   docker run --rm --env-file .env pg-ip-whitelister
   ```

2. **Check logs**:
   ```bash
   docker logs pg-ip-whitelister
   ```

3. **Verify API connectivity**:
   ```bash
   docker exec pg-ip-whitelister curl -f http://localhost:5000/api/client-ip
   ```

### Application Errors

1. **Check Pangolin API credentials**
2. **Verify network connectivity**
3. **Check application logs**
4. **Restart container** if needed

### Performance Issues

1. **Increase workers** in Dockerfile CMD
2. **Add resource limits** in docker-compose.yml
3. **Use reverse proxy** (nginx/traefik) for SSL termination

## Backup and Recovery

### Data Backup

The application is stateless, but logs are persisted:
```bash
# Backup logs
tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/
```

### Container Backup

```bash
# Save image
docker save pg-ip-whitelister > pg-ip-whitelister-backup.tar

# Load image
docker load < pg-ip-whitelister-backup.tar
```

## Updates

### Rolling Updates

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build

# Or use deployment script
./deploy.sh
```

### Zero-Downtime Deployment

For production, consider:
- Load balancer with multiple instances
- Blue-green deployment
- Rolling updates with health checks 