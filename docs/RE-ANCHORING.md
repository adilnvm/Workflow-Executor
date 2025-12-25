# Re-Anchoring the Product: Deviation Analysis & Refactor Plan

## Purpose of This Document

This document exists to:

- Explicitly acknowledge where we deviated from the original product intent
- Explain *why* the system failed to behave like a real support system
- Document how over-engineering obscured core behavior
- Define a clear, non-destructive refactor path back to correctness

This is not a postmortem for a bug.
This is a **product and architecture course-correction**.

---

## Original Product Intent (What We Meant to Build)

The original goal was clear:

> Build a **telecom support decision engine** that behaves like a real customer support system — not a chatbot.

Core expectations:

- Correctly identify user intent
- Act immediately when execution is possible
- Ask only execution-blocking questions
- Run deterministic troubleshooting workflows
- Preserve state across turns and restarts
- Escalate cleanly when automation stops adding value

The system was meant to feel like a **competent Tier-1 telecom agent**, not a conversational assistant.

---

## What Went Wrong (High-Level)

At some point, the system stopped behaving like a decision engine and started behaving like:

- A form-filling system
- A clarification-first chatbot
- A validation-heavy pipeline

As a result:

- Intent was identified but not trusted
- Execution was blocked unnecessarily
- The system entered clarification loops
- Core behavior became difficult to reason about
- Debugging became cognitively exhausting

This was not caused by one bad decision, but by **compounding architectural drift**.

---

## Deviation #1 — Intent Lost Its Authority

### What Happened

Intent was treated as *advisory*, not authoritative.

The system allowed logic equivalent to:

> “Even if intent is known, we still need to confirm issue_type.”

This introduced a contradiction:
- Intent *was* already the issue classification
- Yet the system asked for it again

### Impact

- Failure to confidently classify intent
- Infinite clarification loops
- LLM decisions being ignored by downstream logic
- User frustration due to repeated questions

### Core Insight

> **Intent IS the issue type.**
> Once intent is clear, it must never be re-requested.

---

## Deviation #2 — Slot System Turned Into Validation

### What Slots Were Meant To Be

Slots were meant to answer one question only:

> **“Can we execute the workflow right now?”**

### What They Became

Slots drifted into:

- A completeness checklist
- A schema validator
- A form-like data collection mechanism

Instead of asking:
> “What is the minimum data needed to act?”

The system started asking:
> “Is everything filled?”

### Impact

- Execution was blocked unnecessarily
- Clarifications stopped advancing state
- The system optimized for *completeness*, not *resolution*

This is a **form mindset**, not a support mindset.

---

## Deviation #3 — Over-Engineering Before Behavior Was Stable

### What Was Added Too Early

Before core behavior was fully correct, we added:

- Inference engine
- Rollback mechanisms
- Observability framework
- Redis persistence
- Multi-LLM fallback logic

Each of these is individually valid.

### The Problem

They were added **before** locking:

- Intent authority
- Slot philosophy
- Execution guarantees

### Impact

- The system became harder to reason about
- Bugs were difficult to localize
- Emotional and cognitive load increased during debugging
- Symptoms were treated before the disease was understood

This was a sequencing problem, not a competence problem.

---

## Deviation #4 — Letting LLM Behavior Override Architecture

### What Happened

The system began trusting:

- LLM confidence scores
- LLM-driven clarification decisions

Instead of enforcing **hard architectural invariants**.

### Why This Is Dangerous

LLMs are:
- Probabilistic
- Non-deterministic
- Optimized for plausibility, not correctness

### Correct Rule

> Architecture constrains the LLM.
> The LLM does not shape the architecture.

Violating this caused the system to drift toward chatbot-like behavior.

---

## Root Cause Summary

The failures were not due to:

- Bad intent
- Poor engineering
- Lack of knowledge

They were due to:

> **Losing the original mental model while adding advanced components.**

Once the system stopped being treated as a *decision engine* and started being treated as a *conversation*, correctness eroded.

---

## Refactor Strategy (Without Throwing Work Away)

This is a **surgical refactor**, not a rewrite.

### Step 1 — Re-anchor Non-Negotiable Invariants

These must be explicitly documented and enforced:

- Intent is authoritative
- Intent is never a slot
- Clarifications must unblock execution
- One clarification fills exactly one slot
- Workflows never depend on LLMs mid-execution

---

### Step 2 — Lock the Slot System

- Remove `issue_type` permanently
- Gate only on execution-critical data
- Stop treating slots as validation

---

### Step 3 — Simplify Workflows

- Execution path depends on facts, not LLM confidence
- Intent affects messaging, not execution logic
- Workflows behave like telecom runbooks

---

### Step 4 — Downgrade Inference

Inference must:

- Suggest defaults
- Never block execution
- Never override explicit user facts
- Be fully reversible

Inference is *assistive*, not *foundational*.

---

### Step 5 — Freeze LLM Responsibility

The LLM does exactly two things:

1. Classify intent
2. Route to a workflow

Nothing else.

---

### Step 6 — Use Observability Correctly

Observability exists to validate:

- Where users get stuck
- Why escalation occurs
- Which workflows succeed or fail

It is not a substitute for architectural clarity.

---

## Final Re-Anchor (Core Insight)

We are not building:

- A chatbot
- An agentic AI
- An LLM-driven reasoning system

We are building:

> **A fault-tolerant, stateful telecom decision system that uses LLMs as probabilistic classifiers — not as brains — with the sole goal of solving the customer’s problem efficiently.**

This document exists to ensure we do not drift from that again.



---


#  TL;DR

i over engineered and missed the core part (resolution)...

but eventually ~~`fucked around and`~~ `found out`

---