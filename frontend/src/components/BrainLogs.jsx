import React, { useEffect, useRef } from 'react';
import '../App.css';

const BrainLogs = ({ logs }) => {
    const logsEndRef = useRef(null);

    useEffect(() => {
        logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [logs]);

    return (
        <div className="brain-logs-container">
            <h3 className="brain-title">Agent Brain Activity</h3>
            <div className="logs-content">
                {logs.length === 0 && <p className="waiting-text">Waiting for activity...</p>}
                {logs.map((log, index) => (
                    <div key={index} className="log-entry">
                        <span className="timestamp">[{new Date().toLocaleTimeString()}]</span> {log}
                    </div>
                ))}
                <div ref={logsEndRef} />
            </div>
        </div>
    );
};

export default BrainLogs;
