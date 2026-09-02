import React from 'react'

const ICONS = { CRITICAL: '🚨', WARNING: '⚠️', NORMAL: '✓' }

export default function SeverityBadge({ status }) {
  return <><span className="status-icon">{ICONS[status]}</span><span className={`badge ${status.toLowerCase()}`}>{status}</span></>
}
