const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function analyzeLabs(labs) {
  const response = await fetch(`${API_URL}/analyze_labs`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ labs })
  })
  const body = await response.json()
  if (!response.ok) throw new Error(body.detail || 'Unable to analyze these lab results.')
  return body
}

export async function getReferenceRanges() {
  const response = await fetch(`${API_URL}/reference_ranges`)
  if (!response.ok) throw new Error('Unable to load reference ranges.')
  return (await response.json()).tests
}
