import ollama
import re
from backend.retrieval import get_client_organizer_data

def generate_tax_organizer(client_id: int):
    """
    Retrieves client data, ensures PII safety, and prompts Ollama 
    to build a clean, structured Multi-Year Tax Organizer.
    """
    data = get_client_organizer_data(client_id)
    if "error" in data:
        return data["error"]

    safe_profile = data["safe_profile"]
    token = data["client_token"]
    checklists = data["checklists"]

    checklist_summary = "\n".join([
        f"- {item['tax_year']} {item['document_name']}: {item['status']}"
        for item in checklists
    ])

    prompt = f"""
    You are an automated tax document reporting system. Produce a clean text report for client record reference.

    STRICT FORMATTING RULES:
    - Do NOT use bolding stars (**).
    - Do NOT use conversational filler or introductions.
    - Use clean standard markdown headers (# and ##) and plain hyphens (-) for lists.
    - Format document statuses as simple clear lines.

    Data:
    {safe_profile}

    Checklists:
    {checklist_summary}

    Structure:
    # Multi-Year Tax Organizer: {token}

    ## 1. Executive Summary
    [Write a brief 1-sentence summary]

    ## 2. Document Status Breakdown
    [List documents grouped by tax year]

    ## 3. Action Items
    [List direct action steps]
    """

    response = ollama.chat(model='llama3', messages=[
        {
            'role': 'user',
            'content': prompt,
        },
    ])

    raw_content = response['message']['content']

    # Clean up any lingering double asterisks or weird backticks
    cleaned_content = raw_content.replace("**", "").replace("`", "")
    
    return cleaned_content

if __name__ == "__main__":
    print(generate_tax_organizer(1))