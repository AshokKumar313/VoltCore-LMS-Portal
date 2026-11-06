"""
========================================================================================
VoltCore Apex Academia - Phase I Unit Test Suite (Features 291–300)
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU footprint.
========================================================================================
"""

import os
import sqlite3
import pytest
from backend.ai_assisted_learning_engine import (
    explain_ece_concept,
    explain_ece_code,
    summarize_ece_notes,
    generate_ece_questions,
    describe_ece_diagram,
    evaluate_ece_assignment,
    generate_ece_study_plan,
    lookup_technical_vocabulary,
    interact_viva_session,
    summarize_ece_research_paper,
    init_ai_learning_db
)

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_ai_learning.db")

@pytest.fixture(autouse=True)
def clean_test_db():
    """Ensure clean isolated SQLite test database."""
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass
    init_ai_learning_db(TEST_DB_PATH)
    yield
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass

# Feature 291: Concept Explainer
def test_explain_ece_concept_depths():
    # Test undergraduate depth
    res_ug = explain_ece_concept("pn_junction_diode", depth="undergraduate", language="en", db_path=TEST_DB_PATH)
    assert res_ug["status"] == "success"
    assert "Shockley" in res_ug["explanation"]
    assert len(res_ug["formulae"]) >= 2
    assert "Bridge Rectifiers" in res_ug["applications"][0]

    # Test ELI5 depth
    res_eli5 = explain_ece_concept("pn_junction_diode", depth="eli5", language="en", db_path=TEST_DB_PATH)
    assert "turnstile" in res_eli5["explanation"].lower()

    # Test Rigorous depth
    res_rig = explain_ece_concept("pn_junction_diode", depth="rigorous", language="en", db_path=TEST_DB_PATH)
    assert "Poisson" in res_rig["explanation"]

    # Test Tamil & Bilingual
    res_ta = explain_ece_concept("bjt_amplification", depth="undergraduate", language="ta", db_path=TEST_DB_PATH)
    assert "மின்னழுத்தப் பெருக்கம்" in res_ta["explanation"]

    res_bi = explain_ece_concept("fourier_transform", depth="undergraduate", language="bilingual", db_path=TEST_DB_PATH)
    assert "English" in res_bi["explanation"]
    assert "தமிழ்" in res_bi["explanation"]

# Feature 292: Code Explainer
def test_explain_ece_code_verilog():
    verilog_code = """
    module d_ff (input wire clk, input wire d, output reg q);
        always @(posedge clk) begin
            q <= d;
        end
    endmodule
    """
    res = explain_ece_code(verilog_code, language="verilog")
    assert res["status"] == "success"
    assert len(res["annotated_lines"]) >= 4
    assert any("Flip-Flop" in a["annotation"] for a in res["annotated_lines"])
    assert any("Sequential Logic" in hw for hw in res["hardware_summary"]["inferred_hardware"])

def test_explain_ece_code_arm_c():
    c_code = """
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    GPIOA->MODER |= (1 << 10);
    GPIOA->ODR ^= (1 << 5);
    """
    res = explain_ece_code(c_code, language="c_embedded")
    assert res["status"] == "success"
    assert any("Clock Gating" in a["hardware_element"] for a in res["annotated_lines"])
    assert any("GPIO Port" in a["hardware_element"] for a in res["annotated_lines"])

# Feature 293: Notes Summarizer
def test_summarize_ece_notes():
    dense_text = """
    In a common emitter amplifier, the transistor is biased in the active region.
    The voltage gain is given by Av = -gm * RC where gm is transconductance.
    The input impedance is primarily determined by r_pi = beta / gm.
    Negative feedback can be introduced using an unbypassed emitter resistor RE to stabilize gain.
    High frequency response is limited by Miller capacitance C_mu between base and collector.
    """
    res = summarize_ece_notes(dense_text, max_bullets=3)
    assert res["status"] == "success"
    assert len(res["key_points"]) <= 3
    assert len(res["formula_sheet"]) >= 1
    assert "Av" in res["formula_sheet"][0]["formula"] or "r_pi" in res["formula_sheet"][0]["formula"] or "V" in res["formula_sheet"][0]["formula"]
    assert "5-Minute" in res["cram_card"]["title"]

# Feature 294: Question Generator
def test_generate_ece_questions_part_a():
    res = generate_ece_questions(subject_code="EC3351", topic="Transfer Functions", bloom_level="remember", question_type="part_a_2mark")
    assert res["status"] == "success"
    q_data = res["question_data"]
    assert q_data["marks"] == 2
    assert "transfer function" in q_data["question"].lower()
    assert "H(s)" in q_data["model_answer"]

def test_generate_ece_questions_part_b():
    res = generate_ece_questions(subject_code="EC3351", topic="Root Locus", bloom_level="apply", question_type="part_b_16mark")
    assert res["status"] == "success"
    q_data = res["question_data"]
    assert q_data["marks"] == 16
    assert "rubric" in q_data
    assert "Root Locus" in q_data["question"]

