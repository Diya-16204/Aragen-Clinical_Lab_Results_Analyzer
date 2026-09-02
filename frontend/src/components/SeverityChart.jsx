import React from 'react'

const series = [{ key: 'CRITICAL', label: 'Critical', className: 'critical' }, { key: 'WARNING', label: 'Warning', className: 'warning' }, { key: 'NORMAL', label: 'Normal', className: 'normal' }]

export default function SeverityChart({ results }) {
  const total = Math.max(results.length, 1)
  const counts = Object.fromEntries(series.map(item => [item.key, results.filter(result => result.status === item.key).length]))
  const criticalEnd = counts.CRITICAL / total * 100; const warningEnd = criticalEnd + counts.WARNING / total * 100
  const pieStyle = { background: `conic-gradient(#d75d50 0 ${criticalEnd}%, #e5a641 ${criticalEnd}% ${warningEnd}%, #5bb9a4 ${warningEnd}% 100%)` }
  return <section className="chart-section" aria-label="Severity distribution charts"><div><span className="eyebrow">PHASE 2 · VISUAL ANALYTICS</span><h2>Severity distribution</h2><p>Interactive visual summary of results routed from highest to lowest clinical priority.</p></div><div className="chart-layout"><div className="severity-chart">{series.map(item => <div className="chart-row" key={item.key}><span>{item.label}</span><div className="chart-track"><div className={`chart-bar ${item.className}`} style={{ width: `${(counts[item.key] / total) * 100}%` }} /></div><strong>{counts[item.key]}</strong></div>)}</div><div className="donut-wrap"><div className="donut" style={pieStyle}><div><b>{results.length}</b><span>results</span></div></div><div className="donut-legend">{series.map(item => <span key={item.key}><i className={item.className} />{item.label}</span>)}</div></div></div></section>
}
