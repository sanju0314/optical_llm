from llm.nl_to_json_rulebased import parse_text_to_design
from llm.validate_design import validate_design
import json

test_inputs = [
    "Design a Bragg stack at 1000 nm using SiO2 and TiO2",
    "Design a Bragg stack at 1550 nm using silicon dioxide and titanium dioxide with TM polarization",
    "Create a photonic crystal from 600 nm to 1400 nm using MgF2 and ZnS with 12 periods",
    "Make a Bragg stack at 1200 nm using Al2O3 and TiO2 with center error below 5 nm and bandgap width at least 200 nm",
    "Design a stack at 1000 nm using SiO2 and TiO2 with 50 trials and LH order"
]

for i, text in enumerate(test_inputs, start=1):
    print(f"\n--- TEST {i} ---")
    print("INPUT:", text)
    design = parse_text_to_design(text)
    validate_design(design)
    print(json.dumps(design, indent=2))