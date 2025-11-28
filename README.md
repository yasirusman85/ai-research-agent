# 🤖 Autonomous AI Research Agent

![Python](https://img.shields.io/badge/Python-3.11-blue)
![React](https://img.shields.io/badge/Frontend-React_Vite-61DAFB)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)
![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791)
![Docker](https://img.shields.io/badge/Deployment-Docker-2496ED)

A production-ready **Full Stack AI Application** that performs autonomous internet research. 

Unlike simple chatbots, this agent uses **LangGraph** to maintain state, **PostgreSQL** to persist "memory" across sessions, and a **React + FastAPI** architecture to stream thoughts and tokens in real-time.

## 🚀 Key Features

* **🧠 Autonomous Logic:** The agent decides *when* to search and *when* to answer based on context.
* **⚡ Real-Time Streaming:** Uses **Server-Sent Events (SSE)** to stream LLM tokens and tool activity to the React UI instantly.
* **🛑 Human-in-the-Loop (HITL):** The agent automatically pauses and requests human intervention when confidence is low or when it gets stuck.
* **💾 Persistent State:** Conversation history and agent state are saved in **PostgreSQL**, allowing the agent to resume tasks even after server restarts.
* **🐳 Containerized:** Fully orchestrated using **Docker Compose** for consistent dev/prod environments.

---

## 🏗️ Architecture

The application follows a modern microservices pattern separating the reasoning engine from the UI.

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
        LLM[Groq API (Llama 3)]
        Web[DuckDuckGo / Tavily Search]
    end

    UI -- POST /chat (User Input) --> API
    API -- Start Job --> Graph
    Graph -- Read/Write State --> DB
    Graph -- Inference --> LLM
    Graph -- Search --> Web
    Graph -- Stream Events (SSE) --> SSE
    SSE -- Update UI --> UI
````

## 🛠️ Tech Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Frontend** | React, Vite, TailwindCSS | User Interface & Real-time rendering |
| **Backend** | Python, FastAPI | API & Async Request Handling |
| **Orchestration** | LangGraph, LangChain | Cyclic Graph logic & Tool calling |
| **Database** | PostgreSQL (Psycopg3) | Checkpointing agent state & history |
| **AI Model** | Llama 3.1-8b (via Groq) | Inference Engine |
| **Infrastructure** | Docker Compose | Container orchestration |

## 🏃‍♂️ How to Run

### 1\. Prerequisites

  * Docker Desktop installed.
  * A [Groq API Key](https://console.groq.com/) (Free).

### 2\. Setup Environment

Create a `.env` file in the root directory:

```bash
GROQ_API_KEY=gsk_your_key_here
DATABASE_URL=postgresql://user:password@postgres:5432/agent_db
```

### 3\. Build & Start

```bash
docker compose up --build
```

### 4\. Access the App

  * **Frontend:** `http://localhost:5173`
  * **Backend Docs:** `http://localhost:8000/docs`

## 🧪 Development Workflow

This repo is a **Hybrid Repository** containing both Django (for future Auth expansion) and FastAPI services.

  * `backend/`: Contains the FastAPI application and LangGraph logic.
  * `frontend/`: Contains the React/Vite application.
  * `init_db.py`: Script to initialize Postgres tables without transaction conflicts.

## 🤝 Contributing

1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/amazing-feature`).
3.  Commit your changes.
4.  Push to the branch.
5.  Open a Pull Request.

