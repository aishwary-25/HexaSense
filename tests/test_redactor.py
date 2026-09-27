# tests/test_redactor.py

from src.redactor import redact_pii, find_sensitive_segments


def test_redact_pii_email():
    text = "Contact alice@example.com for follow-up."
    redacted = redact_pii(text)
    assert "alice@example.com" not in redacted
    assert "[REDACTED]" in redacted


def test_redact_pii_credit_card():
    text = "Card number 4111 1111 1111 1111"
    redacted = redact_pii(text)
    assert "4111 1111 1111 1111" not in redacted


def test_find_sensitive_segments_basic():
    text = "Use support@company.com and call 555-123-4567"
    findings = find_sensitive_segments(text)
    assert len(findings) >= 2
