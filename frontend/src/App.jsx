import React, { useState, useEffect, useRef } from 'react';
import ChatInterface from './components/ChatInterface';
import BrainLogs from './components/BrainLogs';
import InterventionModal from './components/InterventionModal';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [logs, setLogs] = useState([]);
  const [isSending, setIsSending] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [threadId] = useState("thread_" + Math.random().toString(36).substr(2, 9));

  const handleSendMessage = async (text) => {
    setIsSending(true);
    setMessages(prev => [...prev, { role: 'user', content: text }]);

    // Start SSE stream
    const eventSource = new EventSource(`http://localhost:8000/stream?query=${encodeURIComponent(text)}&thread_id=${threadId}`);

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'log') {
        setLogs(prev => [...prev, data.content]);
      } else if (data.type === 'done') {
        eventSource.close();
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
    };

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: text, thread_id: threadId })
      });

      const data = await response.json();

      if (data.status === 'paused') {
        setIsPaused(true);
        setLogs(prev => [...prev, "⚠️ AGENT PAUSED: Requesting Human Intervention"]);
      } else {
        setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
      }
    } catch (error) {
      console.error("Error:", error);
      setMessages(prev => [...prev, { role: 'assistant', content: "Error communicating with backend." }]);
    } finally {
      setIsSending(false);
    }
  };

  const handleFeedback = async (feedback) => {
    setIsPaused(false);
    setLogs(prev => [...prev, `👤 Human Feedback: ${feedback}`]);

    try {
      const response = await fetch('http://localhost:8000/human-feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ thread_id: threadId, feedback })
      });

      const data = await response.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
    } catch (error) {
      console.error("Error sending feedback:", error);
    }
  };

  return (
    <div className="app-container">
      <header>
        <h1>🤖 AI Research Agent</h1>
        <p>Powered by LangGraph & React</p>
      </header>

      <main className="main-layout">
        <div className="chat-section">
          <ChatInterface
            onSendMessage={handleSendMessage}
            messages={messages}
            isSending={isSending}
          />
        </div>
        <div className="brain-section">
          <BrainLogs logs={logs} />
        </div>
      </main>

      <InterventionModal isOpen={isPaused} onSubmit={handleFeedback} />
    </div>
  );
}

export default App;
