import React, { useState } from 'react'
import LabInput from './components/LabInput'
import ResultsDisplay from './components/ResultsDisplay'
import ReferenceGlossary from './components/ReferenceGlossary'
import TrendHistory from './components/TrendHistory'
import SeverityChart from './components/SeverityChart'
import ClinicalOverview from './components/ClinicalOverview'
import MCPActivity from './components/MCPActivity'
import AIAnalysisSummary from './components/AIAnalysisSummary'
import AnalysisProgress from './components/AnalysisProgress'
import { analyzeLabs } from './services/api'

const starter = [{ test_name: 'Hemoglobin', value: '8.5', unit: 'g/dL' }, { test_name: 'Glucose', value: '180', unit: 'mg/dL' }, { test_name: 'Potassium', value: '4.2', unit: 'mEq/L' }]
const demos = {
  mixed: starter,
  critical: [{ test_name: 'Hemoglobin', value: '6.8', unit: 'g/dL' }, { test_name: 'Potassium', value: '6.8', unit: 'mEq/L' }, { test_name: 'Glucose', value: '320', unit: 'mg/dL' }],
  normal: [{ test_name: 'Hemoglobin', value: '13.8', unit: 'g/dL' }, { test_name: 'Glucose', value: '99', unit: 'mg/dL' }, { test_name: 'Potassium', value: '4.2', unit: 'mEq/L' }],
}
export default function App() {
  const [labs, setLabs] = useState(starter), [analysis, setAnalysis] = useState(null), [error, setError] = useState(''), [loading, setLoading] = useState(false), [page, setPage] = useState('analyzer')
  const submit = async () => { setError(''); setLoading(true); try { setAnalysis(await analyzeLabs(labs.map(l => ({ ...l, value: Number(l.value) })))) } catch (e) { setError(e.message) } finally { setLoading(false) } }
  const loadDemo = name => { setLabs(demos[name]); setAnalysis(null); setError('') }
  const reset = () => { setLabs(starter); setAnalysis(null); setError('') }
  return <main><header><div className="brand-mark">✚</div><div><h1>Clinical Lab Results Analyzer</h1><p>Transparent, AI-assisted review of laboratory results</p></div><button className="glossary-tab" onClick={() => setPage('glossary')}>⌘ Reference glossary</button><span className="decision">Clinical decision support · Not a diagnosis</span></header>{page === 'glossary' ? <ReferenceGlossary onBack={() => setPage('analyzer')} /> : <>
  <div className="hero"><div><span className="eyebrow">DEMO-READY CLINICAL INTELLIGENCE</span><h2>From raw values to<br/><em>clear next steps.</em></h2><p>Deterministic reference-range checks identify what needs attention. AI adds concise, clinician-friendly context—without changing the result.</p></div><div className="flow"><b>1</b> Classify <i>→</i><b>2</b> Prioritize <i>→</i><b>3</b> Explain</div></div>
  <section className="phase-one"><span>PHASE 1</span><b>Core Lab Analyzer</b><p>Input → deterministic classification → MCP + AI explanation</p></section><LabInput labs={labs} setLabs={setLabs} onAnalyze={submit} loading={loading} onLoadDemo={loadDemo} onReset={reset}/>{loading && <AnalysisProgress />}{error && <div className="error">{error}</div>}{analysis && <><ClinicalOverview results={analysis.results} /><AIAnalysisSummary summary={analysis.overall_summary} /><MCPActivity activity={analysis.agent_activity} /></>}<ResultsDisplay results={analysis?.results ?? null}/>{analysis && <><SeverityChart results={analysis.results} /><TrendHistory results={analysis.results} /></>}<footer>Reference ranges are demo defaults. Always interpret results in clinical context.</footer></>}</main>
}
