from __future__ import annotations

from llm.safe_exec import extract_d1_d2
from llm.criteria import pass_criteria
from runner.auto_tune import auto_tune_scale


def main():
    # Pretend this is LLM output (later we replace with OpenAI API output)
    llm_code = """
d1 = lambda0/(4*n1)
d2 = lambda0/(4*n2)
""".strip()

    lambda0 = 1000.0
    n1, n2 = 1.45, 2.40
    periods = 10

    # 1) Extract initial guess from LLM
    init = extract_d1_d2(llm_code, lambda0=lambda0, n1=n1, n2=n2)
    print("LLM initial guess:", init)

    # 2) Auto-tune thickness scale using physics metrics
    tuned = auto_tune_scale(n1=n1, n2=n2, lambda0=lambda0, periods=periods, iters=5)
    print("\nTuned design:")
    print(" d1:", tuned["d1"])
    print(" d2:", tuned["d2"])
    print(" metrics:", tuned["metrics"])

    # 3) Apply pass/fail criteria to tuned metrics
    ok, msg = pass_criteria(tuned["metrics"])
    print("\nFinal Result:", msg)


if __name__ == "__main__":
    main()