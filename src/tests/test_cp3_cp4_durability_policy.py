"""Tests for CP3 (Durability, Idempotency, Crash Safety) and CP4 (Policy, Approvals, Audit)."""

import pytest

from lab8.config_loader import as_of
from lab8.db import connect
from lab8.durability import (
    InjectedCrash,
    committed_audit_count,
    get_refund,
    issue_refund,
)
from lab8.policy import authorize, order_refunded_vnd


def _add_claim(conn, claim_id, order_id, approval_id, *, principal="P-100"):
    conn.execute(
        """
        INSERT INTO claims (claim_id, principal_id, order_id, ticket, parent_secret, raw_headers_json, approval_id)
        VALUES (?, ?, ?, 'test claim', 'CANARY_SECRET_PARENT_TEST', '{}', ?)
        """,
        (claim_id, principal, order_id, approval_id),
    )


def _add_approval(conn, approval_id, claim_id, amount, status="valid", expires="2027-12-31"):
    conn.execute(
        "INSERT INTO approvals (approval_id, claim_id, approved_vnd, status, expires_at) VALUES (?, ?, ?, ?, ?)",
        (approval_id, claim_id, amount, status, expires),
    )


def _denials(conn, claim_id):
    rows = conn.execute(
        "SELECT details_json FROM audit_events WHERE claim_id = ? AND event_type = 'policy_denied'",
        (claim_id,),
    ).fetchall()
    return [row["details_json"] for row in rows]


def test_crash_before_effect_leaves_zero_rows_and_resumes_safely(public_db):
    conn = connect(public_db)
    crashed = False
    try:
        issue_refund(conn, "C-001", 35000, crash_at="before_effect")
    except InjectedCrash:
        crashed = True
    assert crashed is True
    assert get_refund(conn, "C-001") is None
    assert committed_audit_count(conn, "C-001") == 0

    # Resume without crash
    resumed = issue_refund(conn, "C-001", 35000, crash_at=None)
    assert resumed["ok"] is True
    assert resumed["reason"] == "committed"
    assert int(get_refund(conn, "C-001")["amount_vnd"]) == 35000
    assert committed_audit_count(conn, "C-001") == 1
    conn.close()


def test_crash_after_checkpoint_resumes_as_idempotent_replay(public_db):
    conn = connect(public_db)
    crashed = False
    try:
        issue_refund(conn, "C-001", 35000, crash_at="after_checkpoint")
    except InjectedCrash:
        crashed = True
    assert crashed is True
    assert get_refund(conn, "C-001") is not None
    assert committed_audit_count(conn, "C-001") == 1

    # Resume
    resumed = issue_refund(conn, "C-001", 35000, crash_at=None)
    assert resumed["ok"] is True
    assert resumed["reason"] == "idempotent_replay"
    assert committed_audit_count(conn, "C-001") == 1
    conn.close()


def test_approval_status_pending_and_rejected_are_denied(public_db):
    conn = connect(public_db)
    _add_approval(conn, "A-PENDING", "C-PEND", 35000, status="pending")
    _add_claim(conn, "C-PEND", "O-107", "A-PENDING")

    _add_approval(conn, "A-REJECTED", "C-REJ", 35000, status="rejected")
    _add_claim(conn, "C-REJ", "O-107", "A-REJECTED")
    conn.commit()

    pending_outcome = issue_refund(conn, "C-PEND", 35000)
    rejected_outcome = issue_refund(conn, "C-REJ", 35000)

    assert pending_outcome["ok"] is False
    assert pending_outcome["reason"] == "approval_pending"
    assert get_refund(conn, "C-PEND") is None

    assert rejected_outcome["ok"] is False
    assert rejected_outcome["reason"] == "approval_rejected"
    assert get_refund(conn, "C-REJ") is None

    assert any("approval_pending" in r for r in _denials(conn, "C-PEND"))
    assert any("approval_rejected" in r for r in _denials(conn, "C-REJ"))
    conn.close()


def test_approval_zero_or_negative_amount_denied(public_db):
    conn = connect(public_db)
    _add_approval(conn, "A-ZERO", "C-ZERO", 0)
    _add_claim(conn, "C-ZERO", "O-107", "A-ZERO")
    conn.commit()

    outcome = issue_refund(conn, "C-ZERO", 35000)
    assert outcome["ok"] is False
    assert outcome["reason"] == "non_positive_amount"
    assert get_refund(conn, "C-ZERO") is None
    assert any("non_positive_amount" in r for r in _denials(conn, "C-ZERO"))
    conn.close()


def test_approval_expiry_exact_today_vs_yesterday(public_db):
    conn = connect(public_db)
    today = as_of()  # "2026-11-15"

    _add_approval(conn, "A-TODAY", "C-TODAY", 35000, expires=today)
    _add_claim(conn, "C-TODAY", "O-107", "A-TODAY")

    _add_approval(conn, "A-YESTERDAY", "C-YESTERDAY", 35000, expires="2026-11-14")
    _add_claim(conn, "C-YESTERDAY", "O-107", "A-YESTERDAY")
    conn.commit()

    # Exact today is NOT < today, so it should be valid
    today_dec = authorize(conn, "C-TODAY", 35000, paid_vnd=250000)
    assert today_dec.ok is True

    # Yesterday is < today, so expired
    yesterday_dec = authorize(conn, "C-YESTERDAY", 35000, paid_vnd=250000)
    assert yesterday_dec.ok is False
    assert yesterday_dec.reason == "approval_expired"
    conn.close()


def test_conflict_does_not_overwrite_original_ledger_amount(public_db):
    conn = connect(public_db)
    # First commit 35,000
    first = issue_refund(conn, "C-001", 35000)
    assert first["ok"] is True
    assert first["reason"] == "committed"

    # Try replay with 10,000 (different authorized amount)
    conflicting = issue_refund(conn, "C-001", 10000)
    assert conflicting["ok"] is False
    assert conflicting["conflict"] is True
    assert conflicting["reason"] == "amount_conflict"

    # Ledger remains at 35,000
    effect = get_refund(conn, "C-001")
    assert int(effect["amount_vnd"]) == 35000
    assert committed_audit_count(conn, "C-001") == 1

    # Conflict audit event recorded
    conflict_audits = conn.execute(
        "SELECT details_json FROM audit_events WHERE claim_id = 'C-001' AND event_type = 'amount_conflict'"
    ).fetchall()
    assert len(conflict_audits) == 1
    assert "10000" in conflict_audits[0]["details_json"]
    conn.close()
