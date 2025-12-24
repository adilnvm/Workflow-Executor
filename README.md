# Workflow Executor Backend

A scalable, LLM-assisted workflow execution backend designed to convert unstructured user problems into structured decisions and deterministic backend actions.

This project is currently being developed as part of an internship at **Jio Platforms Ltd**, with a strong focus on **backend correctness, safety, and scalability**.  
The architecture is intentionally product-oriented so it can later be extended, generalized, and presented as an independent platform.

---

#### To see the design up untill phase 5 view [ `/docs/ARCHITECTURE.md`](https://github.com/adilnvm/Workflow-Executor/blob/main/docs/ARCHITECTURE.md)...huh


## 1. Core Idea

The system enforces a strict separation of responsibilities:

1. LLMs are used **only** for intent and entity extraction  
2. Schemas (Pydantic) enforce structure and validation  
3. Backend code controls all decision-making and execution  
4. APIs expose only final outcomes, never internal reasoning  

This approach ensures predictability, auditability, and production readiness.

---

## 2. High-Level Architecture

Client (Frontend)
|
v
FastAPI Backend
|
v
Schema-Aligned LLM Extraction
|
v
Pydantic Validation
|
v
Deterministic Decision Logic
|
v
Tool / API Execution
|
v
Structured API Response



The backend is designed first, with the frontend layered on top later.  
This enables clean API contracts, easy frontend integration, and independent backend evolution.

---

## 3. Design Principles

- LLM output is treated as **untrusted input**
- All boundaries are enforced via schemas
- Decision logic never lives inside prompts
- Failures are contained at validation boundaries
- New workflows are added via schemas and tools, not prompt hacks

---

## 4. Scalability and Product Vision

Although currently scoped for internal workflows at **Jio Platforms Ltd**, the system is designed as a **generic workflow execution platform**.

Planned scalability includes:
- Multiple workflow types
- Domain-specific extraction schemas
- Pluggable tool and API layers
- Admin and client-facing frontend applications

The backend remains the single source of truth, with all future frontends consuming it via stable API contracts.

---

## 5. Tech Stack

- Python 3.x  
- FastAPI  
- Pydantic  
- LangChain  

---

## 6. Project Status

Current focus:
- Backend-first architecture
- Safe and constrained LLM integration
- Deterministic workflow execution
- Extensibility and clarity over feature breadth

Frontend layers and advanced agent behaviors will be added in later stages.
