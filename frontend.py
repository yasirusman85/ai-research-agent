import streamlit as st
import httpx
import os
# Title
st.set_page_config(page_title="AI Research Agent")
st.title("🤖 AI Research Agent")
st.caption("Powered by Groq, LangGraph & FastAPI")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("What would you like to research?"):
    # 1. Display user message immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Call our FastAPI Backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # connect to the FastAPI we built
                response = httpx.post(
                f"{BACKEND_URL}/chat", # Use the variable
                json={"query": prompt},
                timeout=30.0
)
                
                # Check if the response is successful
                if response.status_code == 200:
                    ai_response = response.json()["response"]
                    st.markdown(ai_response)
                    # Save AI response to history
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection failed: {e}. Is the backend running?")