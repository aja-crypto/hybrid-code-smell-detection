/**
 * ResultDisplay Component
 * 
 * Displays:
 * - Prediction (Smell / No Smell)
 * - Confidence score
 * - Probability distribution
 * - Batch results (if applicable)
 * - Detailed statistics
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './ResultDisplay.css';

function ResultDisplay({ result }) {
  const [feedback, setFeedback] = useState('');
  const [activeTab, setActiveTab] = useState('overview');

  const handleDownloadReport = () => {
    const generatedAt = new Date();
    const generatedAtDisplay = generatedAt.toLocaleString();
    const detected = result.detected_lines || [];
    const qualityScore = Math.round((result.probabilities?.clean_code || 0) * 100);
    const totalSmells = detected.length;
    const antiPatterns = detected.filter((item) =>
      /anti-pattern|debug|magic|duplicate|long method/i.test(item.reason || '')
    ).length;

    const rowsHtml =
      detected.length > 0
        ? detected
            .map(
              (item) => `
        <tr>
          <td>Line ${item.line}</td>
          <td>${item.reason}</td>
          <td>${(item.snippet || '').replace(/</g, '&lt;').replace(/>/g, '&gt;')}</td>
        </tr>`
            )
            .join('')
        : `
        <tr>
          <td>-</td>
          <td>No hotspot</td>
          <td>No specific line-level issues were identified.</td>
        </tr>`;

    const reportHtml = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Code Smell Detection Report</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; color: #1f2937; }
    h1 { color: #4f46e5; margin-bottom: 18px; }
    .meta { font-size: 18px; margin: 6px 0; }
    .card {
      margin-top: 22px; padding: 20px; border-radius: 16px;
      border: 2px solid #6366f1; background: #f8fafc;
    }
    .grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin-top: 10px; }
    .metric { font-size: 34px; font-weight: 700; }
    .label { color: #4b5563; font-size: 14px; margin-top: 4px; }
    .sub { margin-top: 18px; font-size: 36px; font-weight: 700; color: #0ea5e9; }
    .perf { margin-top: 12px; display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; font-size: 20px; }
    table { width: 100%; border-collapse: collapse; margin-top: 24px; }
    th {
      background: linear-gradient(90deg, #6366f1, #4f46e5);
      color: white; text-align: left; padding: 12px; font-size: 18px;
    }
    td { padding: 12px; border-bottom: 1px solid #e5e7eb; font-size: 18px; vertical-align: top; }
    tr:nth-child(even) { background: #f9fafb; }
  </style>
</head>
<body>
  <h1>Code Smell Detection Report</h1>
  <div class="meta"><strong>File Analyzed:</strong> ${result.file_name || 'code_snippet'}</div>
  <div class="meta"><strong>Scan Date:</strong> ${generatedAtDisplay}</div>

  <div class="card">
    <div class="meta"><strong>Quality Score:</strong> ${qualityScore}/100</div>
    <div class="grid">
      <div>
        <div class="metric">${totalSmells}</div>
        <div class="label">Total Code Smells</div>
      </div>
      <div>
        <div class="metric">${antiPatterns}</div>
        <div class="label">Anti-Patterns</div>
      </div>
      <div>
        <div class="metric">${result.label || '-'}</div>
        <div class="label">Prediction</div>
      </div>
    </div>

    <div class="sub">Model Performance</div>
    <div class="perf">
      <div><strong>Confidence:</strong> ${(result.confidence * 100).toFixed(2)}%</div>
      <div><strong>Clean Prob:</strong> ${((result.probabilities?.clean_code || 0) * 100).toFixed(2)}%</div>
      <div><strong>Smell Prob:</strong> ${((result.probabilities?.code_smell || 0) * 100).toFixed(2)}%</div>
    </div>
  </div>

  <table>
    <thead>
      <tr>
        <th>Location</th>
        <th>Issue Type</th>
        <th>Description</th>
      </tr>
    </thead>
    <tbody>
      ${rowsHtml}
    </tbody>
  </table>
</body>
</html>
`;

    const blob = new Blob([reportHtml], { type: 'text/html' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    const safeName = (result.file_name || 'analysis').replace(/[^a-zA-Z0-9._-]/g, '_');
    a.href = url;
    a.download = `${safeName}_analysis_report.html`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  };

  // Handle batch results
  if (result.batch) {
    return (
      <div className="result-display batch-results">
        <div className="result-header">
          <h2>📊 Batch Analysis Results</h2>
        </div>

        <div className="summary-cards">
          <div className="summary-card">
            <div className="summary-value">{result.summary.total}</div>
            <div className="summary-label">Total Analyzed</div>
          </div>
          <div className="summary-card smell">
            <div className="summary-value">{result.summary.smells_detected}</div>
            <div className="summary-label">Smells Detected</div>
          </div>
          <div className="summary-card clean">
            <div className="summary-value">{result.summary.clean_code}</div>
            <div className="summary-label">Clean Code</div>
          </div>
          <div className="summary-card">
            <div className="summary-value">
              {(result.summary.average_confidence * 100).toFixed(1)}%
            </div>
            <div className="summary-label">Avg. Confidence</div>
          </div>
        </div>

        <div className="batch-results-table">
          <table>
            <thead>
              <tr>
                <th>File Name</th>
                <th>Length</th>
                <th>Prediction</th>
                <th>Confidence</th>
              </tr>
            </thead>
            <tbody>
              {result.results.map((item, idx) => (
                <tr key={idx} className={item.label.toLowerCase().includes('smell') ? 'smell' : 'clean'}>
                  <td className="file-name">{item.file_name}</td>
                  <td>{item.code_length} chars</td>
                  <td>
                    <span className={`badge ${item.label.toLowerCase().includes('smell') ? 'smell' : 'clean'}`}>
                      {item.label}
                    </span>
                  </td>
                  <td>
                    <div className="confidence-bar">
                      <div
                        className="confidence-fill"
                        style={{ width: `${item.confidence * 100}%` }}
                      />
                      <span className="confidence-text">
                        {(item.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  // Handle single result
  const prediction = result.prediction;
  const confidence = result.confidence;
  const label = result.label;
  const isSmell = prediction === 1;
  const detectedLines = result.detected_lines || [];

  return (
    <motion.div
      className={`result-display ${isSmell ? 'smell' : 'clean'}`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
    >
      {/* Result Header */}
      <div className="result-header">
        <div className={`result-icon ${isSmell ? 'smell' : 'clean'}`}>
          {isSmell ? '⚠️' : '✅'}
        </div>
        <div className="result-title">
          <h2>{label}</h2>
          <p className="file-info">
            {result.file_name} • {result.analysis_time_ms}ms
          </p>
        </div>
      </div>

      {/* Confidence Display */}
      <div className="confidence-section">
        <div className="confidence-meter">
          <div className="confidence-scale">
            <div
              className={`confidence-bar-fill ${isSmell ? 'smell' : 'clean'}`}
              style={{ width: `${confidence * 100}%` }}
            />
          </div>
          <div className="confidence-labels">
            <span>Low</span>
            <span className="confidence-value">
              {(confidence * 100).toFixed(2)}%
            </span>
            <span>High</span>
          </div>
          <p className="confidence-note">
            Confidence is the model’s certainty for this input (not overall dataset accuracy).
          </p>
        </div>
      </div>

      {/* Probability Distribution */}
      <div className="result-tabs">
        <button
          type="button"
          className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          type="button"
          className={`tab-btn ${activeTab === 'lines' ? 'active' : ''}`}
          onClick={() => setActiveTab('lines')}
        >
          Detected Lines
        </button>
        <button
          type="button"
          className={`tab-btn ${activeTab === 'metrics' ? 'active' : ''}`}
          onClick={() => setActiveTab('metrics')}
        >
          Metrics
        </button>
      </div>

      <AnimatePresence mode="wait">
      {activeTab === 'overview' && (
        <motion.div
          key="overview"
          className="probability-section"
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -6 }}
          transition={{ duration: 0.18 }}
        >
          <h3>Prediction Probabilities</h3>
          <div className="probability-bars">
            <div className="probability-item">
              <div className="probability-label">
                <span>Clean Code</span>
                <span className="probability-value">
                  {(result.probabilities.clean_code * 100).toFixed(2)}%
                </span>
              </div>
              <div className="probability-bar clean">
                <div
                  className="probability-fill"
                  style={{ width: `${result.probabilities.clean_code * 100}%` }}
                />
              </div>
            </div>

            <div className="probability-item">
              <div className="probability-label">
                <span>Code Smell</span>
                <span className="probability-value">
                  {(result.probabilities.code_smell * 100).toFixed(2)}%
                </span>
              </div>
              <div className="probability-bar smell">
                <div
                  className="probability-fill"
                  style={{ width: `${result.probabilities.code_smell * 100}%` }}
                />
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Detected Line Locations */}
      {activeTab === 'lines' && (
        <motion.div
          key="lines"
          className="line-detection-section"
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -6 }}
          transition={{ duration: 0.18 }}
        >
          <h3>📍 Detected Code Locations</h3>
          {detectedLines.length > 0 ? (
            <div className="line-list">
              {detectedLines.map((item, idx) => (
                <div className="line-item" key={`${item.line}-${idx}`}>
                  <div className="line-meta">
                    <span className="line-badge">Line {item.line}</span>
                    <span className="line-reason">{item.reason}</span>
                  </div>
                  <code className="line-snippet">{item.snippet}</code>
                </div>
              ))}
            </div>
          ) : (
            <p className="line-empty">
              No specific line-level hotspots were identified for this sample.
            </p>
          )}
        </motion.div>
      )}

      {activeTab === 'metrics' && (
        <motion.div
          key="metrics"
          className="metrics-panel"
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -6 }}
          transition={{ duration: 0.18 }}
        >
          <div className="metric-card">
            <span>Quality Score</span>
            <strong>{Math.round((result.probabilities.clean_code || 0) * 100)}/100</strong>
          </div>
          <div className="metric-card">
            <span>Detected Lines</span>
            <strong>{detectedLines.length}</strong>
          </div>
          <div className="metric-card">
            <span>Confidence</span>
            <strong>{(confidence * 100).toFixed(2)}%</strong>
          </div>
        </motion.div>
      )}
      </AnimatePresence>

      {/* Interpretation */}
      <div className="interpretation-section">
        <h3>📌 Interpretation</h3>
        {isSmell ? (
          <div className="interpretation smell">
            <p>
              <strong>Code Smell Detected:</strong> This code snippet likely contains
              potential issues such as:
            </p>
            <ul>
              <li>Long methods or functions</li>
              <li>Duplicate code segments</li>
              <li>Poor variable naming</li>
              <li>Excessive complexity</li>
              <li>Tight coupling</li>
              <li>Low cohesion</li>
            </ul>
            <p>
              <strong>Recommendation:</strong> Review and refactor this code following SOLID
              principles and clean code practices.
            </p>
          </div>
        ) : (
          <div className="interpretation clean">
            <p>
              <strong>Clean Code:</strong> This code snippet appears to follow good practices:
            </p>
            <ul>
              <li>Good naming conventions</li>
              <li>Appropriate code length</li>
              <li>Clear structure and logic</li>
              <li>Low coupling</li>
              <li>High cohesion</li>
            </ul>
            <p>
              <strong>Recommendation:</strong> Keep maintaining these code quality standards.
            </p>
          </div>
        )}
      </div>

      {/* Technical Details */}
      <div className="technical-details">
        <h3>⚙️ Technical Details</h3>
        <div className="details-grid">
          <div className="detail-item">
            <span className="detail-label">Model:</span>
            <span className="detail-value">GraphCodeBERT</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Analysis Time:</span>
            <span className="detail-value">{result.analysis_time_ms}ms</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Prediction:</span>
            <span className="detail-value">
              {prediction === 0 ? 'No Smell (0)' : 'Smell Detected (1)'}
            </span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Confidence:</span>
            <span className="detail-value">{(confidence * 100).toFixed(2)}%</span>
          </div>
        </div>
      </div>

      <div className="actions-section">
        <button type="button" className="report-btn" onClick={handleDownloadReport}>
          Download Styled Report
        </button>
        <div className="feedback-box">
          <span>Was this result helpful?</span>
          <button
            type="button"
            className={`feedback-btn ${feedback === 'like' ? 'active' : ''}`}
            onClick={() => setFeedback('like')}
            aria-label="Like result"
          >
            👍
          </button>
          <button
            type="button"
            className={`feedback-btn ${feedback === 'dislike' ? 'active' : ''}`}
            onClick={() => setFeedback('dislike')}
            aria-label="Dislike result"
          >
            👎
          </button>
        </div>
      </div>
    </motion.div>
  );
}

export default ResultDisplay;
