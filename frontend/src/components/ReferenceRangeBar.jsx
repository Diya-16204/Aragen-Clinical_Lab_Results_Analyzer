import React from 'react'

export default function ReferenceRangeBar({ value, low, high, unit, status }) {
  if (!Number.isFinite(low) || !Number.isFinite(high) || high <= low || !Number.isFinite(value)) return <p className="range-unavailable">Reference range unavailable</p>
  const span = high - low; const displayLow = Math.min(low - span * .45, value); const displayHigh = Math.max(high + span * .45, value); const position = Math.max(2, Math.min(98, ((value - displayLow) / (displayHigh - displayLow)) * 100)); const normalStart = ((low - displayLow) / (displayHigh - displayLow)) * 100; const normalEnd = ((high - displayLow) / (displayHigh - displayLow)) * 100
  return <div className="reference-bar" role="img" aria-label={`Reference range ${low} to ${high} ${unit}; result ${value} ${unit}; ${status}`}><div className="bar-labels"><span>{low}</span><span>{high}</span></div><div className="bar-track"><div className="normal-zone" style={{ left: `${normalStart}%`, width: `${normalEnd - normalStart}%` }} /><i className="result-marker" style={{ left: `${position}%` }}><em>●</em></i></div><div className="bar-caption"><span>Normal range</span><span>Result: {value} {unit}</span></div></div>
}
