import json

def write_design_json(design: dict, path: str = "generated_design_input.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(design, f, indent=2)