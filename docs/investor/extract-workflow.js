export const meta = {
  name: 'zune-investor-extract',
  description: 'Extract investor-brief content from every research report (8 extractors) and research market sizing/competitors (1 researcher)',
  phases: [
    { title: 'Extract', detail: 'one extractor per cluster of reports -> short structured page content' },
    { title: 'Market', detail: 'market sizing and competitor landscape with sources' },
  ],
}

// Run:  Workflow({ scriptPath: "/home/user/Zune/docs/investor/extract-workflow.js", args: { repo: "/home/user/Zune" } })
const A = (typeof args === 'object' && args) ? args : {}
const REPO = A.repo || '/home/user/Zune'
const R = `${REPO}/docs/research`

const CLUSTERS = [
  { key: 'A', files: ['01-aosp-base-release.md', '03-minimal-product-config.md'] },
  { key: 'B', files: ['02-hardware-target.md', '15-snapdragon-device-selection.md', '21-own-hardware-roadmap-india.md'] },
  { key: 'C', files: ['04-no-browser-lockdown.md', '16-minimal-settings-app.md'] },
  { key: 'D', files: ['05-parental-controls-platform.md', '10-ota-signing-security-supply-chain.md'] },
  { key: 'E', files: ['06-curated-learning-video.md', '07-ai-assistant.md'] },
  { key: 'F', files: ['08-walkie-talkie-comms.md', '12-telephony-calls-sms-allowlists.md', '13-kid-messenger-and-video-calling.md'] },
  { key: 'G', files: ['09-core-apps-stack.md', '14-weather-education-app.md'] },
  { key: 'H', files: ['11-compliance-legal-regulatory.md', '17-byo-image-distribution-installer.md', '18-v1-flash-and-deliver-operations.md', '19-india-regulatory-compliance.md', '20-india-market-and-localization.md'] },
]

const ENTRY = {
  type: 'object',
  properties: {
    id: { type: 'string', description: 'R + two-digit report number, e.g. R04' },
    title: { type: 'string' },
    investorHeadline: { type: 'string', description: 'A claim, not a label; <= 14 words' },
    decision: { type: 'string', description: 'What was decided/recommended; <= 30 words' },
    whyItMatters: { type: 'string', description: 'Why an investor cares; <= 30 words' },
    keyPoints: { type: 'array', items: { type: 'object', properties: { text: { type: 'string' }, ref: { type: 'string' } }, required: ['text', 'ref'] } },
    numbers: { type: 'array', items: { type: 'object', properties: { label: { type: 'string' }, value: { type: 'string' }, note: { type: 'string' }, basis: { type: 'string', enum: ['verified', 'reported', 'estimate'] } }, required: ['label', 'value', 'basis'] } },
    tables: { type: 'array', items: { type: 'object', properties: { title: { type: 'string' }, columns: { type: 'array', items: { type: 'string' } }, rows: { type: 'array', items: { type: 'array', items: { type: 'string' } } }, note: { type: 'string' } }, required: ['title', 'columns', 'rows'] } },
    risks: { type: 'array', items: { type: 'object', properties: { risk: { type: 'string' }, severity: { type: 'string', enum: ['H', 'M', 'L'] }, mitigation: { type: 'string' } }, required: ['risk', 'severity', 'mitigation'] } },
    stage1: { type: 'string' },
    stage2: { type: 'array', items: { type: 'string' } },
    openItems: { type: 'array', items: { type: 'string' } },
    flaggedClaims: { type: 'array', items: { type: 'object', properties: { claim: { type: 'string' }, why: { type: 'string' } }, required: ['claim', 'why'] }, description: 'UNVERIFIED/REFUTED/estimate-only claims an investor must not take as fact' },
    confidence: { type: 'string', enum: ['verified', 'partly-verified', 'unverified', 'superseded'] },
    confidenceNote: { type: 'string' },
    superseded: { type: 'string', description: 'What in the report is superseded by which decision (D-number); empty string if nothing' },
    diagramHint: { type: 'string', description: 'One sentence: the single most useful diagram for this topic' },
  },
  required: ['id', 'title', 'investorHeadline', 'decision', 'whyItMatters', 'keyPoints', 'numbers', 'risks', 'stage1', 'stage2', 'openItems', 'flaggedClaims', 'confidence', 'confidenceNote', 'superseded', 'diagramHint'],
}
const EXTRACT_SCHEMA = { type: 'object', properties: { entries: { type: 'array', items: ENTRY } }, required: ['entries'] }

