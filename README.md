# 🤖 AI Research Agent

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic-orange)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)

A full-stack **Agentic AI application** that autonomously researches topics using web search. Built to demonstrate advanced concepts in **Agentic RAG (Retrieval Augmented Generation)**, **Microservices Architecture**, and **Containerization**.

## 🚀 Features

* **Autonomous Research Agent:** Uses **LangGraph** to decide when to search the web and when to answer directly.
* **"Safety Brake" Logic:** Custom routing logic to prevent infinite search loops and hallucinations.
* **High-Performance Backend:** Asynchronous API built with **FastAPI**.
* **Interactive Frontend:** Chat interface built with **Streamlit** that maintains session history.
* **Free & Fast LLM:** Powered by **Groq API** (Llama 3.1 8B) for instant inference.
* **Production Ready:** Fully containerized using **Docker** & **Docker Compose**.

---

## 🏗️ Architecture

The application follows a microservices architecture:

```mermaid
graph LR
    A[User Browser] -- HTTP --> B(Streamlit Frontend)
    B -- HTTP (Internal Network) --> C(FastAPI Backend)
    C -- Logic --> D{LangGraph Agent}
    D -- Query --> E[Groq API / Llama 3]
    D -- Search --> F[DuckDuckGo Tool]
