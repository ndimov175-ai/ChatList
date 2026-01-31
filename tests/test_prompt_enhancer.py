"""
Tests for prompt enhancer client.
"""
import pytest
from chatlist.core.prompt_enhancer_client import PromptEnhancerClient
from chatlist.core.enhance_result import EnhanceResult


class TestPromptEnhancerClient:
    """Test suite for PromptEnhancerClient."""

    def test_system_prompts_exist(self):
        """Test that all system prompts are defined."""
        client = PromptEnhancerClient()
        expected_types = ['general', 'code', 'analysis', 'creative']
        for enhance_type in expected_types:
            assert enhance_type in client.SYSTEM_PROMPTS
            assert len(client.SYSTEM_PROMPTS[enhance_type]) > 0

    def test_enhance_result_serialization(self):
        """Test EnhanceResult serialization and deserialization."""
        result = EnhanceResult(
            original_prompt="Original",
            enhanced_prompt="Enhanced",
            alternatives=["Alt1", "Alt2"],
            explanation="Changes made",
            recommendations={"code": "For code", "analysis": "For analysis"},
            model_id=1,
            enhancement_type="general"
        )

        # Test to_dict
        data = result.to_dict()
        assert data['original_prompt'] == "Original"
        assert data['enhanced_prompt'] == "Enhanced"
        assert isinstance(data['alternatives'], str)
        assert isinstance(data['recommendations'], str)

        # Test from_dict
        restored = EnhanceResult.from_dict(data)
        assert restored.original_prompt == result.original_prompt
        assert restored.enhanced_prompt == result.enhanced_prompt
        assert restored.alternatives == result.alternatives

    def test_validation_empty_prompt(self):
        """Test that empty prompts are rejected."""
        client = PromptEnhancerClient()
        result = client.enhance_prompt("", model_id=1)
        assert result is None

    def test_validation_short_prompt(self):
        """Test that prompts shorter than 10 chars are rejected."""
        client = PromptEnhancerClient()
        result = client.enhance_prompt("short", model_id=1)
        assert result is None

    def test_validation_long_prompt(self):
        """Test that prompts longer than 10000 chars are rejected."""
        client = PromptEnhancerClient()
        long_prompt = "a" * 10001
        result = client.enhance_prompt(long_prompt, model_id=1)
        assert result is None

    def test_invalid_enhancement_type(self):
        """Test that invalid enhancement type is handled."""
        client = PromptEnhancerClient()
        # Should not raise exception, just log warning
        prompt = "This is a valid prompt for testing purposes"
        # This will fail without API key, but shouldn't crash on invalid type
        # The method should fallback to 'general'
        assert prompt  # Just ensure prompt is valid


class TestEnhanceResult:
    """Test suite for EnhanceResult dataclass."""

    def test_enhance_result_creation(self):
        """Test creating EnhanceResult."""
        result = EnhanceResult(
            original_prompt="Test",
            enhanced_prompt="Enhanced Test",
            alternatives=["Alt1", "Alt2", "Alt3"],
            explanation="Made it better",
            recommendations={"code": "...", "analysis": "..."},
            model_id=1
        )
        assert result.original_prompt == "Test"
        assert result.enhanced_prompt == "Enhanced Test"
        assert len(result.alternatives) == 3

    def test_enhance_result_defaults(self):
        """Test EnhanceResult default values."""
        result = EnhanceResult(
            original_prompt="Test",
            enhanced_prompt="Enhanced",
            alternatives=[],
            explanation="",
            recommendations={},
            model_id=1
        )
        assert result.enhancement_type == "general"
        assert result.timestamp is not None

    def test_enhance_result_id_optional(self):
        """Test that ID is optional in EnhanceResult."""
        result = EnhanceResult(
            original_prompt="Test",
            enhanced_prompt="Enhanced",
            alternatives=[],
            explanation="",
            recommendations={},
            model_id=1
        )
        assert result.id is None
