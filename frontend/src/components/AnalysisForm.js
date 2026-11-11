/**
 * AnalysisForm Component
 * 
 * Handles:
 * - Code input textarea
 * - File upload
 * - Analyze button
 */

import React from 'react';
import Editor from '@monaco-editor/react';
import './AnalysisForm.css';

function AnalysisForm({
  code,
  fileName,
  loading,
  onCodeChange,
  onFileUpload,
  onFileUploadDirect,
  onAnalyze,
  onBatchAnalyze,
  onClear
}) {
  const detectLanguage = () => {
    const lowerName = (fileName || '').toLowerCase();
    if (lowerName.endsWith('.py')) return 'python';
    if (lowerName.endsWith('.java')) return 'java';
    if (lowerName.endsWith('.cpp') || lowerName.endsWith('.c')) return 'cpp';
    if (lowerName.endsWith('.ts')) return 'typescript';
    if (lowerName.endsWith('.js')) return 'javascript';
    if (lowerName.endsWith('.go')) return 'go';
    if (lowerName.endsWith('.php')) return 'php';
    return 'javascript';
  };

  return (
    <div className="analysis-form">
      <div className="form-section">
        <label htmlFor="code-input">
          <strong>🧠 Monaco Code Editor</strong>
        </label>
        <div className="editor-shell">
          <Editor
            height="320px"
            language={detectLanguage()}
            value={code}
            onChange={(value) => onCodeChange(value || '')}
            theme="vs-dark"
            options={{
              minimap: { enabled: false },
              fontSize: 14,
              lineNumbers: 'on',
              wordWrap: 'on',
              scrollBeyondLastLine: false,
              automaticLayout: true,
              readOnly: loading,
              tabSize: 2,
            }}
          />
        </div>
        <p className="char-count">{code.length} characters</p>
      </div>

      <div className="form-section">
        <label>
          <strong>📂 Upload File</strong>
        </label>
        <div className="file-upload-area">
          <input
            type="file"
            id="file-upload"
            onChange={onFileUploadDirect}
            disabled={loading}
            accept=".java,.py,.js,.cpp,.c,.js,.ts,.go,.rb,.php,.txt"
            className="file-input"
          />
          <label htmlFor="file-upload" className="file-label">
            Choose File or Drag & Drop
          </label>
          {fileName && <p className="file-name">✓ {fileName}</p>}
        </div>
      </div>

      <div className="form-section">
        <label>
          <strong>⚙️ Paste & Upload</strong>
        </label>
        <div className="method-buttons">
          <div className="button-group">
            <input
              type="file"
              id="paste-upload"
              onChange={onFileUpload}
              disabled={loading}
              accept=".java,.py,.js,.cpp,.c,.js,.ts,.go,.rb,.php,.txt"
              className="file-input-hidden"
            />
            <label htmlFor="paste-upload" className="btn btn-secondary">
              📥 Upload & Paste
            </label>
          </div>
        </div>
      </div>

      <div className="form-section actions">
        <button
          onClick={onAnalyze}
          disabled={loading || code.trim().length === 0}
          className="btn btn-primary"
        >
          {loading ? '⏳ Analyzing...' : '▶️ Analyze Code'}
        </button>

        <button
          onClick={onBatchAnalyze}
          disabled={loading || code.trim().length === 0}
          className="btn btn-info"
        >
          {loading ? '⏳ Processing...' : '📊 Batch Analyze'}
        </button>

        <button
          onClick={onClear}
          disabled={loading}
          className="btn btn-secondary"
        >
          🗑️ Clear
        </button>
      </div>

      <div className="form-info">
        <p>
          <strong>💡 Tip:</strong> For batch analysis, separate code snippets with blank lines.
        </p>
      </div>
    </div>
  );
}

export default AnalysisForm;
