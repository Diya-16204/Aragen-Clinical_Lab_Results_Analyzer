import React from 'react'

export default function AnalysisProgress() {
  return <section className="analysis-progress" aria-live="polite"><span className="eyebrow">ANALYSIS IN PROGRESS</span><h2>Analyzing laboratory results</h2><p>Running the real workflow: validating inputs, MCP reference lookup, deterministic classification, AI explanations, then the overall AI summary.</p><div className="progress-dots"><span>Classify</span><i>→</i><span>Route</span><i>→</i><span>Explain</span><i>→</i><span>Summarize</span></div></section>
}
