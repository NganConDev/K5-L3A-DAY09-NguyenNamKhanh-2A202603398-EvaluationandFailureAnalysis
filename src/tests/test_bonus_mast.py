"""Unit tests for Bonus Topic B2: Automated MAST Failure Tagging."""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from bonus.mast_tag import (
    GROUP_INTER_AGENT_MISALIGNMENT,
    GROUP_SYSTEM_DESIGN,
    GROUP_TASK_VERIFICATION,
    classify_failure,
    compute_cohen_kappa,
    run_mast_tagging,
)


def _src_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def test_fault_injection_inter_agent_misalignment():
    """Biến thể 1: Handoff làm rơi thông tin delay_days giữa các agent."""
    trial = {"shape": "orchestrator", "claim_id": "C-TEST-01", "reason": "status failed: missing delay_days"}
    trace = {
        "events": [
            {
                "kind": "handoff",
                "payload": {
                    "task": "quote",
                    "dropped_fields": ["delay_days"],
                    "facts": {"order_id": "O-100"},
                },
            }
        ]
    }
    result = classify_failure(trial, trace)
    assert result["failure_group"] == GROUP_INTER_AGENT_MISALIGNMENT
    assert result["failure_mode_id"] == "IAM-1"
    assert "dropped during handoff" in result["rationale"]


def test_fault_injection_system_design_approval_mismatch():
    """Biến thể 2: Host gate từ chối do approval của claim khác hoặc thiếu quyền."""
    trial = {
        "shape": "orchestrator",
        "claim_id": "C-TEST-02",
        "reason": "policy_denied: approval_claim_mismatch",
    }
    trace = {
        "events": [
            {
                "kind": "host_call",
                "payload": {"status": "denied", "audit": "policy_denied"},
            }
        ]
    }
    result = classify_failure(trial, trace)
    assert result["failure_group"] == GROUP_SYSTEM_DESIGN
    assert result["failure_mode_id"] == "SD-2"
    assert "approval" in result["rationale"]


def test_fault_injection_task_verification_grounding_override():
    """Biến thể 3: Model override giá trị thực tế của order bằng text của khách hàng."""
    trial = {"shape": "single", "claim_id": "C-TEST-03", "reason": "status resolved != denied"}
    trace = {
        "events": [
            {"kind": "investigator", "payload": {"order": {"delay_days": 1}}},
            {"kind": "model_override", "payload": {"delay_days": 7}},
        ]
    }
    result = classify_failure(trial, trace)
    assert result["failure_group"] == GROUP_TASK_VERIFICATION
    assert result["failure_mode_id"] == "TV-1"
    assert "model_override" in result["rationale"]


def test_swarm_seed_55_real_trace_classification():
    """Xác minh ca thất bại thực tế của Swarm ở seed 55 trên claim C-002."""
    trace_path = _src_dir() / "traces" / "R-swarm-C-002-s55.json"
    if not trace_path.is_file():
        pytest.skip("Trace R-swarm-C-002-s55.json not present in test run")

    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    trial = {
        "shape": "swarm",
        "claim_id": "C-002",
        "seed": 55,
        "reason": "status resolved != denied",
    }
    result = classify_failure(trial, trace)
    assert result["failure_group"] == GROUP_TASK_VERIFICATION
    assert result["failure_mode_id"] == "TV-1"
    assert "model_override" in result["rationale"]


def test_cohen_kappa_computation_mathematics():
    """Kiểm tra tính chính xác của thuật toán tính hệ số Cohen's Kappa."""
    # 1. Trùng khớp hoàn toàn -> Kappa = 1.0
    labels_a = ["A", "B", "C", "A", "B"]
    labels_b = ["A", "B", "C", "A", "B"]
    res_perfect = compute_cohen_kappa(labels_a, labels_b)
    assert res_perfect["cohen_kappa"] == 1.0
    assert res_perfect["agreement_rate"] == 1.0

    # 2. Bất đồng một phần -> 0 < Kappa < 1.0
    labels_c = ["A", "B", "C", "A", "A"]  # 1 mismatch
    res_partial = compute_cohen_kappa(labels_a, labels_c)
    assert 0.0 < res_partial["cohen_kappa"] < 1.0
    assert res_partial["agreement_rate"] == 0.8


def test_end_to_end_mast_tagging(tmp_path):
    """Kiểm tra quy trình chạy end-to-end sinh báo cáo JSON hợp lệ."""
    bench_file = _src_dir() / "reports" / "benchmark_swarm.json"
    if not bench_file.is_file():
        pytest.skip("Benchmark swarm not yet run")

    out_file = tmp_path / "bonus_mast_test.json"
    output = run_mast_tagging(bench_file, _src_dir() / "traces", out_file)
    assert out_file.is_file()
    assert "human_agreement_evaluation" in output
    assert output["human_agreement_evaluation"]["n"] >= 15
    assert output["human_agreement_evaluation"]["cohen_kappa"] >= 0.80
