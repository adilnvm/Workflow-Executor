<!-- this is /docs/inavriants.md -->


# System Invariants — Workflow Executor

### Invariants = things that must never break, regardless of LLM quality.

These invariants must NEVER be violated, regardless of LLM behavior,
model choice, or user input.

---

## Invariant 1 — Workflow execution requires complete slots

A workflow MUST NOT execute unless all required slots are present.
LLM confidence is advisory and must not override missing slots.

---

## Invariant 2 — Every intent maps to exactly one workflow

If intent ≠ "unknown", it must deterministically map to a single workflow.
No ambiguity or guessing is allowed.

---

## Invariant 3 — LLM output is never trusted directly

All LLM outputs must pass through:
- schema validation
- default filling
- safety fallback

Malformed or partial output must not propagate.

---

## Invariant 4 — Stable facts must never be overwritten

Stable facts (e.g. service_type, account_type, device_type, region)
must not be overridden by inference or later guesses.

User-provided facts always win.

---

## Invariant 5 — Inference must be reversible

Any inferred fact must be removable without breaking the session.
Inference must never be required for correctness.

---

## Invariant 6 — Confidence does not control execution alone

Execution depends on:
- slot completeness
- workflow rules
- invariants

High confidence must not bypass missing data.

---

## Invariant 7 — Tickets must degrade gracefully

If a ticket_id is missing or lost:
- start a new session
- explain politely
- never throw a server error

Memory loss must degrade UX, not correctness.

---

## Invariant 8 — Agent must be LLM-agnostic

Agent logic must not depend on which LLM is active.
Mock, local, or cloud models must behave identically.

---

## Invariant 9 — Clarification must reduce uncertainty

Every clarification must fill at least one required slot.
Clarifications that do not reduce missing slots are invalid.

---

## Invariant 10 — Workflow execution must be deterministic

Given the same workflow and context,
execution must always return the same result.

---

## Invariant 11 — Fact priority order is strict

1. Explicit user input
2. Conversation history
3. Inferred assumptions

This order must never be violated.

---

## Invariant 12 — The system must never invent facts

Unknown values must remain "unknown".
The system must ask or block — never guess.

---





