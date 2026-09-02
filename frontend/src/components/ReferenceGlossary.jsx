import React, { useEffect, useState } from 'react'
import { getReferenceRanges } from '../services/api'

export default function ReferenceGlossary({ onBack }) {
  const [tests, setTests] = useState([]); const [error, setError] = useState('')
  useEffect(() => { getReferenceRanges().then(setTests).catch(error => setError(error.message)) }, [])
  return <section className="glossary glossary-page"><div><span className="eyebrow">REFERENCE LIBRARY</span><h2>Supported test glossary</h2><p>Transparent deterministic intervals used before any AI explanation.</p></div><button onClick={onBack}>← Back to analyzer</button>{error ? <p className="error">{error}</p> : <div className="glossary-grid">{tests.map(test => <article key={test.test_name}><b>{test.test_name}</b><span>{test.unit}</span><p>Normal: <strong>{test.reference_range}</strong></p><small>Warning outside {test.warning[0]}–{test.warning[1]} · Critical beyond {test.critical[0]}–{test.critical[1]}</small></article>)}</div>}</section>
}
