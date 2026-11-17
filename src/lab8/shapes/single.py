"""Shape B — one ReAct agent. Student work.

Use `lab8.runtime.run_react` with max_steps=8. `decide` may pick a read tool.
It must not call `issue_refund`. After the loop, the host validates the quote
and is the only writer.

A decide() that trusts ticket text over the order row will fail hidden claims
where the customer overstates the delay or cites a superseded clause.

Per-order cap: an order may already have been refunded by an earlier claim.
The read tool `lookup_refund_history` shows how much. The host still enforces
the cap, so pass the full quote to `durability.issue_refund`, not a net amount.

Caps: stop at 8 steps. Count model calls in the Budget so cost stays comparable.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.mock_llm import complete
from lab8.runtime import run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.trace import Trace

SHAPE = "single"
MAX_STEPS = 8


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    # Mở DB một lần, luôn đóng trong finally (tránh WinError 32 trên Windows).
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at)
    finally:
        conn.close()


def _run(conn: sqlite3.Connection, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id(SHAPE, claim_id, seed))
    # run_react chỉ đưa cho decide() kết quả của tool VỪA gọi, nên agent tự giữ "trí nhớ".
    # Code (không phải model) sẽ đọc số tiền từ đây sau vòng lặp.
    memory: dict[str, Any] = {}

    def done(status: str, proposal: int, reason: str | None) -> RunResult:
        """Mọi nhánh kết thúc đều đi qua đây: soạn thư (model), ghi trace, trả RunResult."""
        complete(budget, seed=seed, purpose="draft", prompt=f"status={status}")
        trace.add("decision", {"status": status, "proposal_amount": int(proposal), "reason": reason})
        return finish(
            conn,
            shape=SHAPE,
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=reason,
        )

    def decide(seen: dict[str, Any]) -> dict[str, Any]:
        """Một bước 'suy nghĩ' của agent: 1 lần gọi MockLLM, rồi chọn TOOL ĐỌC tiếp theo hoặc dừng.

        Agent chỉ chọn tên tool. Không bao giờ dùng chữ trong ticket làm dữ kiện hay số tiền.
        """
        if "last_tool" in seen:
            memory[seen["last_tool"]] = seen["last_result"]
            trace.add("observe", _trace_view(seen["last_tool"], seen["last_result"]))
        step = sum(1 for event in trace.events if event["kind"] == "think")
        complete(budget, seed=seed, purpose="think", prompt=f"step={step}|have={sorted(memory)}")
        trace.add("think", {"step": step, "have": sorted(memory)})

        claim = memory.get("get_claim_view")
        if claim is None:
            return {"tool": "get_claim_view", "args": {"claim_id": claim_id}}
        if not claim.get("found"):
            return {"final": {"status": "failed", "reason": "unknown_claim"}}
        if not claim.get("order_id"):
            return {"final": {"status": "needs_info", "reason": "missing_order_id"}}

        scope = {"order_id": claim["order_id"], "principal_id": claim["principal_id"]}
        order_view = memory.get("lookup_order")
        if order_view is None:
            return {"tool": "lookup_order", "args": scope}
        if not order_view.get("visible"):
            return {"final": {"status": "escalated", "reason": order_view.get("reason")}}
        if "lookup_refund_history" not in memory:
            return {"tool": "lookup_refund_history", "args": scope}
        if "compute_compensation" not in memory:
            # Tính tiền từ order row trong DB, KHÔNG từ số ngày khách viết trong ticket.
            return {"tool": "compute_compensation", "args": {"order": order_view["order"]}}
        return {"final": {"status": "ready_to_commit"}}

    loop = run_react(
        conn,
        budget,
        observation={"claim": {"claim_id": claim_id}},
        decide=decide,
        max_steps=MAX_STEPS,
    )
    final = loop["final"]
    trace.add("loop", {"stopped": loop["stopped"], "final_status": final.get("status")})

    if loop["stopped"] != "final":
        return done("failed", 0, final.get("error_reason", "step_cap"))
    if final["status"] != "ready_to_commit":
        return done(final["status"], 0, final.get("reason"))

    # Sau vòng lặp: CODE lấy số tiền từ compute_compensation, model không được chọn số.
    quote = memory["compute_compensation"]
    proposal = int(quote["amount_vnd"])
    if proposal <= 0:
        return done("denied", 0, quote.get("reason"))

    # Host là người ghi duy nhất. Truyền QUOTE ĐẦY ĐỦ, host tự trừ phần đã hoàn (T13, T14).
    # CP3: truyền crash_at cho host. Bắt InjectedCrash CHỈ để ghi trace, rồi raise lại (không nuốt).
    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise
    trace.add("host", {"ok": outcome["ok"], "reason": outcome["reason"], "conflict": outcome["conflict"]})

    if not outcome["ok"]:
        return done("failed" if outcome["conflict"] else "denied", proposal, outcome["reason"])
    return done("resolved", proposal, None)


def _trace_view(tool: str, result: dict[str, Any]) -> dict[str, Any]:
    """Phần được phép ghi vào trace từ kết quả tool. Ticket, principal_id, nội dung policy bị loại."""
    if tool == "get_claim_view":
        return {"tool": tool, "found": result.get("found"), "has_order_id": bool(result.get("order_id"))}
    if tool == "lookup_order":
        # lookup_order đã lọc còn 7 field an toàn (không SĐT, địa chỉ, tên hàng, ghi chú nội bộ).
        return {"tool": tool, **safe_dump({k: result[k] for k in ("visible", "reason", "order") if k in result})}
    if tool == "lookup_refund_history":
        return {"tool": tool, **{k: result.get(k) for k in ("visible", "refund_count", "refunded_vnd")}}
    if tool == "compute_compensation":
        return {"tool": tool, **safe_dump(result)}
    return {"tool": tool}
