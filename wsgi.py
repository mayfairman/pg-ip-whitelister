#!/usr/bin/env python3
"""
WSGI entry point for the PG IP Whitelister application.
"""

from app import create_app

# Create the Flask application
app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000) 