import React, { useState } from 'react';
import '../App.css';

const ChatInterface = ({ onSendMessage, messages, isSending }) => {
    const [input, setInput] = useState("");

    const handleSubmit = (e) => {
        e.preventDefault();
        if (input.trim() && !isSending) {
            onSendMessage(input);
            setInput("");
        }
    };

    return (
        <div className="chat-interface">
            <div className="messages-area">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`message-row ${msg.role}`}>
                        <div className="message-bubble">
                            <p>{msg.content}</p>
                        </div>
                    </div>
                ))}
                {isSending && (
                    <div className="message-row assistant">
                        <div className="message-bubble thinking">
                            Thinking...
                        </div>
                    </div>
                )}
            </div>
            <form onSubmit={handleSubmit} className="input-area">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask the agent..."
                    disabled={isSending}
                />
                <button type="submit" disabled={isSending}>Send</button>
            </form>
        </div>
    );
};

export default ChatInterface;
