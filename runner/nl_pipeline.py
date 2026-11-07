from llm.nl_to_json_rulebased import parse_text_to_design
from llm.validate_design import validate_design
from llm.write_design_json import write_design_json
from runner.full_pipeline import main as run_full_pipeline
def run_nl_pipeline(user_text: str):
    print("Step 1: Parsing user input...")
    design = parse_text_to_design(user_text)

    print("Step 2: Validating design...")
    validate_design(design)

    json_path = "generated_design_input.json"

    print("Step 3: Writing JSON...")
    write_design_json(design, json_path)

    print("Step 4: Running full pipeline...")
    run_full_pipeline(json_path)

    print("\n✅ COMPLETE: Text → JSON → Optimization → TMM → Diagram")


if __name__ == "__main__":
    user_text = input("Enter your design request: ")
    run_nl_pipeline(user_text)