const extractPrompt = (c) => `You are an INVESTOR-BRIEF EXTRACTOR for the Zune project (a kids-only, browser-less Android 17 OS image sold with a browser-based parent portal). Today is 2026-10-02.

STEP 1. Read ${REPO}/docs/REQUIREMENTS.md completely. It is AUTHORITATIVE: dated founder decisions D1-D21 and assumptions A1-A10. Later decisions supersede earlier ones (e.g. D19 no cellular calls/SMS supersedes D4-D6; D17 start on Pixel; D18 India first; D20 English only; D21 ~200 Pixel users first, own hardware later).
STEP 2. Read COMPLETELY each of these report files that EXISTS (skip missing ones; do not wait for them): ${c.files.map((f) => `${R}/${f}`).join(' ; ')}. Each report may end with a "Verification (second pass)" section and contain [CORRECTED] markers: always use the CORRECTED version of a claim, never the original.
STEP 3. For EACH existing report return one entry (id = R<number>). The entries will become pages in a visual PDF for an investor who is an ex tech founder: technically literate, wants specifics, hates fluff and walls of text, and will punish overclaiming.

RULES
- Faithful: use ONLY facts in the reports or REQUIREMENTS.md. Never invent numbers, names, sources or claims. If something is an estimate, mark basis "estimate"; if the report only had a search summary or a user report, basis "reported"; if read in primary source/real files, basis "verified".
- Short and concrete. Hard limits: investorHeadline <= 14 words; decision <= 30 words; whyItMatters <= 30 words; each keyPoint text <= 22 words (5-8 of them, each with a ref like "R04 F3" naming the section); numbers up to 8; tables up to 3 with <= 8 rows and cells <= 12 words; risks up to 5 (text <= 20 words, mitigation <= 20 words); stage2 up to 5; openItems up to 5 (<= 20 words each). Keep named technologies, APIs, device names, prices and counts: that is what a technical reader values.
- Honesty: put every UNVERIFIED, REFUTED, unchecked-at-source, or estimate-only claim that matters into flaggedClaims (with why). Set confidence: 'verified' if the report passed a skeptic pass with only minor corrections; 'partly-verified' if it passed a skeptic pass but its core evidence was secondary or AOSP primary sources were unreachable; 'unverified' if no skeptic pass; 'superseded' if its core recommendation was overturned by a later decision. confidenceNote explains in <= 25 words.
- Superseded content: if a report's recommendation or numbers conflict with REQUIREMENTS.md (cellular calls/SMS, Snapdragon-first, US launch assumptions, Hindi/Indic, 10/25/100 cohorts, hardware bundle pricing, etc.), put that in 'superseded' (what, and which D-number) and do NOT present it as current in keyPoints/decision; restate the CURRENT position only if the report supports it. For a mostly superseded report (e.g. R12 telephony): give 3-4 keyPoints on what was proposed and why it was dropped, plus what still survives (reusable ideas), set confidence 'superseded'.
- Include the single most investor-relevant tables (e.g. device comparisons, bypass vectors, cost per device, option comparisons) as 'tables'.
- diagramHint: one sentence naming the diagram that would explain this topic best.
- Do not modify any files. Do not run git. Return only the structured result.`

const MARKET_SCHEMA = {
  type: 'object',
  properties: {
    marketSizing: { type: 'array', items: { type: 'object', properties: { metric: { type: 'string' }, value: { type: 'string' }, year: { type: 'string' }, geography: { type: 'string' }, source: { type: 'string' }, url: { type: 'string' }, basis: { type: 'string', enum: ['primary', 'secondary', 'estimate'] }, note: { type: 'string' } }, required: ['metric', 'value', 'geography', 'source', 'url', 'basis'] } },
    competitors: { type: 'array', items: { type: 'object', properties: { name: { type: 'string' }, geography: { type: 'string' }, approach: { type: 'string' }, price: { type: 'string' }, weakness: { type: 'string' }, funding: { type: 'string' }, source: { type: 'string' }, url: { type: 'string' } }, required: ['name', 'geography', 'approach', 'price', 'weakness', 'source'] } },
    tailwinds: { type: 'array', items: { type: 'object', properties: { item: { type: 'string' }, detail: { type: 'string' }, url: { type: 'string' } }, required: ['item', 'detail'] } },
    funnelFor200Users: { type: 'string', description: 'Honest estimate of how findable ~200 families with a qualified Pixel in India are, with the arithmetic and sources' },
    insights: { type: 'array', items: { type: 'string' } },
    gaps: { type: 'array', items: { type: 'string' } },
  },
  required: ['marketSizing', 'competitors', 'tailwinds', 'funnelFor200Users', 'insights', 'gaps'],
}

