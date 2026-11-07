import json
from pathlib import Path

import streamlit as st

from llm.nl_to_json_rulebased import parse_text_to_design
from llm.validate_design import validate_design
from llm.write_design_json import write_design_json
from runner.full_pipeline import main as run_full_pipeline

st.set_page_config(
    page_title="Optical Bragg Designer",
    layout="wide"
)

st.markdown("""
<style>
.main-title {
    font-size: 2.2rem;
    font-weight: 700;
    margin-bottom: 0.2rem;
}
.sub-title {
    font-size: 1rem;
    color: #888;
    margin-bottom: 1.2rem;
}
.block-box {
    padding: 1rem 0rem 0.7rem 0rem;
    background-color: transparent;
    border: none;
    margin-bottom: 0rem;
}
.small-note {
    color: #888;
    font-size: 0.92rem;
}
[data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.9rem !important;
}
[data-testid="stMetric"] {
    padding: 0px 6px;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="main-title">1D Bragg Photonic Crystal Designer</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="sub-title">Natural language input → JSON generation → Bayesian optimization → TMM validation → stack diagram</div>',
    unsafe_allow_html=True
)

st.sidebar.title("Design Help")
st.sidebar.info(
    "Type a design request in natural language.\n\n"
    "Example:\n"
    "`Design a Bragg stack at 1000 nm using SiO2 and TiO2 with 12 periods and TM polarization`"
)

show_json = st.sidebar.checkbox("Show JSON outputs", value=True)
show_debug = st.sidebar.checkbox("Show step messages", value=True)

sample_prompt = st.sidebar.selectbox(
    "Load sample prompt",
    [
        "Design a Bragg stack at 1000 nm using SiO2 and TiO2 with 10 periods and TE polarization",
        "Design a Bragg stack at 1550 nm using silicon dioxide and titanium dioxide with TM polarization",
        "Create a photonic crystal from 600 nm to 1400 nm using MgF2 and ZnS with 12 periods",
        "Make a Bragg stack at 1200 nm using Al2O3 and TiO2 with center error below 5 nm and bandgap width at least 200 nm",
        "Design a stack at 1000 nm using SiO2 and TiO2 with 50 trials and LH order"
    ]
)

st.markdown('<div class="block-box">', unsafe_allow_html=True)
st.subheader("Enter design request")

user_text = st.text_area(
    "Natural-language input",
    value=sample_prompt,
    height=130,
    label_visibility="collapsed"
)

run_clicked = st.button("Run Design Pipeline", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

if run_clicked:
    try:
        if show_debug:
            st.info("Parsing request and building JSON configuration...")

        design = parse_text_to_design(user_text)
        validate_design(design)

        json_path = "generated_design_input.json"
        write_design_json(design, json_path)

        if show_debug:
            st.success("Input parsed and validated successfully.")

        left_col, right_col = st.columns([1.15, 1])

        with left_col:
            st.markdown('<div class="block-box">', unsafe_allow_html=True)
            st.subheader("Parsed Design Summary")

            mat1 = design["materials"][0]["name"]
            mat2 = design["materials"][1]["name"]
            lam = design["lambda0_nm"]
            periods = design["structure"]["periods"]
            pol = design["optical_conditions"]["polarization"]

            m1, m2, m3, m4 = st.columns(4)

            with m1:
                st.metric("Target λ (nm)", f"{lam}")

            with m2:
                materials_html = " ".join([
                    f'<span style="background:#1f2937; padding:5px 10px; border-radius:8px; margin-right:6px; font-size:0.95rem;">{mat1}</span>',
                    f'<span style="background:#1f2937; padding:5px 10px; border-radius:8px; font-size:0.95rem;">{mat2}</span>'
                ])

                st.markdown(
                    f"""
                    <div style="font-size: 0.85rem; color: #aaaaaa; margin-bottom: 8px;">
                        Materials
                    </div>
                    <div style="line-height: 2;">
                        {materials_html}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with m3:
                st.metric("Periods", f"{periods}")

            with m4:
                st.metric("Polarization", pol)

            st.markdown('</div>', unsafe_allow_html=True)

            if show_json:
                with st.expander("View generated JSON", expanded=False):
                    st.json(design)

        with right_col:
            st.markdown('<div class="block-box">', unsafe_allow_html=True)
            st.subheader("Pipeline Status")
            status = st.empty()
            status.info("Running Bayesian optimization and TMM validation...")
            run_full_pipeline(json_path)
            status.success("Pipeline completed successfully.")
            st.markdown('</div>', unsafe_allow_html=True)

        updated_path = Path(json_path)
        updated_design = None
        if updated_path.exists():
            with open(updated_path, "r", encoding="utf-8") as f:
                updated_design = json.load(f)

        if updated_design is not None:
            st.markdown('<div class="block-box">', unsafe_allow_html=True)
            st.subheader("Optimized Design Output")

            d1 = updated_design["structure"]["d1_nm"]
            d2 = updated_design["structure"]["d2_nm"]
            order = updated_design["structure"]["order"]
            trials = updated_design["optimization"]["trials"]

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("d1_nm", f"{d1:.3f}")
            c2.metric("d2_nm", f"{d2:.3f}")
            c3.metric("Order", order)
            c4.metric("Trials", trials)

            st.markdown('</div>', unsafe_allow_html=True)

            if show_json:
                with st.expander("View optimized JSON", expanded=False):
                    st.json(updated_design)

        img_path = Path("bragg_stack.png")
        st.markdown('<div class="block-box">', unsafe_allow_html=True)
        st.subheader("Generated Bragg Stack Diagram")

        if img_path.exists():
            st.image(
                str(img_path),
                caption="Optimized Bragg Stack Schematic",
                use_container_width=True
            )
        else:
            st.warning("Diagram image not found.")

        st.markdown('</div>', unsafe_allow_html=True)

        st.caption(
            "Current version uses a rule-based natural-language parser as a placeholder for future LLM integration."
        )

    except Exception as e:
        st.error(f"Error: {e}")