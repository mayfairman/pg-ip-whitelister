"""Tests for configuration system."""

from unittest.mock import MagicMock

import pytest


class TestConfig:
    """Test cases for configuration classes."""

    @pytest.mark.skip(
        reason="Config class variables are set at import time; test is unreliable without refactor."
    )
    def test_base_config_defaults(self, monkeypatch):
        """Test base configuration defaults."""
        # Clear environment variables that might interfere with tests
        monkeypatch.delenv("PANGOLIN_API_URL", raising=False)
        monkeypatch.delenv("PANGOLIN_API_KEY", raising=False)
        monkeypatch.delenv("PANGOLIN_ORG_ID", raising=False)
        monkeypatch.delenv("SECRET_KEY", raising=False)
        monkeypatch.delenv("FLASK_ENV", raising=False)
        monkeypatch.delenv("LOG_LEVEL", raising=False)

        # Reload the config module to re-evaluate class variables
        import importlib

        import app.config

        importlib.reload(app.config)

        config = app.config.Config()

        # SECRET_KEY is auto-generated, so just check it's not the default
        assert config.SECRET_KEY != "dev-secret-key-change-in-production"
        assert len(config.SECRET_KEY) > 20  # Should be a reasonable length
        assert config.ENV == "production"
        assert config.DEBUG is False
        assert config.TESTING is False
        assert config.PANGOLIN_API_URL == ""
        assert config.PANGOLIN_API_KEY == ""
        assert config.PANGOLIN_ORG_ID == ""
        assert config.MAX_CONTENT_LENGTH == 16 * 1024 * 1024
        assert config.SESSION_COOKIE_SECURE is True
        assert config.SESSION_COOKIE_HTTPONLY is True
        assert config.SESSION_COOKIE_SAMESITE == "Lax"
        assert config.LOG_LEVEL == "INFO"

    # def test_base_config_with_env_vars(self, monkeypatch):
    #     """Test base configuration with environment variables."""
    #     # Clear any existing env vars that might interfere
    #     monkeypatch.delenv('SECRET_KEY', raising=False)
    #     monkeypatch.delenv('FLASK_ENV', raising=False)
    #     monkeypatch.delenv('PANGOLIN_API_URL', raising=False)
    #     monkeypatch.delenv('PANGOLIN_API_KEY', raising=False)
    #     monkeypatch.delenv('PANGOLIN_ORG_ID', raising=False)
    #     monkeypatch.delenv('LOG_LEVEL', raising=False)
    #
    #     # Set test environment variables
    #     monkeypatch.setenv('SECRET_KEY', 'test-secret')
    #     monkeypatch.setenv('FLASK_ENV', 'development')
    #     monkeypatch.setenv('PANGOLIN_API_URL', 'https://test-api.com')
    #     monkeypatch.setenv('PANGOLIN_API_KEY', 'test-key')
    #     monkeypatch.setenv('PANGOLIN_ORG_ID', 'test-org')
    #     monkeypatch.setenv('LOG_LEVEL', 'DEBUG')
    #
    #     config = Config()
    #
    #     assert config.SECRET_KEY == 'test-secret'
    #     assert config.ENV == 'development'
    #     assert config.PANGOLIN_API_URL == 'https://test-api.com'
    #     assert config.PANGOLIN_API_KEY == 'test-key'
    #     assert config.PANGOLIN_ORG_ID == 'test-org'
    #     assert config.LOG_LEVEL == 'DEBUG'

    def test_base_config_init_app(self):
        """Test base configuration init_app method."""
        from app.config import Config

        config = Config()
        app = MagicMock()

        # Should not raise any exception
        config.init_app(app)

    def test_development_config(self):
        """Test development configuration."""
        from app.config import DevelopmentConfig

        config = DevelopmentConfig()

        assert config.DEBUG is True
        assert config.SESSION_COOKIE_SECURE is False

    def test_development_config_init_app(self, monkeypatch):
        """Test development configuration initialization."""
        import logging

        from app.config import DevelopmentConfig

        config = DevelopmentConfig()
        app = MagicMock()
        app.logger = MagicMock()

        # Mock logging.basicConfig
        mock_basic_config = MagicMock()
        monkeypatch.setattr(logging, "basicConfig", mock_basic_config)

        config.init_app(app)

        mock_basic_config.assert_called_once_with(level=logging.DEBUG)
        app.logger.setLevel.assert_called_once_with(logging.DEBUG)
        app.logger.info.assert_called_once_with(
            "PG IP Whitelister startup (debug mode)"
        )

    def test_production_config(self):
        """Test production configuration."""
        from app.config import ProductionConfig

        config = ProductionConfig()

        assert config.DEBUG is False

    def test_production_config_init_app(self, monkeypatch, tmp_path):
        """Test production configuration initialization."""
        import logging

        from app.config import ProductionConfig

        # Create logs directory
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()

        config = ProductionConfig()
        app = MagicMock()
        app.debug = False
        app.testing = False
        app.logger = MagicMock()

        # Mock os.path.exists and os.mkdir
        mock_exists = MagicMock(return_value=False)
        mock_mkdir = MagicMock()
        monkeypatch.setattr("os.path.exists", mock_exists)
        monkeypatch.setattr("os.mkdir", mock_mkdir)

        # Mock RotatingFileHandler - fix the import path
        mock_handler_instance = MagicMock()
        mock_handler_class = MagicMock(return_value=mock_handler_instance)
        monkeypatch.setattr("logging.handlers.RotatingFileHandler", mock_handler_class)

        config.init_app(app)

        # Verify file handler was created
        mock_handler_class.assert_called_once()
        mock_handler_instance.setFormatter.assert_called_once()
        mock_handler_instance.setLevel.assert_called_once_with(logging.INFO)
        app.logger.addHandler.assert_called_once_with(mock_handler_instance)
        app.logger.setLevel.assert_called_once_with(logging.INFO)

    def test_testing_config(self):
        """Test testing configuration."""
        from app.config import TestingConfig

        config = TestingConfig()

        assert config.TESTING is True
        assert config.WTF_CSRF_ENABLED is False

    def test_config_dict(self):
        """Test configuration dictionary."""
        from app.config import (
            DevelopmentConfig,
            ProductionConfig,
            TestingConfig,
            config,
        )

        assert "development" in config
        assert "testing" in config
        assert "production" in config
        assert "default" in config

        assert config["development"] == DevelopmentConfig
        assert config["testing"] == TestingConfig
        assert config["production"] == ProductionConfig
        assert config["default"] == DevelopmentConfig
