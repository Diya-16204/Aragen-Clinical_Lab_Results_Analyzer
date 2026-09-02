import React from 'react'

const icon = { CRITICAL: '🔴', WARNING: '🟠', NORMAL: '🟢' }
export default function ClinicalOverview({ results }) {
  if (!results?.length) return null
  const count = status => results.filter(item => item.status === status).length
  const critical = count('CRITICAL'); const warning = count('WARNING'); const normal = count('NORMAL')
  const overall = critical ? 'CRITICAL' : warning ? 'WARNING' : 'NORMAL'
  const message = critical ? `Immediate attention required for ${critical} result${critical === 1 ? '' : 's'}.` : warning ? `Clinical review recommended for ${warning} result${warning === 1 ? '' : 's'}.` : 'All analyzed values are within their configured demo ranges.'
  return <section className={`clinical-overview ${overall.toLowerCase()}`}><div><span className="eyebrow">CLINICAL OVERVIEW</span><h2>Overall status: {icon[overall]} {overall}</h2><p>{message}</p></div><div className="overview-counts"><span><b>{critical}</b> Critical</span><span><b>{warning}</b> Warning</span><span><b>{normal}</b> Normal</span><span><b>{results.length}</b> Total</span></div></section>
}
