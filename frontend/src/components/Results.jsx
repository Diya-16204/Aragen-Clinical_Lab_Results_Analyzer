import React, { useState } from 'react'
import SeverityBadge from './SeverityBadge'
import ReferenceRangeBar from './ReferenceRangeBar'

function downloadCsv(results) {
  const columns = ['Date', 'Test Name', 'Value', 'Unit', 'Status', 'Direction', 'Reference Range', 'AI Explanation', 'Suggested Next Step']
  const quote = value => `"${String(value ?? '').replaceAll('"', '""')}"`
  const body = results.map(item => [item.date, item.test_name, item.value, item.unit, item.status, item.direction, item.reference_range, item.explanation, item.next_step].map(quote).join(','))
  const url = URL.createObjectURL(new Blob([[columns.join(','), ...body].join('\n')], { type: 'text/csv;charset=utf-8' }))
  const link = document.createElement('a'); link.href = url; link.download = 'clinical-lab-analysis.csv'; link.click(); URL.revokeObjectURL(url)
}

export default function Results({ results }) {
  const [filter, setFilter] = useState('ALL')
  if (!results) return <section className="empty"><span>◌</span><h2>Results will appear here</h2><p>Enter results above to receive transparent classifications and AI-supported clinical context.</p></section>
  const counts = Object.fromEntries(['CRITICAL', 'WARNING', 'NORMAL'].map(status => [status, results.filter(item => item.status === status).length]))
  const visibleResults = filter === 'ALL' ? results : results.filter(item => item.status === filter)
  return <section className="results"><div className="results-head"><div><span className="eyebrow">ANALYSIS COMPLETE</span><h2>Prioritized findings</h2></div><span>{results.length} results</span></div>
  <div className="severity-summary"><div><b>{counts.CRITICAL}</b><span>Critical</span></div><div><b>{counts.WARNING}</b><span>Warning</span></div><div><b>{counts.NORMAL}</b><span>Normal</span></div><div className="export-actions"><button onClick={() => downloadCsv(results)}>Download CSV</button><button onClick={() => window.print()}>Print / Save PDF</button></div></div>
  <div className="result-controls"><button className={filter === 'ALL' ? 'active' : ''} onClick={() => setFilter('ALL')}>All ({results.length})</button><button className={filter === 'CRITICAL' ? 'critical' : ''} onClick={() => setFilter('CRITICAL')}>🚨 Critical ({counts.CRITICAL})</button><button className={filter === 'WARNING' ? 'warning' : ''} onClick={() => setFilter('WARNING')}>⚠️ Warning ({counts.WARNING})</button><button className={filter === 'NORMAL' ? 'normal' : ''} onClick={() => setFilter('NORMAL')}>✓ Normal ({counts.NORMAL})</button></div>
  <div className="cards">{visibleResults.map((item, i) => <article className={`result-card ${item.status.toLowerCase()}`} key={`${item.test_name}-${i}`}>
    <div className="card-top"><div><SeverityBadge status={item.status} /></div><strong>{item.test_name}</strong></div>
    <div className="measurement"><b>{item.value}</b><span>{item.unit}</span></div><p className="range">Reference range: <strong>{item.reference_range}</strong></p><ReferenceRangeBar value={item.value} low={item.normal_low} high={item.normal_high} unit={item.unit} status={item.status} /><span className={`direction ${item.direction.toLowerCase().replace(' ', '-')}`}>{item.direction === 'IN RANGE' ? 'Within range' : `${item.direction === 'HIGH' ? '↑ High' : '↓ Low'}`}</span>
    <details className="why"><summary>Why this status?</summary><p><strong>Deterministic classification:</strong> {item.classification_reason}</p><p>Fixed reference rules set the status before the AI explanation is requested.</p></details>
    <div className="insight"><h3>AI clinical context</h3><p>{item.explanation}</p></div><div className="next"><h3>Suggested next step</h3><p>{item.next_step}</p></div>
  </article>)}</div></section>
}
