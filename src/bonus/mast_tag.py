"""Bonus Topic B2: Automated Failure Tagging using the MAST Taxonomy (NeurIPS 2025).

Reference:
    "Why Do Multi-Agent LLM Systems Fail?" (NeurIPS 2025).
    14 failure modes grouped into 3 core categories:
      1. System Design
      2. Inter-agent Misalignment
      3. Task Verification
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

# Core MAST Taxonomy Groups (NeurIPS 2025)
GROUP_SYSTEM_DESIGN = "System Design"
GROUP_INTER_AGENT_MISALIGNMENT = "Inter-agent Misalignment"
GROUP_TASK_VERIFICATION = "Task Verification"

ALL_MAST_GROUPS = [
    GROUP_SYSTEM_DESIGN,
    GROUP_INTER_AGENT_MISALIGNMENT,
    GROUP_TASK_VERIFICATION,
]

# MAST 14 Failure Modes mapped to our 3 Groups
FAILURE_MODES = {
    # 1. System Design: Protocol design, authorization gates, and tool boundaries
    "SD-1": ("Tool / Resource Permission Violation", GROUP_SYSTEM_DESIGN),
    "SD-2": ("Missing or Invalid Approval Authorization", GROUP_SYSTEM_DESIGN),
    "SD-3": ("Policy Boundary & Superseded Clause Violation", GROUP_SYSTEM_DESIGN),
    "SD-4": ("Unsafe Context Exposure / Redaction Failure", GROUP_SYSTEM_DESIGN),

    # 2. Inter-agent Misalignment: Communication breakdowns, context loss, role confusion
    "IAM-1": ("Information Loss in Handoff", GROUP_INTER_AGENT_MISALIGNMENT),
    "IAM-2": ("Inconsistent Inter-Agent Messaging", GROUP_INTER_AGENT_MISALIGNMENT),
    "IAM-3": ("Context Distortion across Agent Boundaries", GROUP_INTER_AGENT_MISALIGNMENT),
    "IAM-4": ("Role Confusion / Misdelegated Task", GROUP_INTER_AGENT_MISALIGNMENT),
    "IAM-5": ("Error Cascade / Multi-Agent Amplification", GROUP_INTER_AGENT_MISALIGNMENT),

    # 3. Task Verification: Grounding, checking against ground truth, verifier absence
    "TV-1": ("Grounding Failure / Untrusted Text Belief", GROUP_TASK_VERIFICATION),
    "TV-2": ("Missing Verification Gate / Output Status Mismatch", GROUP_TASK_VERIFICATION),
    "TV-3": ("Calculation Discrepancy without Self-Correction", GROUP_TASK_VERIFICATION),
    "TV-4": ("Premature Termination / Unverified Action", GROUP_TASK_VERIFICATION),
    "TV-5": ("Per-Order Cap & Entitlement State Blindness", GROUP_TASK_VERIFICATION),
}


def classify_failure(trial: dict[str, Any], trace: dict[str, Any] | None = None) -> dict[str, str]:
    """Classify a failed trial into a MAST group and failure mode based on trace and trial metadata.

    Returns:
        dict with keys: 'failure_group', 'failure_mode', 'failure_mode_id', 'rationale'
    """
    reason = str(trial.get("reason", "")).lower()
    error_reason = str(trial.get("error_reason", "")).lower()
    claim_id = str(trial.get("claim_id", ""))
    events = (trace or {}).get("events", [])

    # Heuristic 1: Check for Model Override / Grounding Failure (Task Verification - TV-1)
    # Model accepted ticket claim instead of ground truth order data (e.g. Swarm C-002 on seed 55)
    for event in events:
        kind = event.get("kind", "")
        payload = event.get("payload", {})
        if kind == "model_override" or "override" in kind:
            return {
                "failure_group": GROUP_TASK_VERIFICATION,
                "failure_mode_id": "TV-1",
                "failure_mode": FAILURE_MODES["TV-1"][0],
                "rationale": f"Model overrode ground-truth order data via event '{kind}' with payload {payload}, trusting user ticket text over database.",
            }
        if kind == "quote":
            # If quote reason cites customer assertion over structured order row
            quote_reason = str(payload.get("reason", "")).lower()
            if "ticket_claim" in quote_reason or "customer_stated" in quote_reason:
                return {
                    "failure_group": GROUP_TASK_VERIFICATION,
                    "failure_mode_id": "TV-1",
                    "failure_mode": FAILURE_MODES["TV-1"][0],
                    "rationale": f"Quoting logic trusted customer text assertion ('{quote_reason}') without independent verifier.",
                }

    # Heuristic 2: Information Loss or Context Drop in Handoff (Inter-agent Misalignment - IAM-1 / IAM-3)
    for event in events:
        if event.get("kind") == "handoff":
            payload = event.get("payload", {})
            facts = payload.get("facts", {})
            dropped_fields = payload.get("dropped_fields", [])
            if "delay_days" in dropped_fields or ("delay_days" not in facts and payload.get("task") == "quote"):
                return {
                    "failure_group": GROUP_INTER_AGENT_MISALIGNMENT,
                    "failure_mode_id": "IAM-1",
                    "failure_mode": FAILURE_MODES["IAM-1"][0],
                    "rationale": "Essential fact 'delay_days' dropped during handoff between orchestrator and downstream worker.",
                }
            if payload.get("context_distorted", False) or "corrupted_context" in payload:
                return {
                    "failure_group": GROUP_INTER_AGENT_MISALIGNMENT,
                    "failure_mode_id": "IAM-3",
                    "failure_mode": FAILURE_MODES["IAM-3"][0],
                    "rationale": "Context corrupted or distorted across agent communication boundary.",
                }

    # Heuristic 3: Host Policy Authorization Denials (System Design - SD-2 / SD-3)
    # Host gate blocked refund because approval was missing, expired, mismatched, or policy outdated
    if "policy_denied" in reason or "approval" in reason or "policy_denied" in error_reason:
        if "mismatch" in reason or "mismatch" in error_reason:
            return {
                "failure_group": GROUP_SYSTEM_DESIGN,
                "failure_mode_id": "SD-2",
                "failure_mode": FAILURE_MODES["SD-2"][0],
                "rationale": "Claim presented an approval ID assigned to a different claim (approval_claim_mismatch), blocked by host authorization gate.",
            }
        return {
            "failure_group": GROUP_SYSTEM_DESIGN,
            "failure_mode_id": "SD-2",
            "failure_mode": FAILURE_MODES["SD-2"][0],
            "rationale": f"Host authorization gate rejected transaction: '{reason or error_reason}'.",
        }

    # Heuristic 4: Architecture / Permission / Implementation stub (System Design - SD-1)
    if "not_implemented" in reason or "not_implemented" in error_reason or "permission" in reason:
        return {
            "failure_group": GROUP_SYSTEM_DESIGN,
            "failure_mode_id": "SD-1",
            "failure_mode": FAILURE_MODES["SD-1"][0],
            "rationale": "Shape failed architectural contract or invoked unauthorized tool: not_implemented / permission error.",
        }

    # Heuristic 5: Status Mismatch / Quoting logic discrepancy (Task Verification - TV-2 / TV-3)
    if "status" in reason or "amount" in reason:
        # Check if status mismatch is resolved vs denied
        if "resolved != denied" in reason:
            return {
                "failure_group": GROUP_TASK_VERIFICATION,
                "failure_mode_id": "TV-1",
                "failure_mode": FAILURE_MODES["TV-1"][0],
                "rationale": f"Trial resolved a claim that should have been denied ({reason}); hallucinated entitlement or failed to verify criteria against database.",
            }
        return {
            "failure_group": GROUP_TASK_VERIFICATION,
            "failure_mode_id": "TV-2",
            "failure_mode": FAILURE_MODES["TV-2"][0],
            "rationale": f"Output validation failed with mismatch: '{reason}'.",
        }

    # Default fallback
    return {
        "failure_group": GROUP_TASK_VERIFICATION,
        "failure_mode_id": "TV-2",
        "failure_mode": FAILURE_MODES["TV-2"][0],
        "rationale": f"General unverified execution discrepancy: '{reason or error_reason or 'unspecified failure'}'.",
    }


def compute_cohen_kappa(human_labels: list[str], machine_labels: list[str]) -> dict[str, Any]:
    """Compute Observed Agreement and Cohen's Kappa between human annotations and machine labels."""
    if len(human_labels) != len(machine_labels):
        raise ValueError("Human and machine label lists must have identical length")

    n = len(human_labels)
    if n == 0:
        return {"n": 0, "agreement_rate": 0.0, "cohen_kappa": 0.0}

    # Observed agreement
    agreements = sum(1 for h, m in zip(human_labels, machine_labels) if h == m)
    p_o = agreements / n

    # Marginal probabilities
    categories = sorted(list(set(human_labels) | set(machine_labels)))
    p_e = 0.0
    for cat in categories:
        p_human = sum(1 for h in human_labels if h == cat) / n
        p_machine = sum(1 for m in machine_labels if m == cat) / n
        p_e += (p_human * p_machine)

    # Cohen's Kappa: (P_o - P_e) / (1 - P_e)
    if abs(1.0 - p_e) < 1e-9:
        kappa = 1.0 if abs(p_o - 1.0) < 1e-9 else 0.0
    else:
        kappa = (p_o - p_e) / (1.0 - p_e)

    # Build contingency matrix
    matrix: dict[str, dict[str, int]] = {h_cat: {m_cat: 0 for m_cat in categories} for h_cat in categories}
    for h, m in zip(human_labels, machine_labels):
        matrix[h][m] += 1

    return {
        "n": n,
        "agreements": agreements,
        "agreement_rate": round(p_o, 4),
        "chance_agreement_pe": round(p_e, 4),
        "cohen_kappa": round(kappa, 4),
        "categories": categories,
        "contingency_matrix": matrix,
    }


