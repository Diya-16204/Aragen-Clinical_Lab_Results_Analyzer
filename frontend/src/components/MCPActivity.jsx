import React, { useState } from 'react'

export default function MCPActivity({ activity = [] }) {
  const [open, setOpen] = useState(false)
  if (!activity.length) return null
  return <section className="mcp-activity"><div><span className="eyebrow">ARCHITECTURE TRACE</span><h2>🤖 MCP Activity</h2><p>Actual tools invoked for this analysis: Classify → Route → Explain.</p></div><button onClick={() => setOpen(!open)}>{open ? 'Hide activity ↑' : `View activity (${activity.length}) ↓`}</button>{open && <ol>{activity.map((item, index) => <li className={item.status} key={`${item.tool}-${index}`}><b>{item.status === 'completed' ? '✓' : '!'}</b><div><strong>{item.tool}</strong><span>{item.details}</span></div></li>)}</ol>}</section>
}
