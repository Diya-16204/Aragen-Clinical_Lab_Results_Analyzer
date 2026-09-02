import React, { useState } from 'react'

const items = [
  ['Severity insights', 'Implemented: interactive Critical, Warning, and Normal summary.'],
  ['High / low direction', 'Implemented: abnormal numeric values show above or below range.'],
  ['Exports', 'Implemented: download CSV or use Print / Save PDF.'],
  ['Reference glossary', 'Implemented: browse tests, units, and classification boundaries.'],
  ['Trend history', 'Implemented for repeated dated CSV observations.'],
  ['Quality & delivery', 'Automated tests are included; GitHub release remains a submission step.'],
]

export default function PhaseRoadmap() {
  const [open, setOpen] = useState(false)
  return <section className="phase-roadmap">
    <div><span className="eyebrow">PHASE 2</span><h2>Enhanced decision support</h2><p>Phase 1 provides the core analyzer above. The features below extend it for richer review and presentation.</p></div>
    <button className="roadmap-toggle" type="button" onClick={() => setOpen(!open)}>{open ? 'Hide roadmap ↑' : 'View roadmap ↓'}</button>
    {open && <div className="roadmap-grid">{items.map(([title, description], index) => <article key={title}><span>0{index + 1}</span><h3>{title}</h3><p>{description}</p></article>)}</div>}
  </section>
}
