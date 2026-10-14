"""
privacy_guard.py
Privacy Guardrail Layer for Secure Tax Assistant.

Redacts PII from raw text before it enters the LLM/RAG pipeline.
Uses regex-based detection for local execution.
Production escalation path: Microsoft Presidio (see README).

Limitations:
    - Bank account numbers are context-dependent and may produce
      false positives on long numeric strings (e.g., ZIP+4, routing numbers).
    - Date-of-birth detection uses common US formats only.
    - Full names are NOT redacted (requires NER / Presidio).
"""

import re
from dataclasses import dataclass, field


# ─── Pattern Registry ───────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Pattern:
    name: str
    regex: str
    replacement: str
    flags: int = 0


PII_PATTERNS: list[Pattern] = [
    # SSN — dashed (123-45-6789)
    Pattern(
        name="SSN_DASHED",
        regex=r"\b\d{3}-\d{2}-\d{4}\b",
        replacement="[REDACTED_SSN]",
    ),
    # SSN — plain 9 digits (123456789)
    # Excludes strings preceded/followed by more digits (avoids matching
    # substrings of longer numbers like account numbers).
    Pattern(
        name="SSN_PLAIN",
        regex=r"(?<!\d)\d{9}(?!\d)",
        replacement="[REDACTED_SSN]",
    ),
    # Phone — (555) 123-4567, 555-123-4567, 555.123.4567, 5551234567
    Pattern(
        name="PHONE",
        regex=r"\b(?:\(?[\d]{3}\)?[\s.-]?)[\d]{3}[\s.-]?[\d]{4}\b",
        replacement="[REDACTED_PHONE]",
    ),
    # Email
    Pattern(
        name="EMAIL",
        regex=r"[\w.+-]+@[\w-]+\.[\w.-]+",
        replacement="[REDACTED_EMAIL]",
    ),
    # Bank / routing account numbers — 8 to 17 consecutive digits
    # (will also catch routing numbers; acceptable tradeoff for tax context)
    # Production: replace with Presidio NER for context-aware detection.
    Pattern(
        name="ACCOUNT_NUMBER",
        regex=r"(?<!\d)\d{8,17}(?!\d)",
        replacement="[REDACTED_ACCOUNT]",
    ),
    # Date of Birth — MM/DD/YYYY, MM-DD-YYYY, MMM DD, YYYY
    Pattern(
        name="DOB",
        regex=r"\b(?:0[1-9]|1[0-2])[/\-.](?:0[1-9]|[12]\d|3[01])[/\-.](?:19|20)\d{2}\b",
        replacement="[REDACTED_DOB]",
    ),
    # ZIP code — 5 digits or ZIP+4
    Pattern(
        name="ZIP",
        regex=r"\b\d{5}(?:-\d{4})?\b",
        replacement="[REDACTED_ZIP]",
    ),
    # Driver's License (generic — 7-12 alphanumeric chars with prefix letter)
    Pattern(
        name="DL_NUMBER",
        regex=r"\b[A-Z]{1,2}[-\s]?\d{6,10}\b",
        replacement="[REDACTED_DL]",
        flags=re.IGNORECASE,
    ),
]


# ─── Core Function ──────────────────────────────────────────────────────────────

@dataclass
class RedactionResult:
    redacted_text: str
    findings: list[dict] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.findings)


def redact_pii(text: str, patterns: list[Pattern] | None = None) -> str:
    """
    Redact all detected PII from the given text.
    Returns the cleaned string.
    """
    return redact_pii_with_audit(text, patterns).redacted_text


def redact_pii_with_audit(
    text: str, patterns: list[Pattern] | None = None
) -> RedactionResult:
    """
    Redact PII and return a RedactionResult containing the cleaned text
    plus a list of findings (type, original value, position) for audit logging.

    FIX: findings are scanned on the progressively-cleaning string so that
    a value already replaced by an earlier pattern is not double-counted.
    """
    if patterns is None:
        patterns = PII_PATTERNS

    findings: list[dict] = []
    cleaned = text

    for p in patterns:
        for match in re.finditer(p.regex, cleaned, p.flags):
            findings.append({
                "type": p.name,
                "original": match.group(),
                "start": match.start(),
                "end": match.end(),
            })
        cleaned = re.sub(p.regex, p.replacement, cleaned, flags=p.flags)

    return RedactionResult(redacted_text=cleaned, findings=findings)


# ─── Self-Test ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sample = (
        "Client: John Smith\n"
        "SSN: 123-45-6789 (alt: 987654321)\n"
        "Phone: (415) 555-0199\n"
        "Email: john.smith@example.com\n"
        "Bank: 45210000001234567\n"
        "DOB: 03/14/1985\n"
        "Address: 123 Main St, Springfield, IL 62704\n"
        "DL: IL-1234567\n"
    )

    result = redact_pii_with_audit(sample)

    print("═══ REDACTED ═══")
    print(result.redacted_text)
    print(f"\n═══ AUDIT LOG ({result.count} findings) ═══")
    for f in result.findings:
        print(f"  [{f['type']}] {f['original']}  (pos {f['start']}–{f['end']})")
