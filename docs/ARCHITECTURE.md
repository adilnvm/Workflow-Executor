# ARCHITECTURE.md — Phase-5 Invariants

## System: Agentic Workflow Executor (Telecom Support)

### 1. Ticket Lifecycle Invariants

- A ticket is the unit of truth
- Every request belongs to exactly one ticket
- Tickets may be resumed, clarified, or retried
- Tickets must degrade gracefully

**If memory is lost (restart / crash):**
- The system must NOT 500
- The ticket must restart cleanly
- Unknown ticket_id → treated as a new ticket

**Ticket state must never corrupt**
- Partial updates are forbidden
- On any failure:
  - Ticket state is rolled back
  - Previous stable state is restored

### 2. LLM Invariants

- Agent is LLM-agnostic
- Agent logic must not depend on:
  - Gemini
  - Phi-3
  - Mock

**All LLMs MUST expose:**
- `generate(prompt: str) → LLMResponse`

**LLMs may fail, system must not**
- Quota exhaustion
- Local model crashes
- Invalid JSON
- → Must never propagate as 500 errors

### 3. Decision Invariants

- Intent and workflow are distinct
  - Intent = user problem
  - Workflow = system response plan
- One intent may map to multiple workflows later

**Confidence reflects clarity of intent**
- Missing entities MUST NOT reduce confidence
- Only unclear problem type lowers confidence

**Clarification is NOT chat**
- Clarification exists only to fill missing slots
- Every clarification must correspond to exactly one slot

### 4. Slot & Entity Invariants

- Slots are workflow-defined
- Workflows declare required slots
- Agent asks only for missing slots
- Never ask generic questions

**Derived slots are first-class**
- Some slots may be inferred

**Inferred slots:**
- Must be reversible
- Must never override user-provided facts

**Stable facts persist across turns**  
Examples:
- `service_type`
- `account_type`
- `device_type`
- `region`

Once known → never discarded

### 5. Execution Invariants

- Execution is deterministic
  - LLMs decide
  - Code executes
- LLMs never execute tools directly

**Optimistic execution is allowed**
- If intent is clear and confidence ≥ threshold
- Missing non-critical slots may be deferred

### 6. Failure & Rollback Invariants

- Every mutation is transactional
  - Before mutation → snapshot
  - On failure → rollback

- No failure may poison future turns
- A failed step must not affect:
  - Next clarification
  - Next workflow
  - Ticket continuity

### 7. Observability Invariants

- Every decision is inspectable
  - Intent
  - Confidence
  - Entities
  - Workflow
  - Next action

- Agent behavior must be explainable
- No hidden reasoning
- No silent state changes

**End of Architecture Contract**

## Why Phase-5 Was Important (what you actually learned)

**Before Phase-5, systems usually:**
- “work” until they don’t
- fail in confusing ways
- corrupt state silently

**After Phase-5:**
- You learned transactional thinking
- You separated decision vs execution
- You learned how real agents avoid hallucination-driven damage
- You stopped treating LLMs as reliable components

This is senior-level engineering thinking.

## Phase-6: Persistence (what changes, what doesn’t)

### What Phase-6 WILL change
- `TICKET_STORE` moves out of memory
- Tickets survive restarts
- Multiple workers can share state

### What Phase-6 will NOT change
- Agent logic
- Invariants
- Workflows
- Slot logic
- Rollback semantics

**If Phase-6 breaks Phase-5 invariants → Phase-6 is wrong**

### Phase-6 Options 
####  ..idk wht to choose, gpt gave me options :)

| Option    | When to use             | Why                              |
|-----------|-------------------------|----------------------------------|
| SQLite    | Learning / single machine | Simple, visible, debuggable     |
| Redis     | Multi-worker / prod-like  | Fast, TTLs, session-like        |
| Postgres  | Enterprise              | Auditing, analytics             |