# Phase-6 — Redis Schema Design

**Goal:** Persist tickets safely without breaking agent invariants

### 0. What Redis is doing in your system

Redis is not a database here.  
It is a **session-state engine**.

It stores:

- Active ticket memory
- Conversation progress
- Derived facts
- Decision snapshots

It must:

- Survive process restarts
- Support TTL
- Be fast
- Be simple to reason about

### Core invariant (must never break)

The agent must behave identically whether memory is in Python dict or Redis.

That means:

- Same structure
- Same keys
- Same semantics
- Same lifecycle

So Redis schema mirrors your current `TICKET_STORE`.

### 2. Logical ticket model (what you already have)

```python
TICKET_STORE[ticket_id] = {
    "facts": {},
    "history": [],
    "last_decision": {}
}
```


Redis will store **exactly this**, nothing more.

### 3. Redis Key Design (critical)

**🔑 Ticket root key**  
`ticket:{ticket_id}`

**Example:**  
`ticket:e835743f-afd1-4ccd-8747-6220b45d83d9`

#### Redis Data Structure Choice

✅ **Use Redis HASH** for ticket metadata

**Why?**

- Atomic field updates
- Simple
- Debuggable
- No overengineering

#### Redis Hash Fields (final schema)

Each ticket key is a HASH with these fields:

| Field name      | Type | Description                          |
|-----------------|------|--------------------------------------|
| facts           | JSON | Stable + inferred facts              |
| history         | JSON | List of user messages                |
| last_decision   | JSON | Last LLM decision                    |
| created_at      | int  | Unix timestamp                       |
| updated_at      | int  | Unix timestamp                       |
| version         | int  | Schema version (start with 1)         |

**Example (conceptual):**
``` 
ticket:e835743f-... {
"facts": "{...}",
"history": "[...]",
"last_decision": "{...}",
"created_at": 1734958201,
"updated_at": 1734958265,
"version": 1
}
```

#### Why JSON inside Redis (not native Redis types)?

You *could* split facts/history into lists and sets.  
You *should not*.

**Reasons:**

- Your agent already treats them as atomic objects
- Rollback logic becomes trivial
- Snapshot/restore is simple
- No partial corruption
- Easier migrations

This is correct engineering, not laziness.

### 7. TTL Strategy (important)

**Ticket TTL**  
`TTL = 30 minutes` (configurable)

Redis command conceptually:  
`EXPIRE ticket:{ticket_id} 1800`

**TTL rules**

- Reset TTL on every user interaction
- Expired ticket = session expired
- Agent already handles this gracefully ✔

This satisfies:  
“Tickets must gracefully degrade”

### 8. Read / Write lifecycle (flow)

**On new ticket**

- Generate ticket_id
- Create Redis hash
- Set TTL
- Return ticket_id to client

**On clarification**

- `HGETALL ticket:{ticket_id}`
- Deserialize JSON
- Mutate in memory
- Write back with `HSET`
- Refresh TTL

**On workflow execution**

- Read facts
- Execute workflow
- Optionally close ticket or keep alive

#### Rollback compatibility (Phase-5)

Your rollback logic already does:

```
ticket_snapshot = deepcopy(ticket)

```

With Redis:

Snapshot = Python dict from Redis

Rollback = overwrite Redis hash with snapshot

No new logic required. This is why we store whole JSON blobs.

## 10. Schema versioning (future-proofing)

Field:  
`version = 1`

Why?
- Phase-7 / Phase-8 may add fields
- You can migrate safely
- You avoid silent corruption
- Managers love this.

## 11. Why Redis over SQLite/Postgres for this phase

| Feature | Redis | SQLite | Postgres |
|------|------|------|------|
| Session TTL | ✅ Native | ❌ Manual | ❌ Manual |
| Speed | ✅ In-memory | ⚠️ File-based | ⚠️ Network |
| Simplicity | ✅ Very high | Medium | Low |
| Learning curve | Low | Medium | High |
| Impressiveness (for this system) | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |

Redis is industry-standard for:
- Chat sessions
- Agent memory
- Rate limits
- Queues
- Temporary state

## 12. What Redis is not storing

- ❌ Analytics
- ❌ Logs
- ❌ User accounts
- ❌ Long-term history

Those come later (Postgres).

This separation shows architectural maturity.

## 13. Final mental model (important)

- Redis = agent brain RAM
- Postgres = system memory
- LangChain = reasoning amplifier (later)

You are building the system in the right order.


# “fallback to in-memory” 



> If Redis is not available, the system silently uses Python memory (dict) instead — without breaking the agent.

Concretely

You will have one abstraction:

TicketStore


Behind it, there are two implementations:

Environment	Storage
DEV / no Redis	Python dict (current behavior)
PROD / Redis up	Redis

The agent never knows which one it’s using.

2️⃣ Why this matters in your system (not generic theory)

Your agent has these properties:

✅ Stateful

Tickets span multiple requests.

✅ Long-running

Clarifications, slot filling, inference, rollback.

✅ LLM-heavy

You already fight:

rate limits

model crashes

reloads

restarts

Now imagine Redis is down.

Without fallback:

→ Every request fails
→ Tickets are lost
→ Demo breaks
→ You look unreliable


With fallback:

→ Redis unavailable
→ Agent continues using in-memory
→ Tickets still work
→ Demo continues
→ Graceful degradation


