import pytest
from plugins.regex_pii_masker import PIMaskerPlugin
from plugins.credential_leak_detector import CredentialLeakDetectorPlugin
from plugins.rate_limiter import RateLimiterPlugin

def test_pii_masker_redacts_sensitive_data():
    plugin = PIMaskerPlugin()
    input_text = "Contact me at dev@test.com or via card 4111222233334444."
    result = plugin.inspect(input_text)
    
    assert result["safe"] is True
    assert "[REDACTED_EMAIL]" in result["prompt"]
    assert "[REDACTED_CARD]" in result["prompt"]
    assert "dev@test.com" not in result["prompt"]

def test_credential_leak_detector_blocks_keys():
    plugin = CredentialLeakDetectorPlugin()
    malicious_prompt = "Here is my master key: sk-proj-1234567890abcdef1234567890abcdef12345678"
    result = plugin.inspect(malicious_prompt)
    
    assert result["safe"] is False
    assert "Security Violation" in result["reason"]

def test_rate_limiter_blocks_spikes():
    # Set threshold low to test the break limits quickly
    plugin = RateLimiterPlugin(max_requests=2, window_seconds=10)
    
    # Request 1 & 2 pass smoothly
    assert plugin.inspect("Prompt 1")["safe"] is True
    assert plugin.inspect("Prompt 2")["safe"] is True
    
    # Request 3 should trigger a drop block instantly
    result = plugin.inspect("Prompt 3")
    assert result["safe"] is False
    assert "Rate Limit Exceeded" in result["reason"]