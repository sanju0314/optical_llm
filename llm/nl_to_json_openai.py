import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_design_from_text(user_text: str) -> dict:
    prompt = f"""
Convert the following user request into a JSON configuration for a 1D Bragg photonic crystal.

IMPORTANT:
- Return ONLY valid JSON
- Do NOT include explanation
- Follow this exact schema:

{{
  "device_type": "bragg_stack",
  "lambda0_nm": number,
  "wavelength_range_nm": [number, number],
  "materials": [
    {{"name": string, "n": number}},
    {{"name": string, "n": number}}
  ],
  "structure": {{
    "periods": number,
    "d1_nm": number,
    "d2_nm": number,
    "order": "HL" or "LH"
  }},
  "optical_conditions": {{
    "incident_angle_deg": number,
    "polarization": "TE" or "TM"
  }},
  "optimization": {{
    "method": "bayesian",
    "trials": number
  }},
  "targets": {{
    "max_center_error_nm": number,
    "min_bandgap_width_nm": number,
    "max_minT": number
  }}
}}

Use reasonable defaults if values are missing.

User request:
{user_text}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You convert photonic design requests into strict JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    content = response.choices[0].message.content

    return json.loads(content)