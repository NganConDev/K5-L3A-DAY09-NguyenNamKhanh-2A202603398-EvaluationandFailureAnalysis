"""Shape B — one ReAct agent.

Signature (do not change):

    run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult
"""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.mock_llm import complete
from lab8.runtime import run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import get_claim_view, tool_cost
from lab8.trace import Trace


class _Trace:
    """Local alias so a crash can still flush."""

    def __init__(self, run_id: str) -> None:
        self._inner = Trace(run_id)

    def add(self, kind: str, payload: dict) -> None:
        self._inner.add(kind, payload)

    def write(self) -> str:
        return self._inner.write()

    @property
    def run_id(self) -> str:
        return self._inner.run_id


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at)
    finally:
        conn.close()


def _run(conn: sqlite3.Connection, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    budget = Budget()
    run_id = make_run_id("single", claim_id, seed)
    trace = _Trace(run_id)

    claim_view = get_claim_view(conn, claim_id)
    budget.add_tool(tool_cost())
    if not claim_view.get("found"):
        trace.add("error", {"reason": "unknown_claim"})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="failed",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason="unknown_claim",
        )

    ticket = claim_view.get("ticket", "")
    complete(budget, seed=seed, purpose="react_plan", prompt=ticket)

    def decide(seen: dict[str, Any]) -> dict[str, Any]:
        last_tool = seen.get("last_tool")
        if last_tool is None:
            if not claim_view.get("order_id"):
                return {"final": {"status": "needs_info", "error_reason": "missing_order_id"}}
            return {
                "tool": "lookup_order",
                "args": {
                    "order_id": claim_view["order_id"],
                    "principal_id": claim_view["principal_id"],
                },
            }
        if last_tool == "lookup_order":
            order_view = seen["last_result"]
            trace.add("lookup_order", {"visible": order_view.get("visible"), "reason": order_view.get("reason")})
            if not order_view.get("visible"):
                return {"final": {"status": "escalated", "error_reason": order_view.get("reason")}}
            return {
                "tool": "compute_compensation",
                "args": {"order": order_view["order"]},
            }
        if last_tool == "compute_compensation":
            quote_payload = seen["last_result"]
            trace.add("quote", quote_payload)
            return {"final": {"status": "ready_to_pay", "quote": quote_payload}}
        return {"final": {"status": "failed", "error_reason": "unexpected_react_state"}}

    react_result = run_react(
        conn,
        budget,
        observation={"claim": claim_view},
        decide=decide,
        max_steps=8,
        worker=False,
    )

    final = react_result.get("final") or {}
    status = final.get("status")

    if status == "needs_info":
        trace.add("decision", {"status": "needs_info"})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="needs_info",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason="missing_order_id",
        )

    if status == "escalated":
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="escalated",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=final.get("error_reason"),
        )

    if status != "ready_to_pay":
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="failed",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=final.get("error_reason", "react_failure"),
        )

    quote_payload = final["quote"]
    proposal = int(quote_payload["amount_vnd"])

    if proposal <= 0:
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="denied",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=quote_payload.get("reason"),
        )

    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise

    if not outcome["ok"]:
        st = "failed" if outcome["conflict"] else "denied"
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status=st,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=outcome["reason"],
        )

    return finish(
        conn,
        shape="single",
        claim_id=claim_id,
        seed=seed,
        status="resolved",
        proposal_amount=proposal,
        budget=budget,
        trace=trace,
        error_reason=None,
    )
