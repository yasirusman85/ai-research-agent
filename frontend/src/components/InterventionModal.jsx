import React, { useState } from 'react';
import '../App.css';

const InterventionModal = ({ isOpen, onSubmit }) => {
    const [feedback, setFeedback] = useState("");

    if (!isOpen) return null;

    const handleSubmit = (e) => {
        e.preventDefault();
        if (feedback.trim()) {
            onSubmit(feedback);
            setFeedback("");
        }
    };

    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <h2>⚠️ Agent Needs Help</h2>
                <p>The agent is stuck and requested your assistance.</p>
                <form onSubmit={handleSubmit}>
                    <textarea
                        value={feedback}
                        onChange={(e) => setFeedback(e.target.value)}
                        placeholder="Provide guidance..."
                        rows={4}
                    />
                    <button type="submit">Submit Feedback</button>
                </form>
            </div>
        </div>
    );
};

export default InterventionModal;