This is exactly what Phase-5 invariants were preparing you for.

3️⃣ “Graceful degradation” (the thing you didn’t understand earlier)

Let’s define it clearly.

Graceful degradation means:
The system keeps working in a reduced capacity instead of failing hard.

In your system:
Failure	Without fallback	With fallback
Redis down	500 errors	Works
Redis slow	Timeouts	Works
Laptop offline	Dead	Works
Hackathon Wi-Fi	Dead	Works
Manager demo	Embarrassing	Impressive

This is real-world engineering, not LeetCode.

4️⃣ Why NOT just always use Redis?

Because:

DEV reality

Redis not always running

Laptop reboots

PATH issues

Docker not started

PROD reality

Redis restarts

Network partitions

Misconfigurations

Robust systems never depend on a single runtime assumption.

5️⃣ Architectural pattern you’re using (important)

You are implementing:

Pluggable State Backend

This is the same pattern used by:

LangChain memory backends

Celery brokers

Django cache backends

Kubernetes storage classes

Your version is cleaner than most tutorials.

6️⃣ What fallback buys you beyond reliability
1. Faster development

No Redis needed to hack features.

2. Easier testing

Unit tests run without infra.

3. Cleaner code

All state logic lives in one place.

4. Better interviews

You can confidently say:

“We use Redis in production, with automatic fallback to in-memory for resilience.”

That sentence alone signals seniority.

7️⃣ How this looks conceptually (no code)
Agent
  |
  v
TicketStore (interface)
  |
  +--> RedisTicketStore
  |
  +--> InMemoryTicketStore


Selection logic:

If Redis available:
    use RedisTicketStore
Else:
    use InMemoryTicketStore


The agent does not change.

8️⃣ Why this pairs perfectly with your Phase-5 rollback

Because:

Rollback = overwrite snapshot

Storage backend = irrelevant

Redis or memory → same semantics

This is clean design alignment.

9️⃣ Why managers love this

Because you’re showing:

- Failure thinking

Real-world assumptions

Operational maturity

Not just “it works on my laptop”

This is production thinking, not toy AI.



---
---
---


# “fallback to in-memory” ?

**Plain English:**

> If Redis is not available, the system silently uses Python memory (`dict`) instead — without breaking the agent.

### Concretely

You will have **one abstraction**:

```
TicketStore
```

Behind it, there are **two implementations**:

| Environment     | Storage                        |
| --------------- | ------------------------------ |
| DEV / no Redis  | Python dict (current behavior) |
| PROD / Redis up | Redis                          |

The **agent never knows** which one it’s using.

---

## 2️⃣ Why this matters in *your* system (not generic theory)

Your agent has these properties:

### ✅ Stateful

Tickets span multiple requests.

### ✅ Long-running

Clarifications, slot filling, inference, rollback.

### ✅ LLM-heavy

You already fight:

* rate limits
* model crashes
* reloads
* restarts

Now imagine **Redis is down**.

Without fallback:

```
→ Every request fails
→ Tickets are lost
→ Demo breaks
→ You look unreliable
```

With fallback:

```
→ Redis unavailable
→ Agent continues using in-memory
→ Tickets still work
→ Demo continues
→ Graceful degradation
```

This is **exactly** what Phase-5 invariants were preparing you for.

---

## 3️⃣ “Graceful degradation” (the thing you didn’t understand earlier)

Let’s define it clearly.

> Graceful degradation means:
> *The system keeps working in a reduced capacity instead of failing hard.*



|
---

## 4️⃣ Why NOT just always use Redis?

Because:

### DEV reality

* Redis not always running
* Laptop reboots
* PATH issues
* Docker not started

### PROD reality

* Redis restarts
* Network partitions
* Misconfigurations

**Robust systems never depend on a single runtime assumption.**

---

## 5️⃣ Architectural pattern you’re using (important)

You are implementing:

> **Pluggable State Backend**

This is the same pattern used by:

* LangChain memory backends
* Celery brokers
* Django cache backends
* Kubernetes storage classes

Your version is **cleaner** than most tutorials.

---

## 6️⃣ What fallback buys you beyond reliability

### 1. Faster development

No Redis needed to hack features.

### 2. Easier testing

Unit tests run without infra.

### 3. Cleaner code

All state logic lives in one place.

### 4. Better interviews

You can confidently say:

> “We use Redis in production, with automatic fallback to in-memory for resilience.”

That sentence alone **signals seniority**.

---

## 7️⃣ How this looks conceptually (no code)

```text
Agent
  |
  v
TicketStore (interface)
  |
  +--> RedisTicketStore
  |
  +--> InMemoryTicketStore
```

Selection logic:

```text
If Redis available:
    use RedisTicketStore
Else:
    use InMemoryTicketStore
```

The agent does **not change**.

---

## 8️⃣ Why this pairs perfectly with your Phase-5 rollback

Because:

* Rollback = overwrite snapshot
* Storage backend = irrelevant
* Redis or memory → same semantics

This is **clean design alignment**.

---

## 9️⃣  you’re showing:

* Failure thinking
* Real-world assumptions
* Operational maturity
* Not just “it works on my laptop”

This is *10️⃣ Summary in one sentence (write this in ARCHITECTURE.md)

> The system uses Redis for persistent ticket state, with automatic fallback to in-memory storage to ensure graceful degradation during infrastructure failures or development environments.*

---
---
---