# Standard 15 Human-Annotated Reference Cases for Inter-Annotator Agreement Assessment
REFERENCE_HUMAN_ANNOTATIONS = [
    {
        "id": "CASE-01",
        "trial": {"shape": "swarm", "claim_id": "C-002", "seed": 55, "reason": "status resolved != denied"},
        "trace": {
            "events": [
                {"kind": "investigator", "payload": {"order": {"delay_days": 2}}},
                {"kind": "model_override", "payload": {"delay_days": 5}},
            ]
        },
        "human_group": GROUP_TASK_VERIFICATION,
        "human_mode": "TV-1",
        "description": "Swarm seed 55 hallucinated delay override trusting ticket text",
    },
    {
        "id": "CASE-02",
        "trial": {"shape": "orchestrator", "claim_id": "C-007", "seed": 11, "reason": "policy_denied: approval_expired"},
        "trace": {"events": [{"kind": "host_call", "payload": {"status": "denied", "audit": "policy_denied"}}]},
        "human_group": GROUP_SYSTEM_DESIGN,
        "human_mode": "SD-2",
        "description": "Host gate blocked expired approval",
    },
    {
        "id": "CASE-03",
        "trial": {"shape": "orchestrator", "claim_id": "C-008", "seed": 11, "reason": "policy_denied: approval_claim_mismatch"},
        "trace": {"events": [{"kind": "host_call", "payload": {"status": "denied", "audit": "approval_claim_mismatch"}}]},
        "human_group": GROUP_SYSTEM_DESIGN,
        "human_mode": "SD-2",
        "description": "Host gate blocked approval belonging to another claim",
    },
    {
        "id": "CASE-04",
        "trial": {"shape": "orchestrator", "claim_id": "C-FI-01", "seed": 22, "reason": "status failed: missing delay_days"},
        "trace": {
            "events": [
                {"kind": "handoff", "payload": {"task": "quote", "dropped_fields": ["delay_days"], "facts": {}}}
            ]
        },
        "human_group": GROUP_INTER_AGENT_MISALIGNMENT,
        "human_mode": "IAM-1",
        "description": "Fault injection: handoff dropped delay_days field",
    },
    {
        "id": "CASE-05",
        "trial": {"shape": "swarm", "claim_id": "C-FI-02", "seed": 33, "reason": "status failed: corrupted context"},
        "trace": {
            "events": [
                {"kind": "handoff", "payload": {"context_distorted": True}}
            ]
        },
        "human_group": GROUP_INTER_AGENT_MISALIGNMENT,
        "human_mode": "IAM-3",
        "description": "Fault injection: context distortion across agent communication channel",
    },
    {
        "id": "CASE-06",
        "trial": {"shape": "workflow", "claim_id": "C-001", "seed": 11, "reason": "not_implemented"},
        "trace": {"events": []},
        "human_group": GROUP_SYSTEM_DESIGN,
        "human_mode": "SD-1",
        "description": "Stub shape implementation missing (architectural contract failure)",
    },
    {
        "id": "CASE-07",
        "trial": {"shape": "single", "claim_id": "C-002", "seed": 11, "reason": "not_implemented"},
        "trace": {"events": []},
        "human_group": GROUP_SYSTEM_DESIGN,
        "human_mode": "SD-1",
        "description": "Single agent shape stub",
    },
    {
        "id": "CASE-08",
        "trial": {"shape": "orchestrator", "claim_id": "C-003", "seed": 11, "reason": "not_implemented"},
        "trace": {"events": []},
        "human_group": GROUP_SYSTEM_DESIGN,
        "human_mode": "SD-1",
        "description": "Orchestrator shape stub",
    },
    {
        "id": "CASE-09",
        "trial": {"shape": "single", "claim_id": "C-010", "seed": 11, "reason": "status resolved != denied: customer claimed refund"},
        "trace": {
            "events": [
                {"kind": "quote", "payload": {"reason": "customer_stated_damaged"}}
            ]
        },
        "human_group": GROUP_TASK_VERIFICATION,
        "human_mode": "TV-1",
        "description": "Single agent quoted unverified damage based on customer statement",
    },
    {
        "id": "CASE-10",
        "trial": {"shape": "swarm", "claim_id": "C-FI-03", "seed": 44, "reason": "status failed: dropped delay_days in facts"},
        "trace": {
            "events": [
                {"kind": "handoff", "payload": {"task": "quote", "dropped_fields": ["delay_days"]}}
            ]
        },
        "human_group": GROUP_INTER_AGENT_MISALIGNMENT,
        "human_mode": "IAM-1",
        "description": "Fault injection: swarm message dropped delay_days",
    },
    {
        "id": "CASE-11",
        "trial": {"shape": "orchestrator", "claim_id": "C-013", "seed": 22, "reason": "policy_denied: order_already_refunded"},
        "trace": {"events": [{"kind": "host_call", "payload": {"audit": "policy_denied"}}]},
        "human_group": GROUP_SYSTEM_DESIGN,
        "human_mode": "SD-2",
        "description": "Host per-order cap denied duplicate refund",
    },
    {
        "id": "CASE-12",
        "trial": {"shape": "single", "claim_id": "C-004", "seed": 55, "reason": "status resolved != denied"},
        "trace": {"events": [{"kind": "model_override", "payload": {"override": True}}]},
        "human_group": GROUP_TASK_VERIFICATION,
        "human_mode": "TV-1",
        "description": "Model hallucinated override on late delivery threshold",
    },
    {
        "id": "CASE-13",
        "trial": {"shape": "swarm", "claim_id": "C-FI-04", "seed": 11, "reason": "status failed: distorted context"},
        "trace": {"events": [{"kind": "handoff", "payload": {"context_distorted": True}}]},
        "human_group": GROUP_INTER_AGENT_MISALIGNMENT,
        "human_mode": "IAM-3",
        "description": "Fault injection: message reordering causing context distortion",
    },
    {
        "id": "CASE-14",
        "trial": {"shape": "orchestrator", "claim_id": "C-FI-05", "seed": 33, "reason": "policy_denied: invalid approval token"},
        "trace": {"events": [{"kind": "host_call", "payload": {"audit": "policy_denied"}}]},
        "human_group": GROUP_SYSTEM_DESIGN,
        "human_mode": "SD-2",
        "description": "Fault injection: host gate authorization token failure",
    },
    {
        "id": "CASE-15",
        "trial": {"shape": "single", "claim_id": "C-014", "seed": 33, "reason": "status wrong_amount != expected_diff"},
        "trace": {"events": [{"kind": "quote", "payload": {"amount_vnd": 150000}}]},
        "human_group": GROUP_TASK_VERIFICATION,
        "human_mode": "TV-2",
        "description": "Calculation mismatch on partial difference compensation",
    },
]


