"""Shape A — deterministic workflow. Student work.

Signature (do not change):

    run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult

Suggested steps. Money stays in code (`lab8.tools.compute_compensation`).

1. Open the store. Read the claim through `get_claim_view` (not SELECT *).
2. Missing order_id -> status `needs_info`. Do not write the ledger.
3. `lookup_order`. If not visible -> `escalated`. Do not copy phone, address, item, internal note.
4. Quote from the order row. Ignore delay numbers written in the ticket.
5. Quote amount 0 -> `denied`. Do not call issue_refund.
6. Quote amount > 0 -> `durability.issue_refund(conn, claim_id, <full quote>)`.
   Pass the FULL quote. The host checks the claim's own approval and subtracts
   what earlier claims already got for the same order (T13, T14). Do not
   subtract it yourself or the host subtracts twice.
   Auth failure or order already refunded -> `denied` (the host writes `policy_denied`).
   `proposal_amount` stays the full quote. Amount conflict -> `failed`.
7. Success -> `resolved`. One ledger row, one `refund_committed` audit.
8. Use MockLLM only to draft the reply text, if you want a model call at all.

The model must not choose the refund amount and must not commit the refund.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

from lab8.db import connect
from lab8.durability import issue_refund
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import compute_compensation, get_claim_view, lookup_order, tool_cost
from lab8.trace import Trace


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    # Open the database for this run and always close it before returning or raising.
    conn = connect(store_path)
    try:
        # Track simulated tool usage and create one stable ID for the result and trace.
        budget = Budget()
        run_id = make_run_id("workflow", claim_id, seed)
        trace = Trace(run_id)

        # Read only the claim fields needed by this workflow; never log the raw ticket.
        budget.add_tool(tool_cost())
        claim = get_claim_view(conn, claim_id)
        if not claim["found"]:
            # An unknown claim cannot be processed, so return a traced failure.
            trace.add("error", {"reason": "unknown_claim"})
            return finish(
                conn,
                shape="workflow",
                claim_id=claim_id,
                seed=seed,
                status="failed",
                proposal_amount=0,
                budget=budget,
                trace=trace,
                error_reason="unknown_claim",
            )

        # A claim without an order needs more information and must not reach the ledger.
        if not claim["order_id"]:
            trace.add("decision", {"status": "needs_info"})
            return finish(
                conn,
                shape="workflow",
                claim_id=claim_id,
                seed=seed,
                status="needs_info",
                proposal_amount=0,
                budget=budget,
                trace=trace,
                error_reason="missing_order_id",
            )

        # Look up the order within the claimant's scope to avoid exposing another user's data.
        budget.add_tool(tool_cost())
        order_view = lookup_order(conn, claim["order_id"], claim["principal_id"])
        if not order_view["visible"]:
            # Escalate when the order is absent or outside this claimant's scope.
            reason = order_view["reason"]
            trace.add("decision", {"status": "escalated", "reason": reason})
            return finish(
                conn,
                shape="workflow",
                claim_id=claim_id,
                seed=seed,
                status="escalated",
                proposal_amount=0,
                budget=budget,
                trace=trace,
                error_reason=reason,
            )

        # Calculate compensation from trusted order data and current policy, not ticket text.
        order = order_view["order"]
        budget.add_tool(tool_cost())
        quote = compute_compensation(conn, order)
        proposal = int(quote["amount_vnd"])
        trace.add("quote", quote)

        # A zero-value quote is a denial; do not ask the host to create a refund.
        if proposal <= 0:
            return finish(
                conn,
                shape="workflow",
                claim_id=claim_id,
                seed=seed,
                status="denied",
                proposal_amount=0,
                budget=budget,
                trace=trace,
                error_reason=quote.get("reason"),
            )

        # The host validates approval and order limits, then commits the full quote idempotently.
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
        if not outcome["ok"]:
            # Conflicting retries are failures; authorization and policy rejections are denials.
            status = "failed" if outcome["conflict"] else "denied"
            return finish(
                conn,
                shape="workflow",
                claim_id=claim_id,
                seed=seed,
                status=status,
                proposal_amount=proposal,
                budget=budget,
                trace=trace,
                error_reason=outcome["reason"],
            )

        # Report success; finish reads the committed refund and audit count into RunResult.
        return finish(
            conn,
            shape="workflow",
            claim_id=claim_id,
            seed=seed,
            status="resolved",
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
        )
    finally:
        conn.close()
