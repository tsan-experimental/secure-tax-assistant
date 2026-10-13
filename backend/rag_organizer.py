"""
rag_organizer.py
Retrieves client data via retrieval.py, applies a PII safety gate,
and prompts a local Ollama LLM to generate a structured Multi-Year Tax Organizer.
"""

import ollama
from backend.retrieval import get_client_organizer_data
from backend.privacy_guard import redact_pii


def generate_tax_organizer(client_id: int) -> str:
    """
    Retrieves client data, ensures PII safety via a hard redaction gate,
    and prompts Ollama to build a clean, structured Multi-Year Tax Organizer.

    Returns:
        str: Markdown-formatted organizer, or an error message string.
    """
    data = get_client_organizer_data(client_id)
    if "error" in data:
        return data["error"]

    safe_profile = data["safe_profile"]
    token = data["client_token"]
    checklists = data["checklists"]
    tax_years = data["tax_years"]

    # Build checklist summary
    checklist_summary = "\n".join([
        f"- {item['tax_year']} {item['document_name']}: {item['status']}"
        for item in checklists
    ]) or "  (no checklist items on file)"

    # Build tax year summary
    year_summary = "\n".join([
        f"- {t['tax_year']}: ${t['gross_income']:,.2f} | {t['filing_status']} | "
        f"{t['employer']} | {t['notes']}"
        for t in tax_years
    ]) or "  (no tax year data on file)"

    prompt = f"""You are an automated tax document reporting system. Produce a clean text report for client record reference.

STRICT FORMATTING RULES:
- Do NOT use bolding stars (**).
- Do NOT use conversational filler or introductions.
- Use clean standard markdown headers (# and ##) and plain hyphens (-) for lists.
- Format document statuses as simple clear lines.

Data:
{safe_profile}

Tax Year Details:
{year_summary}

Document Checklists:
{checklist_summary}

Structure:
# Multi-Year Tax Organizer: {token}

## 1. Executive Summary
[Write a brief 1-2 sentence summary of the client's filing profile and document readiness]

## 2. Tax Year Breakdown
[For each year, list income, filing status, employer, and notes]

## 3. Document Status
[List documents grouped by tax year, marking each as Received or Missing]

## 4. Action Items
[List direct, prioritized action steps for outstanding documents]
"""

    # ─── HARD PII GATE (defense-in-depth) ─────────────────────────────────────
    # Even though retrieval.py already scrubs, we gate the final prompt
    # so no new data source added later can leak PII into the LLM.
    prompt = redact_pii(prompt)

    # ─── Call Ollama ──────────────────────────────────────────────────────────
    try:
        response = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": prompt}],
            options={"num_predict": 2048, "temperature": 0.2},
        )
    except Exception as e:
        return f"Error: Ollama LLM unavailable. {str(e)}"

    raw_content = response["message"]["content"]

    # Clean up any lingering markdown artifacts the model may emit
    cleaned_content = raw_content.replace("**", "").replace("`", "")

    return cleaned_content


if __name__ == "__main__":
    result = generate_tax_organizer(1)
    print(result)   