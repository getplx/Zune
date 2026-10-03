# Investor brief

`Zune-Investor-Brief.pdf` is generated, not hand-edited. It is landscape A4, about 94 pages:
a visual main body (summary, problem, market, product, architecture, one page per topic, security,
devices, delivery, India, economics, roadmap, risks, evidence status, asks, founder-to-complete),
then appendices (decision log, a detail sheet for every research report, glossary).

## Regenerate

```
# 1. (optional) refresh the page content from the research reports
Workflow({ scriptPath: "docs/investor/extract-workflow.js", args: { repo: "<repo root>" } })
#    -> save its entries + market result as docs/investor/content/extracted.json
# 2. build the PDF (needs node + playwright + pdftoppm for previews)
python3 docs/investor/build_pdf.py
```

- `build_pdf.py` = design system and helpers; `pages.py` = page definitions; `render.js` = Chromium
  rendering with automatic fit-to-page, detail-sheet pagination and overflow reporting.
- Dates and decisions come from `docs/REQUIREMENTS.md`; evidence status comes from the extracted
  content (each report's confidence, flagged claims and verification state).
- "To be completed by the founder" holds the facts the research cannot supply (team, traction, raise).
