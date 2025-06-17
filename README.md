# IP Whitelister for Pangolin

A self-service web application that allows authenticated users to whitelist their IP addresses for direct access to Pangolin-protected services.

## Features

- 🔐 **Secure Authentication**: Integrates with Pangolin's SSO authentication
- 🌐 **IP Detection**: Automatically detects user's direct IP address
- 📋 **Resource Management**: Lists available resources from Pangolin API
- ✅ **Whitelist Status**: Shows which resources already have user's IP whitelisted
- 🎯 **Bulk Operations**: Select multiple resources for whitelisting
- 📊 **Real-time Feedback**: Immediate status updates and error handling

## Architecture

- **Backend**: Flask web application with RESTful API
- **Frontend**: Single-page application using Alpine.js and Tailwind CSS
- **Integration**: Direct integration with Pangolin API
- **Deployment**: Containerized for easy deployment alongside Pangolin

## Quick Start

### Prerequisites

- Python 3.11+
- Pangolin API access
- Environment variables configured

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pg_ip_whitelister_v3
   ```

2. **Install dependencies**
   ```bash
   pip install -e .
   ```

3. **Configure environment variables**
   ```bash
   export PANGOLIN_API_URL="local-address-of-pangolin-server:3001"
   export PANGOLIN_API_KEY="your-api-key"
   export PANGOLIN_ORG_ID="your-org-id"
   export SECRET_KEY="your-secret-key"
   export FLASK_ENV="development"
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5000`

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PANGOLIN_API_URL` | Pangolin API base URL | `local-address-of-pangolin-server:3001` |
| `PANGOLIN_API_KEY` | Pangolin API authentication key | Required |
| `PANGOLIN_ORG_ID` | Pangolin organization ID | Required |
| `SECRET_KEY` | Flask secret key for sessions | `dev-secret-key-change-in-production` |
| `FLASK_ENV` | Flask environment | `production` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Production Deployment

For production deployment, use Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## API Endpoints

### Frontend Routes
- `GET /` - Main application interface

### API Routes
- `GET /api/client-ip` - Get client's IP address
- `GET /api/resources` - Get available resources
- `GET /api/resource/<id>/rules` - Get rules for a resource
- `POST /api/check-whitelist` - Check if IP is whitelisted
- `POST /api/whitelist` - Add IP to whitelist

## Development

### Setup Development Environment

```bash
pip install -e ".[dev]"
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

### Testing

```bash
pytest
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

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Verify `PANGOLIN_API_URL` is correct
   - Check `PANGOLIN_API_KEY` is valid
   - Ensure network connectivity

2. **IP Detection Issues**
   - Application must be behind proper proxy configuration
   - Check `request.remote_addr` is being set correctly

3. **Resource Loading Failures**
   - Verify `PANGOLIN_ORG_ID` is correct
   - Check API permissions for resource access

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license information here]
