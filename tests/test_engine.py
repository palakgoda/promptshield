import pytest
import os
from plugins.regex_pii_masker import PIMaskerPlugin
from plugins.credential_leak_detector import CredentialLeakDetectorPlugin
from plugins.rate_limiter import RateLimiterPlugin
from src.main import load_security_plugins
from src.database import init_db, log_request, get_recent_logs, get_db_metrics, DB_PATH

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

def test_dynamic_plugin_loader():
    plugins_list = load_security_plugins()
    # Should load RateLimiter, PIMasker, CredentialLeakDetector
    names = [p.name for p in plugins_list]
    assert "Local Rate Limiter" in names
    assert "Regex PII Masker" in names
    assert "Credential Leak Detector" in names
    # Verify RateLimiter is first
    assert names[0] == "Local Rate Limiter"

def test_sqlite_database_logging():
    # Force initialize the DB
    init_db()
    assert os.path.exists(DB_PATH)
    
    # Log a dummy request
    log_request(
        endpoint="/test/completions",
        status_code=403,
        plugin_triggered="Test Shield",
        message="Blocked due to testing"
    )
    
    # Retrieve logs
    logs = get_recent_logs(limit=5)
    assert len(logs) > 0
    latest = logs[0]
    assert latest["endpoint"] == "/test/completions"
    assert latest["status_code"] == 403
    assert latest["plugin_triggered"] == "Test Shield"
    assert latest["message"] == "Blocked due to testing"
    
    # Check metrics calculation
    metrics = get_db_metrics()
    assert metrics["total_prompts"] > 0
    assert metrics["blocked_leaks"] > 0