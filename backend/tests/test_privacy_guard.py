"""Unit tests for backend.privacy_guard — PII redaction engine."""

from backend.privacy_guard import (
    redact_pii,
    redact_pii_with_audit,
    RedactionResult,
)


class TestSSN:
    def test_dashed_ssn(self):
        result = redact_pii_with_audit("SSN: 123-45-6789")
        assert "123-45-6789" not in result.redacted_text
        assert "[REDACTED_SSN]" in result.redacted_text
        assert any(f["type"] == "SSN_DASHED" for f in result.findings)

    def test_plain_ssn(self):
        result = redact_pii_with_audit("SSN: 123456789")
        assert "123456789" not in result.redacted_text
        assert "[REDACTED_SSN]" in result.redacted_text
        assert any(f["type"] == "SSN_PLAIN" for f in result.findings)

    def test_ssn_in_sentence(self):
        text = "The client's SSN is 987-65-4321 and should be stored securely."
        result = redact_pii_with_audit(text)
        assert "987-65-4321" not in result.redacted_text
        assert "client's" in result.redacted_text


class TestPhone:
    def test_standard_phone(self):
        result = redact_pii_with_audit("Call 555-123-4567 for details.")
        assert "555-123-4567" not in result.redacted_text
        assert "[REDACTED_PHONE]" in result.redacted_text

    def test_phone_with_parens(self):
        result = redact_pii_with_audit("Reach us at (555) 987-6543.")
        assert "987-6543" not in result.redacted_text
        assert "[REDACTED_PHONE]" in result.redacted_text

    def test_phone_with_dots(self):
        result = redact_pii_with_audit("Number: 555.123.4567")
        assert "555.123.4567" not in result.redacted_text
        assert "[REDACTED_PHONE]" in result.redacted_text


class TestEmail:
    def test_simple_email(self):
        result = redact_pii_with_audit("Contact: alice.smith@example.com")
        assert "alice.smith@example.com" not in result.redacted_text
        assert "[REDACTED_EMAIL]" in result.redacted_text

    def test_email_with_plus(self):
        result = redact_pii_with_audit("Send to bob.jones+tax@techstart.io")
        assert "bob.jones+tax@techstart.io" not in result.redacted_text
        assert "[REDACTED_EMAIL]" in result.redacted_text


class TestBankAccount:
    def test_account_12_digits(self):
        result = redact_pii_with_audit("Account: 123456789012")
        assert "123456789012" not in result.redacted_text
        assert "[REDACTED_ACCOUNT]" in result.redacted_text

    def test_account_17_digits(self):
        result = redact_pii_with_audit("Bank: 45210000001234567")
        assert "45210000001234567" not in result.redacted_text
        assert "[REDACTED_ACCOUNT]" in result.redacted_text


class TestDOB:
    def test_dob_slash(self):
        result = redact_pii_with_audit("DOB: 03/15/1985")
        assert "03/15/1985" not in result.redacted_text
        assert "[REDACTED_DOB]" in result.redacted_text

    def test_dob_dash(self):
        result = redact_pii_with_audit("DOB: 12-25-1990")
        assert "12-25-1990" not in result.redacted_text
        assert "[REDACTED_DOB]" in result.redacted_text


class TestZIP:
    def test_zip5(self):
        result = redact_pii_with_audit("Mailing to 90210")
        assert "90210" not in result.redacted_text
        assert "[REDACTED_ZIP]" in result.redacted_text

    def test_zip_plus_4(self):
        result = redact_pii_with_audit("Address: 100 Main St, 90210-1234")
        assert "90210-1234" not in result.redacted_text
        assert "[REDACTED_ZIP]" in result.redacted_text


class TestDriversLicense:
    def test_dl_two_letter_prefix(self):
        result = redact_pii_with_audit("DL: IL-1234567")
        assert "IL-1234567" not in result.redacted_text
        assert "[REDACTED_DL]" in result.redacted_text

    def test_dl_lowercase(self):
        result = redact_pii_with_audit("DL: ca-9876543")
        assert "ca-9876543" not in result.redacted_text
        assert "[REDACTED_DL]" in result.redacted_text


class TestAuditLog:
    def test_returns_redaction_result(self):
        result = redact_pii_with_audit("SSN: 123-45-6789")
        assert isinstance(result, RedactionResult)
        assert result.count >= 1

    def test_finding_keys(self):
        result = redact_pii_with_audit("SSN: 123-45-6789")
        finding = result.findings[0]
        assert "type" in finding
        assert "original" in finding
        assert "start" in finding
        assert "end" in finding

    def test_multiple_findings(self):
        text = "SSN: 123-45-6789, Email: test@test.com, Phone: 555-123-4567"
        result = redact_pii_with_audit(text)
        assert result.count >= 3

    def test_no_pii_empty_findings(self):
        result = redact_pii_with_audit("The tax return was filed on time.")
        assert result.redacted_text == "The tax return was filed on time."
        assert result.findings == []


class TestRedactPII:
    def test_returns_string(self):
        result = redact_pii("SSN: 123-45-6789")
        assert isinstance(result, str)
        assert "123-45-6789" not in result

    def test_no_pii_unchanged(self):
        text = "Client filed MFJ for tax year 2024."
        assert redact_pii(text) == text


class TestEdgeCases:
    def test_empty_string(self):
        result = redact_pii_with_audit("")
        assert result.redacted_text == ""
        assert result.findings == []

    def test_mixed_pii_and_normal_text(self):
        text = "Alice (alice@acme.com) called 555-123-4567 about her 1099-NEC."
        result = redact_pii_with_audit(text)
        assert "alice@acme.com" not in result.redacted_text
        assert "555-123-4567" not in result.redacted_text
        assert "Alice" in result.redacted_text
        assert "1099-NEC" in result.redacted_text

    def test_self_test_sample(self):
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
        types_found = {f["type"] for f in result.findings}
        assert "SSN_DASHED" in types_found
        assert "SSN_PLAIN" in types_found
        assert "PHONE" in types_found
        assert "EMAIL" in types_found
        assert "ACCOUNT_NUMBER" in types_found
        assert "DOB" in types_found
        assert "ZIP" in types_found
        assert "DL_NUMBER" in types_found
        assert "John Smith" in result.redacted_text
