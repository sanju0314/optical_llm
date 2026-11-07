from llm.nl_to_json_openai import generate_design_from_text
import json

text = "Design a Bragg stack at 1550 nm using SiO2 and TiO2 with TM polarization"

design = generate_design_from_text(text)

print(json.dumps(design, indent=2))