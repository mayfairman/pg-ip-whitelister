import os

from flask import Flask, jsonify
from flask_cors import CORS


def create_app(config=None):
    """Application factory pattern with proper configuration management."""
    app = Flask(__name__)

    # Configuration
    from app.config import config as config_dict

    env = os.getenv("FLASK_ENV", "production")

    app.config.from_object(config_dict[env])
    app.config.from_object(config_dict["default"])

    if config:
        # Handle both config objects and dictionaries
        if hasattr(config, "__dict__"):
            # Config object - use from_object
            app.config.from_object(config)
        else:
            # Dictionary - use update
            app.config.update(config)

    # Environment-specific overrides
    if app.config["ENV"] == "development":
        app.config["DEBUG"] = True

    # Initialize extensions
    CORS(app)  # Enable CORS for API endpoints

    # Initialize configuration
    config_dict[env].init_app(app)

    # Register blueprints
    from app.routes import main

    app.register_blueprint(main)

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Server Error: {error}")
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"Unhandled exception: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

    return app
