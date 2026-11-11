import React, { useMemo } from 'react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from 'recharts';
import './ChartsPanel.css';

const COLORS = ['#22d3ee', '#6366f1', '#f59e0b', '#ef4444', '#10b981', '#a855f7', '#ec4899', '#14b8a6'];

function buildHotspotSeries(detectedLines = []) {
  const counts = new Map();
  for (const item of detectedLines) {
    const reason = item?.reason || 'Other';
    counts.set(reason, (counts.get(reason) || 0) + 1);
  }
  return Array.from(counts.entries())
    .map(([reason, count]) => ({ reason, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 8);
}

export default function ChartsPanel({ result, history }) {
  const probSeries = useMemo(() => {
    const clean = Number(result?.probabilities?.clean_code ?? 0);
    const smell = Number(result?.probabilities?.code_smell ?? 0);
    return [
      { name: 'Clean', value: Math.max(0, clean) },
      { name: 'Smell', value: Math.max(0, smell) },
    ];
  }, [result]);

  const hotspotSeries = useMemo(
    () => buildHotspotSeries(result?.detected_lines || []),
    [result]
  );

  const historySeries = useMemo(() => {
    const rows = (history || [])
      .slice(0, 8)
      .map((h, idx) => ({
        idx: idx + 1,
        confidence: Number(h?.result?.confidence ?? 0) * 100,
        label: h?.result?.label || '',
      }))
      .reverse();
    return rows;
  }, [history]);

  const hasProbs =
    result?.probabilities &&
    typeof result.probabilities.clean_code === 'number' &&
    typeof result.probabilities.code_smell === 'number';

  return (
    <div className="charts-panel">
      <div className="charts-header">
        <h3>📊 Analytics</h3>
        <p>Probability + hotspot distribution + recent confidence trend</p>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <div className="chart-title">Prediction split</div>
          <div className="chart-body">
            {hasProbs ? (
              <ResponsiveContainer width="100%" height={240}>
                <PieChart>
                  <Pie
                    data={probSeries}
                    dataKey="value"
                    nameKey="name"
                    innerRadius={50}
                    outerRadius={80}
                    cx="50%"
                    cy="50%"
                    paddingAngle={3}
                  >
                    {probSeries.map((entry, idx) => (
                      <Cell key={`cell-${entry.name}`} fill={COLORS[idx % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="chart-empty">Run analysis to generate probabilities.</div>
            )}
          </div>
        </div>

        <div className="chart-card">
          <div className="chart-title">Hotspot reasons (top)</div>
          <div className="chart-body">
            {hotspotSeries.length ? (
              <ResponsiveContainer width="100%" height={240}>
                <BarChart
                  data={hotspotSeries}
                  margin={{ top: 8, right: 10, left: 0, bottom: 6 }}
                >
                  <CartesianGrid strokeDasharray="3 3" opacity={0.25} />
                  <XAxis dataKey="reason" tick={false} />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#22d3ee" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="chart-empty">No detected hotspots for this sample.</div>
            )}
          </div>
        </div>

        <div className="chart-card">
          <div className="chart-title">Recent confidence trend</div>
          <div className="chart-body">
            {historySeries.length ? (
              <ResponsiveContainer width="100%" height={240}>
                <BarChart
                  data={historySeries}
                  margin={{ top: 8, right: 10, left: 0, bottom: 6 }}
                >
                  <CartesianGrid strokeDasharray="3 3" opacity={0.25} />
                  <XAxis dataKey="idx" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Bar dataKey="confidence" fill="#6366f1" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="chart-empty">History is empty (DB off) or not loaded.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