const marketPrompt = `You are a MARKET RESEARCHER preparing the market page of an investor brief for Zune (today 2026-10-02): a kids-only, browser-less Android OS image (no browser, no YouTube, no cellular calls/SMS; in-product WhatsApp-style text/voice/video with approved contacts; AI assistant; curated learning videos; weather lessons; walkie-talkie) sold with a browser-based parent portal. Read ${REPO}/docs/REQUIREMENTS.md first (decisions D1-D21): first market INDIA (D18), English only (D20), first phase ~200 users on customer-owned Pixel phones that WE flash (D16/D17/D21), own hardware later, pricing idea in reports of $59 provisioning + ~$13/month per child (unvalidated).
Your tools: WebSearch and WebFetch (some sites are blocked; skip them; source.android.com and googlesource are blocked, irrelevant here). Training knowledge ends ~June 2026, so check anything time-sensitive. NEVER invent a number or URL: every figure needs a source name and URL; if you cannot find it, say so in 'gaps'. Label basis primary (government/company filing/official statistic), secondary (press/analyst summary), estimate (your own arithmetic, shown).
Cover, for India and globally where relevant:
1) Children and teen population by age band (esp. 8-14, 6-17); children's smartphone access/ownership and usage in India (ASER, NCPCR, UNICEF, Pew, Common Sense, surveys); screen-time and online-safety concerns; urban affluent household counts.
2) India smartphone market: shipments, price-band split, premium (> INR 40,000 / ~$500) segment size and growth; Pixel's India sales/share and which Pixel models are sold officially (9a, 10, 10a?), INR prices; Android vs iPhone premium share. Compute the honest funnel for finding ~200 families with a qualified Pixel (state the arithmetic and assumptions).
3) Parental-control and kids-device market size and growth (global and India): parental control software, kids smartwatches/phones; any analyst numbers with sources.
4) Competitors and substitutes with price and model: global (Pinwheel, Bark Phone, Gabb, Troomi, Light Phone, Wisephone, Google Family Link, Apple Screen Time, Qustodio, Net Nanny, Aura, Kidslox, Fully Kiosk-based kiosks) and India (JioBharat/JioPhone, kids smartwatches such as boAt/Noise/Fire-Boltt/imoo, Family Link usage, any Indian kids phone/launcher startups); funding rounds and notable outcomes (Pinwheel, Bark, Gabb, Troomi, etc.) if public.
5) Tailwinds: laws and movements (Australia under-16 social media ban, US state phone/age-verification laws, UK/EU, India DPDP Act and children's provisions, school phone bans, 'Wait Until 8th', smartphone-free childhood movements) with dates and links.
6) Willingness to pay: any evidence on subscription prices parents pay for kids' devices/safety services (US and India).
Return the structured result. Be skeptical and specific; put limits and doubts in 'gaps'. Do not modify any files.`

phase('Extract')
const results = await parallel([
  ...CLUSTERS.map((c) => () => agent(extractPrompt(c), { label: `extract:${c.key}`, phase: 'Extract', schema: EXTRACT_SCHEMA })),
  () => agent(marketPrompt, { label: 'market', phase: 'Market', schema: MARKET_SCHEMA }),
])
const extracts = results.slice(0, CLUSTERS.length).filter(Boolean)
const market = results[CLUSTERS.length]
log(`${extracts.length}/${CLUSTERS.length} extract clusters returned; market ${market ? 'ok' : 'FAILED'}`)
return { entries: extracts.flatMap((e) => e.entries), market }