# Feature 295: Diagram Description Assistant
def test_describe_ece_diagram_schematic():
    res = describe_ece_diagram("circuit_schematic", "ce_amplifier")
    assert res["status"] == "success"
    assert "BC547" in res["ascii_art"]
    assert "+VCC" in res["ascii_art"]
    assert len(res["key_nodes"]) >= 3

def test_describe_ece_diagram_timing_and_fsm():
    res_spi = describe_ece_diagram("timing_diagram", "spi_bus_timing")
    assert "SCLK" in res_spi["ascii_art"]
    assert "MOSI" in res_spi["ascii_art"]

    res_fsm = describe_ece_diagram("state_machine", "mealy_fsm")
    assert "1011" in res_fsm["title"]
    assert "[S0]" in res_fsm["ascii_art"]

# Feature 296: Assignment Feedback
def test_evaluate_ece_assignment():
    submission = """
    Aim: Design CE amplifier for voltage gain Av = 10 at 1 kHz.
    Formulas: Av = -gm * RC = -10, VCC = 12V, IC = 2 mA.
    Components: Transistor BC547, R1 = 22 kohm, R2 = 4.7 kohm, RC = 3 kohm, CE = 10 uf.
    Result: Observed peak-to-peak output voltage Vo = 2.0 V for Vin = 200 mV. Error is 2%.
    """
    res = evaluate_ece_assignment(submission, assignment_type="lab_experiment", max_score=20.0, db_path=TEST_DB_PATH)
    assert res["status"] == "success"
    assert res["total_score"] >= 14.0
    assert len(res["praise_points"]) >= 2
    assert "theoretical_rigor" in res["rubric_breakdown"]

# Feature 297: Study Plan Generator
def test_generate_ece_study_plan():
    res = generate_ece_study_plan(student_id="2023MITEC042", subject_code="EC3351", days_remaining=10, daily_hours=3.5, db_path=TEST_DB_PATH)
    assert res["status"] == "success"
    plan = res["plan"]
    assert plan["days_remaining"] == 10
    assert plan["total_study_hours"] == 35.0
    assert len(plan["daily_schedule"]) == 10
    assert "Unit I" in plan["daily_schedule"][0]["focus"]

# Feature 298: Technical Vocabulary
def test_lookup_technical_vocabulary():
    res_baud = lookup_technical_vocabulary("baud_rate")
    assert res_baud["status"] == "success"
    assert res_baud["symbol"] == "Bd"
    assert "COMMON TRAP" in res_baud["misconception_trap"]
    assert "பாட் வீதம்" in res_baud["tamil"]

    res_imp = lookup_technical_vocabulary("impedance")
    assert "Heaviside" in res_imp["etymology"]
    assert "Z = R + j" in res_imp["key_formula"]

# Feature 299: Viva Practice Assistant
def test_interact_viva_session():
    # Start session
    start_res = interact_viva_session(session_id=None, subject="EC3361", examiner_persona="friendly_mit_prof", db_path=TEST_DB_PATH)
    assert start_res["status"] == "session_started"
    assert "VIVA-" in start_res["session_id"]
    assert "0.7V" in start_res["question"]

    # Student answers
    session_id = start_res["session_id"]
    ans = "Silicon has a wider energy bandgap of 1.1 eV and lower intrinsic carrier concentration ni compared to germanium, resulting in higher built-in potential barrier."
    turn_res = interact_viva_session(session_id=session_id, student_answer=ans, db_path=TEST_DB_PATH)
    assert turn_res["status"] == "ongoing"
    assert turn_res["turn_score"] >= 7.0
    assert "Good attempt" in turn_res["examiner_feedback"]
    assert "reverse recovery" in turn_res["next_question"].lower()

# Feature 300: Research Paper Summarizer
def test_summarize_ece_research_paper():
    paper_title = "Energy-Efficient Sub-Threshold SRAM Design for Ultra-Low Power Biomedical SoCs"
    paper_text = """
    In sub-10nm FinFET technologies, leakage current dominates static dissipation.
    We present a 10T differential SRAM cell operating down to 0.35V.
    Experimental results demonstrate 45% reduction in leakage power, dissipating only 1.2 uW
    with read access delay of 85 ps at 100 MHz.
    """
    res = summarize_ece_research_paper(paper_title, paper_text, domain="vlsi", student_id="2023MITEC042", db_path=TEST_DB_PATH)
    assert res["status"] == "success"
    summary = res["summary"]
    assert summary["domain"] == "VLSI"
    assert "1.2 UW" in summary["quantitative_findings"] or "45 %" in summary["quantitative_findings"] or "85 PS" in summary["quantitative_findings"]
    assert "MIT Campus" in summary["final_year_project_scope"]

# SQLite WAL Persistence Test
def test_ai_learning_sqlite_persistence():
    # Verify records stored in SQLite WAL database
    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cursor.fetchall()]
    assert "ai_concept_queries" in tables
    assert "ai_study_plans" in tables
    assert "ai_viva_sessions" in tables
    assert "ai_paper_summaries" in tables
    assert "ai_assignment_evaluations" in tables
    conn.close()
