import re
from typing import List, Tuple

SENSITIVE_PATTERNS = [
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
    r"\b(?:\d[ -]?){13,16}\b",
    r"\b(?:sk_live_[A-Za-z0-9]+|ghp_[A-Za-z0-9]+|AKIA[0-9A-Z]{16})\b",
    r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    r"\b(?:\+?1[ -]?)?(?:\(\d{3}\)|\d{3})[ -.]\d{3}[ -.]\d{4}\b",
]


def redact_pii(text: str) -> str:
    """Mask obvious sensitive values before indexing."""
    redacted = text
    for pattern in SENSITIVE_PATTERNS:
        redacted = re.sub(pattern, "[REDACTED]", redacted, flags=re.IGNORECASE)
    return redacted


def find_sensitive_segments(text: str) -> List[Tuple[int, int, str]]:
    """Return positions of detected sensitive values.

    This can be extended to support structured redaction decisions and UI review.
    """
    findings: List[Tuple[int, int, str]] = []
    for pattern in SENSITIVE_PATTERNS:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            findings.append((match.start(), match.end(), match.group(0)))
    return findings