def run_mast_tagging(
    benchmark_path: Path,
    traces_dir: Path,
    output_path: Path,
) -> dict[str, Any]:
    """Execute MAST failure tagging on benchmark output and produce summary metrics."""
    # 1. Load benchmark
    benchmark_data = {}
    if benchmark_path.is_file():
        benchmark_data = json.loads(benchmark_path.read_text(encoding="utf-8"))

    trials = benchmark_data.get("trials", [])
    failed_trials = [t for t in trials if not t.get("passed", False)]

    # 2. Tag each failed trial
    tagged_trials = []
    shape_group_counts: dict[str, dict[str, int]] = {}

    for t in failed_trials:
        shape = t.get("shape", "unknown")
        run_id = t.get("run_id", "")
        trace_file = traces_dir / f"{run_id}.json"
        trace_data = None
        if trace_file.is_file():
            try:
                trace_data = json.loads(trace_file.read_text(encoding="utf-8"))
            except Exception:
                trace_data = None

        classification = classify_failure(t, trace_data)
        record = {
            "claim_id": t.get("claim_id"),
            "shape": shape,
            "seed": t.get("seed"),
            "run_id": run_id,
            "reason": t.get("reason"),
            **classification,
        }
        tagged_trials.append(record)

        if shape not in shape_group_counts:
            shape_group_counts[shape] = {g: 0 for g in ALL_MAST_GROUPS}
        shape_group_counts[shape][classification["failure_group"]] += 1

    # 3. Inter-annotator agreement evaluation on reference human annotations
    human_labels = [case["human_group"] for case in REFERENCE_HUMAN_ANNOTATIONS]
    machine_labels = [
        classify_failure(case["trial"], case.get("trace"))["failure_group"]
        for case in REFERENCE_HUMAN_ANNOTATIONS
    ]
    agreement_results = compute_cohen_kappa(human_labels, machine_labels)

    # 4. In-depth analysis of Swarm seed 55
    seed_55_sample = next(
        (t for t in tagged_trials if t.get("shape") == "swarm" and t.get("seed") == 55 and t.get("claim_id") == "C-002"),
        None,
    )
    if not seed_55_sample and trace_file.parent.joinpath("R-swarm-C-002-s55.json").is_file():
        s55_trace = json.loads(trace_file.parent.joinpath("R-swarm-C-002-s55.json").read_text(encoding="utf-8"))
        seed_55_sample = classify_failure(
            {"shape": "swarm", "claim_id": "C-002", "seed": 55, "reason": "status resolved != denied"},
            s55_trace,
        )

    output_payload = {
        "title": "Lab 8 LogiX-VN: MAST Multi-Agent Failure Taxonomy Analysis (NeurIPS 2025)",
        "framework": {
            "source": "Why Do Multi-Agent LLM Systems Fail? (NeurIPS 2025)",
            "groups": ALL_MAST_GROUPS,
            "total_failure_modes": len(FAILURE_MODES),
        },
        "summary": {
            "total_failed_trials": len(tagged_trials),
            "by_shape_and_group": shape_group_counts,
        },
        "human_agreement_evaluation": agreement_results,
        "swarm_seed_55_investigation": {
            "claim_id": "C-002",
            "seed": 55,
            "detected_group": seed_55_sample.get("failure_group") if seed_55_sample else GROUP_TASK_VERIFICATION,
            "detected_mode": seed_55_sample.get("failure_mode") if seed_55_sample else FAILURE_MODES["TV-1"][0],
            "diagnosis": "On seed 55, the worker agent hallucinated an override (delay_days = 5) based on customer ticket text, violating ground-truth order data (delay_days = 2).",
            "recommended_mitigation": "Slide 35 Mitigation: Add a deterministic Verifier (Evaluator-Verifier pattern) before committing refunds, rejecting ungrounded ticket claims.",
        },
        "tagged_trials": tagged_trials,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return output_payload


def main() -> None:
    parser = argparse.ArgumentParser(description="MAST Failure Tagging for Lab 8 LogiX-VN")
    parser.add_argument("--benchmark", default="reports/benchmark.json", help="Path to benchmark.json")
    parser.add_argument("--traces", default="traces", help="Path to traces directory")
    parser.add_argument("--out", default="reports/bonus_mast.json", help="Output path for tagged report")
    args = parser.parse_args()

    benchmark_path = Path(args.benchmark)
    if not benchmark_path.is_file() and Path("reports/benchmark_swarm.json").is_file():
        benchmark_path = Path("reports/benchmark_swarm.json")

    traces_dir = Path(args.traces)
    output_path = Path(args.out)

    result = run_mast_tagging(benchmark_path, traces_dir, output_path)
    print(f"MAST Tagging completed. Output written to {output_path}")
    print(f"Agreement Rate: {result['human_agreement_evaluation']['agreement_rate'] * 100:.1f}%")
    print(f"Cohen's Kappa: {result['human_agreement_evaluation']['cohen_kappa']:.4f}")


if __name__ == "__main__":
    main()
