import React from 'react'

export default function TrendHistory({ results }) {
  const dated = results.filter(item => item.date)
  if (!dated.length) return null
  const grouped = Object.values(dated.reduce((groups, item) => { (groups[item.test_name] ||= []).push(item); return groups }, {})).filter(items => items.length > 1)
  if (!grouped.length) return <section className="trend"><span className="eyebrow">TREND HISTORY</span><p>Upload two or more dated observations for the same supported test to view its trend.</p></section>
  return <section className="trend"><span className="eyebrow">TREND HISTORY</span><h2>CSV observation history</h2>{grouped.map(items => <TrendChart key={items[0].test_name} items={items} />)}</section>
}

function TrendChart({ items }) {
  const ordered = [...items].sort((a, b) => String(a.date).localeCompare(String(b.date)))
  const values = ordered.map(item => item.value); const low = Math.min(...values); const high = Math.max(...values); const pad = Math.max((high - low) * .15, 1)
  const x = index => ordered.length === 1 ? 150 : 32 + index * (276 / (ordered.length - 1)); const y = value => 116 - ((value - (low - pad)) / ((high + pad) - (low - pad))) * 84
  const points = ordered.map((item, index) => `${x(index)},${y(item.value)}`).join(' ')
  return <article className="trend-chart"><div className="trend-head"><b>{ordered[0].test_name}</b><span>{ordered[0].unit}</span></div><svg viewBox="0 0 340 150" role="img" aria-label={`${ordered[0].test_name} value trend`}><line x1="32" y1="116" x2="310" y2="116"/><line x1="32" y1="22" x2="32" y2="116"/><text x="4" y="27">{high}</text><text x="4" y="119">{low}</text><polyline points={points}/>{ordered.map((item, index) => <g key={`${item.date}-${item.value}`}><circle cx={x(index)} cy={y(item.value)} r="5"/><text x={x(index)} y="137" textAnchor="middle">{item.date}</text><text x={x(index)} y={y(item.value) - 10} textAnchor="middle">{item.value}</text></g>)}</svg></article>
}
