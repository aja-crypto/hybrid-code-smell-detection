/**
 * Main React App Component
 * 
 * Features:
 * - Code input textarea
 * - File upload button
 * - Analyze button
 * - Results display with confidence score
 * - History panel (optional)
 * - AI System Boot loading screen
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import AnalysisForm from './components/AnalysisForm';
import ResultDisplay from './components/ResultDisplay';
import LoadingScreen from './components/LoadingScreen';
import HealthCheck from './components/HealthCheck';
import ChartsPanel from './components/ChartsPanel';

// Use explicit IPv4 loopback to avoid Windows localhost IPv6 edge cases.
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000/api';

function App() {
  // State management
  const [code, setCode] = useState('');
  const [fileName, setFileName] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [apiConnected, setApiConnected] = useState(false);
  const [history, setHistory] = useState([]);
  const [analyticsOpen, setAnalyticsOpen] = useState(false);
  const [appInitialized, setAppInitialized] = useState(false);
  const [initializationStep, setInitializationStep] = useState('initializing');
  const [modelReady, setModelReady] = useState(false);

  const dashboardStats = {
    smells: result?.batch
      ? (result.summary?.smells_detected || 0)
      : (result?.prediction === 1 ? 1 : 0),
    antiPatterns: result?.detected_lines?.length || 0,
    qualityScore: result?.probabilities?.clean_code
      ? Math.round(result.probabilities.clean_code * 100)
      : 0,
    confidence: result?.confidence ? `${(result.confidence * 100).toFixed(1)}%` : '--'
  };

  // Check API health on component mount
  useEffect(() => {
    checkApiHealth();
    loadHistory();
  }, []);

  // Initialize the AI system boot sequence
  useEffect(() => {
    if (appInitialized) return;

    let initialized = false;
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const initSequence = async () => {
      try {
        // Check backend health first
        const healthResponse = await axios.get('http://127.0.0.1:5000/api/health', {
          timeout: 5000
        });
        setApiConnected(true);

        // Progress through initialization steps with realistic delays
        setInitializationStep('CONNECTING TO BACKEND');
        await new Promise(r => setTimeout(reducedMotion ? 300 : 800, r));
        if (initialized) return;

        setInitializationStep('LOADING GRAPHCODEBERT');
        await new Promise(r => setTimeout(reducedMotion ? 500 : 1500, r));
        if (initialized) return;

        setInitializationStep('PREPARING AI MODEL');
        await new Promise(r => setTimeout(reducedMotion ? 500 : 1500, r));
        if (initialized) return;

        setInitializationStep('INITIALIZING CODE ANALYSIS ENGINE');
        await new Promise(r => setTimeout(reducedMotion ? 800 : 2000, r));
        if (initialized) return;

        // Mark as ready
        initialized = true;
        setAppInitialized(true);
        setModelReady(true);
        setInitializationStep('SYSTEM READY');

        // Signal main app to render
        setTimeout(() => {
          if (!initialized) return;
          setAppInitialized(true);
        }, 500);

      } catch (err) {
        console.error('Init sequence error:', err);
        setError('Could not initialize system. Please check backend connection.');
        setApiConnected(false);
      }
    };

    initSequence();

    return () => {
      initialized = true;
    };
  }, [appInitialized, setApiConnected, setAppInitialized, setModelReady, setInitializationStep, setError]);

  // Check if backend API is connected
  const checkApiHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`, {
        timeout: 5000
      });
      setApiConnected(true);
      console.log('API Health:', response.data);
    } catch (err) {
      setApiConnected(false);
      console.error('API Connection Error:', err);
      setError('Could not connect to backend server');
    }
  };

  // Load analysis history from database
  const loadHistory = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/history?limit=10`);
      if (response.data.status === 'success') {
        setHistory(response.data.history || []);
      }
    } catch (err) {
      console.log('Could not load history:', err);
    }
  };

  // Handle file upload
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFileName(file.name);
      const reader = new FileReader();
      reader.onload = (event) => {
        setCode(event.target.result);
      };
      reader.readAsText(file);
    }
  };

  // Handle code analysis
  const handleAnalyze = async () => {
    if (!code.trim()) {
      setError('Please enter some code to analyze');
      return;
    }

    if (!apiConnected) {
      setError('Backend server is not connected');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await axios.post(
        `${API_BASE_URL}/analyze`,
        {
          code: code,
          file_name: fileName || 'code_snippet'
        },
        {
          timeout: 30000, // 30 second timeout
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data.status === 'success') {
        setResult({
          ...response.data,
          source_code: code
        });
        // Reload history
        loadHistory();
      } else {
        setError(response.data.error || 'Unknown error');
      }
    } catch (err) {
      if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else if (err.message === 'Network Error') {
        setError('Could not connect to backend server. Make sure it is running.');
      } else {
        setError(`Error: ${err.message}`);
      }
      console.error('Analysis Error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Handle file upload via form (reads file as text)
  const handleFileUploadLocal = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!apiConnected) {
      setError('Backend server is not connected');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const reader = new FileReader();
      reader.onload = (event) => {
        setCode(event.target.result);
        setFileName(file.name);
      };
      reader.readAsText(file);
    } catch (err) {
      console.error('File read error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Handle file upload to backend (FormData)
  const handleUploadFile = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!apiConnected) {
      setError('Backend server is not connected');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(
        `${API_BASE_URL}/upload`,
        formData,
        {
          timeout: 30000,
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      if (response.data.status === 'success') {
        setResult({
          ...response.data,
          source_code: code
        });
        setFileName(file.name);
        loadHistory();
      } else {
        setError(response.data.error || 'Unknown error');
      }
    } catch (err) {
      setError(`Upload Error: ${err.message}`);
      console.error('Upload Error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Handle batch analysis
  const handleBatchAnalyze = async () => {
    if (!code.trim()) {
      setError('Please enter code snippets to analyze');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Split code by empty lines for batch processing
      const snippets = code
        .split('\n\n')
        .map(snippet => snippet.trim())
        .filter(snippet => snippet.length > 0);

      const response = await axios.post(
        `${API_BASE_URL}/batch-analyze`,
        {
          codes: snippets.map(snip => ({ code: snip })),
          file_name: fileName || 'code_snippet_batch'
        },
        {
          timeout: 60000
        }
      );

      if (response.data.status === 'success') {
        setResult({
          ...response.data,
          batch: true
        });
        loadHistory();
      } else {
        setError(response.data.error || 'Unknown error');
      }
    } catch (err) {
      setError(`Batch Analysis Error: ${err.message}`);
      console.error('Batch Analysis Error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Clear all
  const handleClear = () => {
    setCode('');
    setFileName('');
    setResult(null);
    setError('');
  };

  return (
    <div className="app">
      {appInitialized ? (
        {/* Main Application Content when initialized */}

        <header className="app-header">
          <div className="container">
            <h1>AI-Powered Code Smell Detection</h1>
            <p>Semantic Software Quality Analysis using Contrastive Transformer Learning</p>
            <HealthCheck connected={apiConnected} onRetry={checkApiHealth} />
          </div>
        </header>

        <main className="app-main">
          <div className="container">
            <section className="dashboard-cards">
              <div className="dashboard-card">
                <div className="card-value">{dashboardStats.smells}</div>
                <div className="card-label">Code Smells</div>
              </div>
              <div className="dashboard-card">
                <div className="card-value">{dashboardStats.antiPatterns}</div>
                <div className="card-label">Detected Lines</div>
              </div>
              <div className="dashboard-card">
                <div className="card-value">{dashboardStats.qualityScore}</div>
                <div className="card-label">Quality Score</div>
              </div>
              <div className="dashboard-card">
                <div className="card-value">{dashboardStats.confidence}</div>
                <div className="card-label">Confidence</div>
              </div>
              <button
                type="button"
                className="dashboard-card dashboard-card-action"
                onClick={() => setAnalyticsOpen(true)}
                disabled={!result}
                title={result ? 'Open full-screen analytics' : 'Run analysis first'}
              >
                <div className="card-value">↗</div>
                <div className="card-label">Open Analytics</div>
              </button>
            </section>

            <div className="layout">
              {/* Left Panel - Input */}
              <div className="input-panel">
                <AnalysisForm
                  code={code}
                  fileName={fileName}
                  loading={loading}
                  onCodeChange={setCode}
                  onFileUpload={handleUploadFile}
                  onFileUploadDirect={handleFileUploadLocal}
                  onAnalyze={handleAnalyze}
                  onBatchAnalyze={handleBatchAnalyze}
                  onClear={handleClear}
                />
              </div>

              {/* Right Panel - Results */}
              <div className="output-panel">
                {error && (
                  <div className="error-box">
                    <strong>⚠️ Error:</strong> {error}
                  </div>
                )}

                {result && !loading && (
                  <ResultDisplay result={result} />
                )}

                {!result && !loading && !error && (
                  <div className="info-box">
                    <h3>📋 How to Use</h3>
                    <ol>
                      <li>Paste your code in the editor or upload a file</li>
                      <li>Click "Analyze Code" to detect code smells</li>
                      <li>View the results with confidence score</li>
                      <li>Higher confidence = more accurate prediction</li>
                    </ol>
                  </div>
                )}
              </div>
            </div>

            {/* Full-width analytics charts */}
            {result && !loading && (
              <ChartsPanel result={result} history={history} />
            )}

            {/* History Panel */}
            {history.length > 0 && (
              <div className="history-panel">
                <h3>📚 Recent Analyses</h3>
                <div className="history-list">
                  {history.slice(0, 5).map((item, idx) => (
                    <div key={idx} className="history-item">
                      <span className="history-file">{item.result?.file_name}</span>
                      <span
                        className={`history-label ${item.result?.label === 'Code Smell Detected' ? 'smell' : 'clean'}`}
                      >
                        {item.result?.label}
                      </span>
                      <span className="history-confidence">
                        {(item.result?.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </main>

        {analyticsOpen && result && (
          <div className="analytics-overlay" role="dialog" aria-modal="true">
            <div className="analytics-shell">
              <div className="analytics-topbar">
                <div className="analytics-title">
                  <div className="analytics-heading">Analytics Dashboard</div>
                  <div className="analytics-sub">
                    {result.file_name || 'code_snippet'} • {(result.confidence * 100).toFixed(1)}% confidence
                  </div>
                </div>
                <button
                  type="button"
                  className="analytics-close"
                  onClick={() => setAnalyticsOpen(false)}
                >
                  Close ✕
                </button>
              </div>

              <div className="analytics-content">
                <ChartsPanel result={result} history={history} />
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <footer className="app-footer">
          <div className="container">
            <p>© 2024 Code Smell Detection System | Final Year Project</p>
            <p>Powered by GraphCodeBERT & PyTorch</p>
          </div>
        </footer>
      ) : (
        /* Full-screen Loading - AI System Boot */
        <div className="full-loading-overlay">
          <LoadingScreen
            onInitComplete={() => setAppInitialized(true)}
            onError={(errorType) => {
              setError(errorType);
              setAppInitialized(true);
            }}
            initializationStep={initializationStep}
            modelReady={modelReady}
          />
        </div>
      )}
    </div>
  );
}

export default App;