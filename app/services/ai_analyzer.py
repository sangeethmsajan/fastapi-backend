import json
from openai import OpenAI
from app.core.config import settings

# connect to DeepSeek (OpenAI library, DeepSeek URL)
client = OpenAI(
    api_key=settings.deepseek_api_key,
    base_url="https://api.deepseek.com",
)

def analyze_findings(findings: dict) -> dict:
    # turn your nmap findings dict into text for the prompt
    findings_text = json.dumps(findings, indent=2)

    response = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a senior penetration tester. You receive nmap scan "
                    "results and analyze them. Respond ONLY with valid JSON."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Here are the nmap scan findings:\n{findings_text}\n\n"
                    "Analyze them and return JSON with these keys: "
                    '"risk_level" (Low/Medium/High/Critical), '
                    '"summary" (short text), '
                    '"vulnerabilities" (list of strings), '
                    '"next_steps" (list of recommended follow-up scans like '
                    "nikto, sqlmap, nuclei)."
                ),
            },
        ],
        response_format={"type": "json_object"},   # forces clean JSON output
        stream=False,
    )

    # the AI's answer comes back as a text string of JSON
    raw = response.choices[0].message.content
    return json.loads(raw)   # convert that JSON string into a Python dict