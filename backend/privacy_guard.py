import re

def redact_pii(text: str) -> str:
    """
    Scrub sensitive PII such as Social Security Numbers from input text.
    Matches standard SSN format (XXX-XX-XXXX) and replaces it with [REDACTED_SSN].
    """
    ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
    redacted_text = re.sub(ssn_pattern, '[REDACTED_SSN]', text)
    return redacted_text

if __name__ == "__main__":
    # Quick local test of the privacy guard
    sample_input = "Client's SSN is 123-45-6789 and their spouse's is 987-65-4321."
    print("Original:", sample_input)
    print("Redacted:", redact_pii(sample_input))