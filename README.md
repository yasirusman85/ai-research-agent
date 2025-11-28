

# 🤖 Autonomous AI Research Agent

![Python](https://img.shields.io/badge/Python-3.11-blue)
![React](https://img.shields.io/badge/Frontend-React_Vite-61DAFB)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)
![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791)
![Docker](https://img.shields.io/badge/Deployment-Docker-2496ED)

A production-ready **Full Stack AI Application** that performs autonomous internet research.

Unlike simple chatbots, this agent uses **LangGraph** for stateful reasoning, **PostgreSQL** for persistent memory, and a **React + FastAPI** stack for real-time streaming.

---

## 🚀 Key Features

* **🧠 Autonomous Logic:** Decides when to search versus answer.
* **⚡ Real-Time Streaming:** SSE streams tokens + tool updates to the UI.
* **🛑 Human-in-the-Loop:** Automatically pauses when confidence is low.
* **💾 Persistent State:** Stores conversation & checkpoints in Postgres.
* **🐳 Containerized:** Fully deployable with Docker Compose.

---

## 🏗️ Architecture

```mermaid
graph TD
    subgraph Frontend [React UI]
        UI[Chat Interface]
        SSE[EventSource Listener]
    end

    subgraph Backend [FastAPI Service]
        API[API Endpoints]
        Graph[LangGraph Orchestrator]
    end

    subgraph Database
        DB[(PostgreSQL)]
    end

    subgraph External
        LLM["Groq API (Llama 3)"]
        Web["DuckDuckGo / Tavily Search"]
    end

    UI -->|POST /chat| API
    API -->|Start Job| Graph
    Graph -->|Read/Write State| DB
    Graph -->|Inference| LLM
    Graph -->|Search| Web
    Graph -->|SSE Stream| SSE
    SSE -->|Update UI| UI
```

---

## 🛠️ Tech Stack

| Component          | Technology               | Role                   |
| ------------------ | ------------------------ | ---------------------- |
| **Frontend**       | React, Vite, TailwindCSS | UI + Streaming         |
| **Backend**        | Python, FastAPI          | API + async engine     |
| **Orchestration**  | LangGraph, LangChain     | Cyclic reasoning graph |
| **Database**       | PostgreSQL (Psycopg3)    | Persistent memory      |
| **AI Model**       | Llama 3.1-8B (Groq)      | Inference              |
| **Infrastructure** | Docker Compose           | Deployment             |

---

## 🏃‍♂️ How to Run

### 1. Prerequisites

* Docker Desktop
* Groq API Key

### 2. Environment Setup

Create `.env`:

```bash
GROQ_API_KEY=gsk_your_key_here
DATABASE_URL=postgresql://user:password@postgres:5432/agent_db
```

### 3. Build & Start

```bash
docker compose up --build
```

### 4. Access

* Frontend: `http://localhost:5173`
* Backend Docs: `http://localhost:8000/docs`

---

## 🧪 Development Workflow

This repo includes both the FastAPI backend and React frontend.

* `backend/` — FastAPI + LangGraph logic
* `frontend/` — React/Vite UI
* `init_db.py` — Postgres table initialization

---

## 🤝 Contributing

* Fork
* Create feature branch
* Commit
* Push
* Submit PR


