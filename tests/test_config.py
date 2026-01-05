"""Tests for configuration"""

import pytest
import os
from candidate_evaluator.utils.config import Config, APIConfig, get_default_config


def test_api_config_validation():
    """Test API configuration validation"""

    # Valid config
    config = APIConfig(anthropic_api_key="test-key", temperature=0.5)
    assert config.temperature == 0.5

    # Invalid temperature
    with pytest.raises(ValueError):
        APIConfig(anthropic_api_key="test-key", temperature=1.5)


def test_get_default_config_without_api_key():
    """Test that default config requires API key"""

    # Remove API key if it exists
    original = os.environ.get('ANTHROPIC_API_KEY')
    if 'ANTHROPIC_API_KEY' in os.environ:
        del os.environ['ANTHROPIC_API_KEY']

    try:
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY not found"):
            get_default_config()

    finally:
        # Restore original
        if original:
            os.environ['ANTHROPIC_API_KEY'] = original


def test_config_model():
    """Test full config model"""

    config = Config(
        api=APIConfig(
            anthropic_api_key="test-key",
            model="claude-sonnet-4-5-20250929"
        )
    )

    assert config.api.anthropic_api_key == "test-key"
    assert config.api.model == "claude-sonnet-4-5-20250929"
    assert config.criteria.weights.critical_thinking == 10
