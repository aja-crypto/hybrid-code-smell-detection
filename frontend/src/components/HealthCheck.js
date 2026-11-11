/**
 * HealthCheck Component
 * 
 * Displays backend API connection status
 */

import React from 'react';
import './HealthCheck.css';

function HealthCheck({ connected, onRetry }) {
  return (
    <div className={`health-check ${connected ? 'connected' : 'disconnected'}`}>
      <div className="health-status">
        <div className={`status-indicator ${connected ? 'online' : 'offline'}`}></div>
        <span className="status-text">
          {connected ? '🟢 Backend Connected' : '🔴 Backend Offline'}
        </span>
      </div>
      {!connected && (
        <button onClick={onRetry} className="retry-btn">
          🔄 Retry Connection
        </button>
      )}
    </div>
  );
}

export default HealthCheck;
