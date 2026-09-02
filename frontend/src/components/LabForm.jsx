import React, { useRef, useState } from 'react'

const blank = () => ({ test_name: '', value: '', unit: '' })
const supportedTests = new Set([
  'hemoglobin', 'glucose', 'wbc', 'white blood cells', 'lökosit',
  'platelets', 'trombosit', 'creatinine', 'sodium', 'potassium', 'cholesterol', 'bilirubin'
])

export default function LabForm({ labs, setLabs, onAnalyze, loading, onLoadDemo, onReset }) {
  const fileInput = useRef()
  const [uploadNotice, setUploadNotice] = useState('')
  const [csvData, setCsvData] = useState(null)
  const [startRow, setStartRow] = useState(1)
  const [endRow, setEndRow] = useState(1)
  const update = (index, key, value) => setLabs(labs.map((lab, i) => i === index ? { ...lab, [key]: value } : lab))
  const loadCsv = async (event) => {
    const file = event.target.files?.[0]; if (!file) return
    const rows = (await file.text()).trim().split(/\r?\n/).map(line => line.split(',').map(x => x.trim()))
    const headers = rows.shift().map(header => header.replace(/^\uFEFF/, '').toLowerCase().replace(/[ _-]/g, ''))
    const nameIndex = headers.findIndex(header => ['testname', 'test'].includes(header))
    const valueIndex = headers.findIndex(header => ['value', 'result'].includes(header))
    const unitIndex = headers.indexOf('unit')
    const dateIndex = headers.indexOf('date')
    if (nameIndex < 0 || valueIndex < 0 || unitIndex < 0) {
      setUploadNotice('CSV must include Test_Name/Result/Unit or test_name/value/unit columns.')
      event.target.value = ''; return
    }
    const detectedRows = rows.map((row, index) => ({ row: index + 1, testName: row[nameIndex], value: row[valueIndex], unit: row[unitIndex] }))
      .filter(item => item.testName && item.unit && Number.isFinite(Number(item.value)) && supportedTests.has(item.testName.trim().toLowerCase()))
    setCsvData({ fileName: file.name, rows, nameIndex, valueIndex, unitIndex, dateIndex, detectedRows })
    setStartRow(1)
    setEndRow(Math.min(rows.length, 10))
    setUploadNotice(detectedRows.length ? `Supported rows detected: ${detectedRows.map(item => `${item.row} (${item.testName})`).join(', ')}. Choose a range containing them.` : `Choose data rows 1–${rows.length}, then select “Load selected rows”.`)
    event.target.value = ''
  }
  const loadSelectedRows = () => {
    if (!csvData) return
    const first = Math.max(1, Number(startRow) || 1)
    const last = Math.min(csvData.rows.length, Number(endRow) || first)
    if (first > last) { setUploadNotice('The starting row must not be greater than the ending row.'); return }
    const numericRows = csvData.rows.slice(first - 1, last).filter(row => row.length > Math.max(csvData.nameIndex, csvData.valueIndex, csvData.unitIndex))
      .map(row => ({ test_name: row[csvData.nameIndex], value: row[csvData.valueIndex], unit: row[csvData.unitIndex], date: csvData.dateIndex >= 0 ? row[csvData.dateIndex] : null }))
      .filter(lab => lab.test_name && lab.unit && lab.value !== '' && Number.isFinite(Number(lab.value)))
    const parsed = numericRows.filter(lab => supportedTests.has(lab.test_name.trim().toLowerCase()))
    if (parsed.length) {
      setLabs(parsed)
      const skipped = numericRows.length - parsed.length
      setUploadNotice(`Loaded ${parsed.length} supported result${parsed.length === 1 ? '' : 's'} from rows ${first}–${last}${skipped ? `; skipped ${skipped} unsupported test${skipped === 1 ? '' : 's'}.` : '.'}`)
    } else setUploadNotice(`No supported numeric lab rows were found between rows ${first}–${last}.`)
  }
  return <section className="panel form-panel">
    <div className="section-heading"><div><span className="eyebrow">LAB ENTRY</span><h2>Add laboratory results</h2></div><button className="upload" onClick={() => fileInput.current.click()} type="button">Upload CSV</button><input ref={fileInput} onChange={loadCsv} accept=".csv" type="file" hidden /></div>
    <div className="demo-bar"><span>Quick demo:</span><button type="button" onClick={() => onLoadDemo('mixed')}>Mixed severity</button><button type="button" onClick={() => onLoadDemo('critical')}>Critical case</button><button type="button" onClick={() => onLoadDemo('normal')}>Normal case</button><button className="reset-inline" type="button" onClick={onReset}>↺ Reset demo</button></div>
    <div className="lab-labels"><span>Test name</span><span>Value</span><span>Unit</span></div>
    {labs.map((lab, index) => <div className="lab-row" key={index}>
      <input aria-label="Test name" placeholder="e.g. Hemoglobin" value={lab.test_name} onChange={e => update(index, 'test_name', e.target.value)} />
      <input aria-label="Value" placeholder="e.g. 13.8" type="number" value={lab.value} onChange={e => update(index, 'value', e.target.value)} />
      <input aria-label="Unit" placeholder="e.g. g/dL" value={lab.unit} onChange={e => update(index, 'unit', e.target.value)} />
      {labs.length > 1 && <button className="remove" type="button" onClick={() => setLabs(labs.filter((_, i) => i !== index))} aria-label="Remove lab">×</button>}
    </div>)}
    <div className="form-actions"><button className="secondary" type="button" onClick={() => setLabs([...labs, blank()])}>+ Add another test</button><button className="analyze" type="button" disabled={loading} onClick={onAnalyze}>{loading ? 'Analyzing…' : 'Analyze results →'}</button></div>
    {csvData && <div className="csv-range"><strong>{csvData.fileName}</strong><span>Choose data rows (header excluded; 1–{csvData.rows.length})</span><label>From <input type="number" min="1" max={csvData.rows.length} value={startRow} onChange={e => setStartRow(e.target.value)} /></label><label>To <input type="number" min="1" max={csvData.rows.length} value={endRow} onChange={e => setEndRow(e.target.value)} /></label><button className="secondary" type="button" onClick={loadSelectedRows}>Load selected rows</button></div>}
    <p className="hint">Supported: Hemoglobin, Glucose, WBC/Lökosit, Platelets/Trombosit, Creatinine, Sodium, Potassium, Cholesterol, Bilirubin.</p>
    {uploadNotice && <p className="upload-notice">{uploadNotice}</p>}
  </section>
}
