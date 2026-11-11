/**
 * LoadingSpinner Component
 * 
 * Displays loading animation during analysis
 */

import React from 'react';
import './LoadingSpinner.css';

function LoadingSpinner() {
  return (
    <div className="loading-spinner">
      <div className="spinner">
        <div className="spinner-circle"></div>
        <div className="spinner-circle"></div>
        <div className="spinner-circle"></div>
      </div>
      <p>Analyzing code with GraphCodeBERT...</p>
      <p className="loading-subtext">This may take a few seconds</p>
    </div>
  );
}

export default LoadingSpinner;
