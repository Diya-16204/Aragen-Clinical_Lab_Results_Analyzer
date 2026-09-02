# Project Phases

## Phase 1 — MVP Complete

The current delivered MVP provides the full assignment workflow:

- React dashboard with manual entry, Kaggle-style CSV upload, row selection, demo presets, and reset controls.
- FastAPI `POST /analyze_labs` endpoint with input validation and error handling.
- Deterministic NORMAL, WARNING, and CRITICAL classification using transparent reference ranges.
- MCP tools for range lookup, classification, and LLM explanation.
- Severity routing: Critical first, Warning second, Normal last.
- Live Groq or Gemini LLM-generated clinical context and suggested next steps.
- Explainable result cards that separate deterministic classification from AI explanation.
- Synthetic Normal, Warning, and Critical test CSVs plus the supplied Kaggle dataset.

## Phase 2 — Planned Enhancements

These are intentionally planned improvements, not current MVP claims.

1. **Severity summary chart** — interactive count chart for Critical, Warning, and Normal results.
2. **High / low direction** — show whether abnormal values are above or below the normal interval.
3. **Export results** — download the analyzed results as CSV and presentation-friendly PDF.
4. **Reference-range glossary** — browse supported tests, units, ranges, and classification boundaries.
5. **Trend history** — group dated CSV observations by test and show value trends over time.
6. **Automated backend tests** — test normal, warning, critical, invalid-unit, and unknown-test cases.
7. **Repository delivery** — initialize Git, create meaningful incremental commits, and publish a public GitHub repository.

## Suggested Phase 2 Delivery Order

1. Automated backend tests and high/low direction.
2. Severity summary chart and reference-range glossary.
3. CSV/PDF exports.
4. Trend history.
5. GitHub release and deployment.
