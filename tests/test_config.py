import os
import tempfile
import pytest
from agentic_layer.config import Config, DEFAULT_CONFIG


class TestConfig:
    """Tests for the Config class"""

    def test_default_config(self):
        """Test that default config is loaded correctly"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(tmpdir)
            assert config.get_model() == DEFAULT_CONFIG["model"]
            assert config.get_temperature() == DEFAULT_CONFIG["temperature"]
            assert config.get_max_tokens() == DEFAULT_CONFIG["max_tokens"]

    def test_config_get_set(self):
        """Test getting and setting config values"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(tmpdir)

            # Test get
            assert config.get("model") == "gpt-4.1-mini"

            # Test set
            config.set("model", "gpt-4")
            assert config.get("model") == "gpt-4"

            # Test nested get
            assert config.get("logging.enabled") is True

            # Test nested set
            config.set("logging.enabled", False)
            assert config.get("logging.enabled") is False

    def test_config_save_load(self):
        """Test saving and loading config"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and modify config
            config1 = Config(tmpdir)
            config1.set("model", "custom-model")
            config1.save()

            # Load config in new instance
            config2 = Config(tmpdir)
            assert config2.get("model") == "custom-model"

    def test_config_prompts(self):
        """Test getting prompts"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(tmpdir)
            assert config.get_prompt("specify") is not None
            assert config.get_prompt("plan") is not None
            assert config.get_prompt("tasks") is not None

    def test_config_booleans(self):
        """Test boolean config methods"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(tmpdir)
            assert config.should_confirm() is True
            assert config.should_auto_commit() is False
            assert config.is_logging_enabled() is True
            assert config.should_save_history() is True
