# Architecture Overview — Workflow Executor (Telecom LLM System)

## 1. What This System Is

This project is a **stateful, LLM-driven workflow engine** designed for telecom customer support (India-first, Jio-focused).

It is **not a chatbot**.
It is a **decision system** that:

* Classifies user issues
* Extracts and accumulates facts across turns
* Executes deterministic workflows
* Survives LLM failures, restarts, and partial information

The architecture follows **production-grade conversational systems**, not demo assistants.

---

## 2. Core Design Principles (Non-Negotiable Invariants)

These invariants must **never break**, regardless of future phases.

### 2.1 LLM-Agnostic Core

* The agent must not depend on a specific LLM
* All LLMs implement the same interface:

```
generate(prompt: str) -> LLMResponse
```

This enables:

* Gemini (prod)
* Phi-3 via Ollama (local/dev)
* MockLLM (tests)

No agent logic changes when switching LLMs.

---

### 2.2 Deterministic Execution

* LLMs **decide**, they do not **act**
* All real actions happen inside workflows
* Workflows are deterministic, testable, and side-effect controlled

LLMs never:

* Call APIs
* Touch databases
* Execute tools directly

---

### 2.3 Explicit State Ownership

* The system owns state, not the LLM
* Tickets persist facts, history, and decisions
* LLM output is advisory, never authoritative

---

### 2.4 Graceful Degradation

The system must always respond meaningfully, even if:

* LLM fails
* Quota is exhausted
* Server restarts
* Memory is lost

This is achieved via:

* Fallback LLMs
* Slot-based clarification
* Ticket rollback
* In-memory fallback for persistence

---

## 3. High-Level Architecture

```
Client
  ↓
FastAPI Controller
  ↓
Agent (State + Decisions)
  ↓
Workflow Executor
  ↓
Tools (Deterministic)
```

Parallel concern:

```
Agent → Observability Event Bus
```

---

## 4. Key Components

### 4.1 Agent (`agent.py`)

**Responsibilities:**

* Ticket lifecycle management
* LLM orchestration
* Fact accumulation
* Slot enforcement
* Rollback on failure

The agent:

* Never executes business logic directly
* Never embeds observability logic
* Never depends on a specific LLM

---

### 4.2 LLM Layer (`llm/`)

#### Base Interface

```
BaseLLM.generate(prompt) -> LLMResponse
```

#### Implementations

* `GeminiLLM` (prod, quota-aware)
* `Phi3LLM` (local via Ollama)
* `MockLLM` (tests)

LLMs only:

* Interpret language
* Produce structured decisions

---

### 4.3 Ticket Store (Phase-6)

Abstracted via:

```
storage/store_provider.py
```

Implementations:

* RedisTicketStore (primary)
* InMemoryTicketStore (fallback)

**Why fallback matters:**

* DEV works without Redis
* Graceful failure in prod
* Zero downtime during infra issues

---

### 4.4 Decision Schema

All LLMs must emit:

```
{
  intent,
  confidence,
  entities,
  workflow,
  next_action,
  clarification_question
}
```

Strict validation ensures:

* No hallucinated behavior
* Predictable routing

---

### 4.5 Slot-Based Clarification (Phase-3.2)

Each workflow declares required slots.

The agent:

* Checks missing slots
* Asks targeted questions
* Ensures each clarification fills exactly one slot

This prevents:

* Infinite clarification loops
* Ambiguous conversations

---

### 4.6 Inference Engine (Phase-5)

Purpose:

* Infer safe, reversible facts
* Reduce user friction

Rules:

* Never overwrite user-provided facts
* Fully rollbackable
* Optional, confidence-bounded

---

### 4.7 Workflow Executor

Workflows are:

* Declarative
* Step-based
* Deterministic

Example steps:

* validate_region
* check_network_status
* suggest_resolution

No LLM involvement here.

---

### 4.8 Observability (Phase-7)

**What it is:**

* Event-based instrumentation

**What it is NOT:**

* Logging sprinkled everywhere
* Business logic coupling

Events capture:

* Ticket lifecycle
* LLM decisions
* Slot misses
* Rollbacks

Designed for:

* Replay
* Metrics
* Debugging
* Future analytics

---

## 5. Phase Breakdown (What We Built)

### Phase 1–2

* Basic LLM decision routing
* Workflow execution

### Phase 3

* Memory (facts + history)
* Slot-based clarification
* Decision re-evaluation

### Phase 4

* Stable vs volatile fact separation

### Phase 5

* Inference engine
* Rollback safety

### Phase 6

* Redis persistence
* In-memory fallback

### Phase 7

* Observability event architecture

---

## 6. What the Final Product Looks Like

A system that:

* Handles incomplete user input gracefully
* Works with or without LLM availability
* Persists state across restarts
* Can be audited, replayed, and improved

This is **backend infrastructure**, not UI.

---

## 7. Future Roadmap

### Phase 8

* Persist observability events
* Metrics aggregation
* Dashboards

### Phase 9

* Ticket replay engine
* Prompt improvement loops
* Failure-driven learning

### Phase 10 (Optional)

* LangChain (only if orchestration complexity increases)

---

## 8. LangChain — Why It Is Optional Here

This system already implements:

* Memory
* Routing
* Tool execution
* State control

LangChain becomes useful only if:

* Multi-agent planning is added
* Dynamic tool graphs emerge

Until then, **pure Python is simpler, clearer, and safer**.

---

## 9. Final Takeaway

This project is **not about calling LLMs**.

It is about:

> Building a fault-tolerant, stateful decision system where LLMs are replaceable components.

That is what production AI systems actually look like.
