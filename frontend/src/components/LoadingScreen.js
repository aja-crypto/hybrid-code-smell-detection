/**
 * AI System Boot Loading Screen
 * Premium futuristic AI operating system boot-up interface
 * Code Smell Detection System
 */

import React, { useEffect, useRef, useState } from 'react';
import './LoadingScreen.css';
import axios from 'axios';

function LoadingScreen(props) {
  const { onInitComplete, onError, initializationStep, modelReady } = props;
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const spinnerRef = useRef(null);

  // Initialization state
  const [progress, setProgress] = useState(0);
  const [modulesInitialized, setModulesInitialized] = useState(0);
  const [backendHealth, setBackendHealth] = useState(null);
  const [error, setError] = useState(null);
  const [initializationStep, setInitializationStep] = useState('initializing');

  // Step progression for initialization
  const steps = [
    'CONNECTING TO BACKEND',
    'LOADING GRAPHCODEBERT',
    'PREPARING AI MODEL',
    'INITIALIZING CODE ANALYSIS ENGINE'
  ];

  // Check backend health
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/api/health', {
          timeout: 5000
        });
        setBackendHealth(response.data);
        setModelReady(response.data.model_loaded === true);
      } catch (err) {
        setBackendHealth({ status: 'ok', device: 'None', model_loaded: false, database_connected: false });
        if (onError) onError('backend_connection');
      }
    };

    checkHealth();
  }, [onError]);

  // Main initialization sequence
  useEffect(() => {
    if (backendHealth === null) return;

    let initialized = false;

    const initSequence = async () => {
      // Reset state
      setProgress(0);
      setModulesInitialized(0);
      setError(null);
      setInitializationStep('initializing');

      // Step 1: Connect to backend
      setInitializationStep('CONNECTING TO BACKEND');
      await new Promise(resolve => setTimeout(resolve, 500 + Math.random() * 500));
      if (initialized) return;
      setInitializationStep(steps[0] || 'CONNECTING TO BACKEND');

      // Step 2: Load GraphCodeBERT model
      if (initialized) return;
      setInitializationStep(steps[1] || 'LOADING GRAPHCODEBERT');
      await new Promise(resolve => setTimeout(reducedMotion ? 1000 : 2000 + Math.random() * 1000));
      if (initialized) return;

      // Step 3: Prepare AI model
      if (initialized) return;
      setInitializationStep(steps[2] || 'PREPARING AI MODEL');
      await new Promise(resolve => setTimeout(reducedMotion ? 800 : 1500 + Math.random() * 800));
      if (initialized) return;

      // Step 4: Initialize Code Analysis Engine
      if (initialized) return;
      setInitializationStep(steps[3] || 'INITIALIZING CODE ANALYSIS ENGINE');

      // Final initialization - mark as ready
      await new Promise(resolve => setTimeout(reducedMotion ? 500 : 1000 + Math.random() * 500));
      if (initialized) return;

      // Initialize complete
      initialized = true;
      setInitializationStep('SYSTEM READY');
      setProgress(100);
      setModulesInitialized(5);

      // Signal completion
      if (onInitComplete) {
        const timeoutId = setTimeout(() => {
          if (!initialized) return;
          onInitComplete();
        }, 500);

        return () => clearTimeout(timeoutId);
      }
    };

    initSequence();

    return () => {
      initialized = true;
    };
  }, [backendHealth, reducedMotion, onInitComplete, steps]);

  // Circular progress animation
  useEffect(() => {
    if (reducedMotion || progress < 100) return;

    let animationId = 0;
    const startTime = Date.now();

    const animate = () => {
      const elapsed = Date.now() - startTime;
      // Easing function for smooth progress
      const t = Math.min(elapsed / 2000, 1);
      const easeOut = 1 - Math.pow(1 - t, 3);
      setProgress(Math.round(100 * easeOut));

      if (t < 1) {
        animationId = requestAnimationFrame(animate);
      } else {
        setProgress(100);
      }
    };

    animate();

    return () => {
      if (animationId) cancelAnimationFrame(animationId);
    };
  }, [progress, reducedMotion]);

  // Module indicator sequential animation
  useEffect(() => {
    if (modulesInitialized <= 0 || reducedMotion) return;

    const timeoutId = setTimeout(() => {
      setModulesInitialized(prev => {
        if (prev >= 5) {
          return 5;
        }
        return prev + 1;
      });
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [modulesInitialized, reducedMotion]);

  // Error handling - retry (inline, no useEffect)
  const handleRetry = () => {
    setError(null);
    setInitializationStep('initializing');
    setProgress(0);
    setModulesInitialized(0);
    setBackendHealth(null);
    setModelReady(false);

    // Re-run initialization check
    const checkHealth = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/api/health', {
          timeout: 5000
        });
        setBackendHealth(response.data);
        setModelReady(response.data.model_loaded === true);
      } catch (err) {
        setError('Could not connect to backend server');
      }
    };

    checkHealth();
  };

  // If initialization complete, hide loading screen
  if (modelReady && modulesInitialized >= 5) {
    if (onInitComplete) {
      const timeoutId = setTimeout(() => {
        onInitComplete();
      }, 500);
      // Don't return null immediately - let the parent handle the transition
    }
    // Continue showing loading screen briefly then hide
  }

  // Error state
  if (error) {
    return (
      <div className="loading-screen error-state">
        <div className="error-content">
          <div className="error-icon">⚠️</div>
          <h2>Initialization Failed</h2>
          <p>{error}</p>
          <button className="retry-btn" onClick={handleRetry}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="loading-screen">
      <div className="loading-container">
        {/* Central AI Circular Indicator */}
        <div className="ai-core">
          <div className="ai-core-inner">
            <div className="ai-core-ring"></div>
            <div className="ai-core-ring secondary"></div>
            <div className="ai-core-ring tertiary"></div>
            <span className="ai-letters">AI</span>
          </div>
          <div className="progress-track">
            <div className="progress-fill" style={{ width: `${progress}%` }}></div>
          </div>
        </div>

        {/* System Boot Information */}
        <div className="system-boot">
          <span className="boot-label">SYSTEM BOOT</span>
          <span className="boot-version">V1.0.0</span>
        </div>

        {/* Loading Status */}
        <div className="status-text">
          {initializationStep}
        </div>

        {/* Progress Bar */}
        <div className="progress-bar">
          <div className="progress-segment" style={{ width: `${progress}%` }}></div>
        </div>

        {/* Module Indicators */}
        <div className="module-indicators">
          {Array.from({ length: 5 }, (_, i) => (
            <div
              key={i}
              className={`module-indicator ${modulesInitialized > i ? 'active' : ''}`}
            />
          ))}
        </div>

        {/* Cyan glow accent */}
        <div className="cyan-glow"></div>
      </div>
    </div>
  );
}

export default LoadingScreen;