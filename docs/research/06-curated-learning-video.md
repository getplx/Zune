# 06. Curated learning video: legality, tech, alternatives

Written 2026-10-02. Basis tags: **[P]** read in a primary source this session, **[S]** secondary (reputable doc/news or a search-tool summary), **[I]** engineering judgement, **[M]** memory, unchecked.

**Evidence limit.** `developers.google.com`, `support.google.com`, `youtube.com`, Wikipedia, FTC and Khan Academy were EGRESS_BLOCKED. Every YouTube-policy claim comes from WebSearch summaries of the official pages, so it is tagged **[S]**, not **[P]**. Re-read those pages verbatim on an unrestricted container before legal reliance.

## 1. Summary & recommendation

**Verdict: CONDITIONAL GO. YouTube is a gated Tier 2, never the foundation of the Videos section.**

- YouTube does not forbid a hand-picked, child-directed embed. Its policies name a "Child-Directed API Client" and say what it must do [S]. There is no YouTube Kids API for third parties [S]. The IFrame player in a WebView is the only sanctioned route; the native Android Player API is deprecated [P: library README; S].
- Zune's containment design (D2, report 04) collides with four YouTube rules: no overlays over the player, no disabling player links, no blocking ads, no offline caching (2.2). Enforcement is discretionary and YouTube can cut embedding for our referrer at any time.
- So: build Tier 2 in Stage 1 behind a server-side kill switch, **MFK-only (made-for-kids videos only)**, and make Videos work on day one without it, using offline licensed/open content (Tier 1) plus a few paid partners (Tier 3). Never charge for access to YouTube content.
- **Gate:** written YouTube answers to the five questions in 4.4 plus counsel sign-off on COPPA. If YouTube says no, or is silent after 8 weeks, ship Tier 1 and 3 only. No NewPipe-style extraction, ad blocking or downloading.
- Best clean Tier 1 find: **Oak National Academy** (UK curriculum, open licence, videos, bulk offline download). Biggest trap: **Khan Academy, TED and PBS** content, and the Kolibri/Kiwix packs carrying it, is non-commercial.

## 2. Findings

### 2.1 What YouTube permits
| # | Finding | Basis |
|---|---|---|
| F1 | Clients must look up the Made-For-Kids (MFK) status of **each embedded video** (`videos.list`, `status.madeForKids`), turn off tracking for MFK videos, and comply with COPPA/GDPR (cited as III.E.4.j). developers.google.com/youtube/terms/developer-policies | S |
| F2 | A child-directed client must self-designate with Google's tools (becoming a "Known Child-Directed API Client"), may not use personalised ads or remarketing, and its users' write actions are not applied. Designation is required even with `youtube-nocookie.com`, and turns off personalised ads and some player features. support.google.com/policies/answer/9664901 | S |
| F3 | Clients must link the YouTube Terms of Service, state that users are bound by them, and make users accept a privacy policy. Player at least 200x200; one autoplaying player at most, started once over half visible. | S |
| F4 | Embeds are identified by the HTTP `Referer` (added to Required Minimum Functionality 2025-07-07); a missing referrer gives **Error 153**. The reference Android wrapper loads its page with `loadDataWithBaseURL("https://<packageName>", html)` and maps `153` to REQUEST_MISSING_HTTP_REFERER (android-youtube-player@60efc356 `WebViewYouTubePlayer.kt`, `IFramePlayerOptions.kt`, `YouTubePlayerBridge.kt`). developers.google.com/youtube/terms/required-minimum-functionality | S, P |
| F5 | Embeds need no OAuth and no Play Services: the wrapper's core depends only on AndroidX lifecycle and loads `https://www.youtube.com/iframe_api` (`core/build.gradle`, `ayp_youtube_player.html`). | P |

### 2.2 Rules that collide with the Zune design
| YouTube rule [S] | Zune element hit | Verdict |
|---|---|---|
| No overlays or frames in front of any part of the embedded player, including controls (exceptions: consent, playback controls). developers.google.com/youtube/terms/developer-policies-guide | Report 04 row 7 "touch shield" | **Drop the shield.** Block navigation in the WebView client. |
| Must not remove, obscure, alter or disable any link in YouTube players | D2: no path to youtube.com (logo, title, "Watch on YouTube") | **Grey, needs a written answer.** No browser exists, but our code refuses the navigation. MFK videos show no cards or end screens [S: support.google.com/youtube/answer/9684541], which helps. |
| No modifying, replacing or blocking ads; MFK embeds still carry contextual ads [S: support.google.com/youtube/answer/9713557] | Report 04 proxy/allowlist that could drop ad hosts | **Allowlist must include Google ad hosts.** Kids see ads we cannot remove. Play has removed apps using the wrapper for "access[ing] YouTube videos in a way that violates the YouTube Terms of Service" (issues #791, #192; cause unstated, the developer suspected ad bypass) [P: issue text]. |
| No downloading, caching or offline copies without written approval | Offline Videos | **No offline YouTube.** Tier 1 covers offline. |
| No background (audio-only or hidden) player | "Listen" mode | Not offered. |
| No charging users to watch embedded content; no gating a video behind anything but pressing play | Product is sold; D3 gating | Keep YouTube free in the product. Parent PIN and screen-time locks are grey. |
| Derived-metrics policy: custom scores and "brand suitability" metrics need an amendment (audited analytics developers). developers.google.com/youtube/terms/derived-metrics-policy | ML age-suitability pre-filter | Unclear if it applies. Make all labels **human editorial** judgements. |

### 2.3 Technical feasibility (no GMS, no browser)
- **Embed:** one first-party HTTPS page we host (stable origin means stable Referer and a domain we can tag child-directed), one `YT.Player`, `rel=0`, `fs=0`, `disablekb=1`. Since 2018 `rel=0` shows same-channel related videos and cannot disable them; `modestbranding` is dead since 2023-08, so the logo and links stay [S: developers.google.com/youtube/player_parameters].
- **Network:** firewall guides list `youtube.com`, `youtube-nocookie.com`, `google.com`, `ytimg.com`, `googlevideo.com`, `gstatic.com`, `ggpht.com`, `googleapis.com` and the doubleclick/2mdn/googlesyndication/googleadservices families [S: sonicwall.com KB "YouTube fails to play videos after adding to Allowed Domains list"]. The list drifts unannounced, so the allowlist is a coarse perimeter and the page is the real gate [I].
- **Leakage:** `target=_blank` links need `setSupportMultipleWindows(false)` and `onCreateWindow` returning false; `shouldOverrideUrlLoading` covers top-frame navigation only (report 04 F5). The wrapper has no navigation handling, so we write it [P].
- **Unplayable:** age-restricted, deleted, private, region-blocked and embedding-disabled videos fail with 100/101/150 [S]; catch them in a nightly check. Exclude live streams [I].
- **Data API:** 10,000 units/day default; `videos.list` and `playlistItems.list` cost 1; `search.list` costs 100 and since 2026-06-01 has its own 10,000 bucket, so **about 100 live searches a day fleet-wide** [S: developers.google.com/youtube/v3/revision_history]. Non-authorised data may be cached 30 days at most [S]. More quota needs an audit, and YouTube may audit any client [S: developers.google.com/youtube/v3/guides/quota_and_compliance_audits].
- **Consequence for D3:** "topic the child asked about" is answered from **our own catalog index**, never live YouTube search. Store permanently only `videoId` plus our editorial text; treat YouTube titles, thumbnails and stats as a 30-day cache [I].
- **Extraction (NewPipe, Invidious, InnerTube):** **not acceptable.** Undocumented, against the Terms [S].

### 2.4 Child-privacy exposure
- Amended COPPA Rule: effective 2025-06-23, compliance due 2026-04-22; adds separate parental consent for third-party disclosures and a written retention policy [S: davispolk.com "FTC prioritizes COPPA enforcement"].
- Disney paid $10M (order entered 2025-12-23) for leaving child-directed videos marked "not made for kids", so YouTube collected data and served personalised ads [S: natlawreview.com "No child's play"]. Anyone putting a mislabelled video before a child shares that exposure.
- Whether YouTube's identifiers via our embed are a "third-party disclosure" needing separate consent is for topic 11 [I].
- **Rule: MFK-only for age bands up to 12.** Older learners' channels are often "not made for kids"; they need child-directed designation plus counsel sign-off, or go to Tier 1/3.

### 2.5 Alternatives and licences
| Source | Licence found | Commercial in a paid image? | Basis |
|---|---|---|---|
| Oak National Academy (UK KS1-4, videos, quizzes) | OGL v3.0, attribution; the API blocks any lesson with restricted third-party files, media, quiz images or works; bulk offline video tars exist | **Yes** | P: `oaknational/oak-curriculum-api@main` `README.md`, `src/lib/queryGate.ts`; S: schoolsweek.co.uk "Oak ... will allow commercial use" |
| PhET sims (STEM) | CC BY 4.0 | **Yes** (HTML5, needs WebView) | S: phet.colorado.edu/en/licensing/html |
| NASA media | Generally not copyrighted; no implied endorsement, no logos, third-party items excluded | **Yes**, with care | S: nasa.gov/nasa-brand-center/images-and-media |
| Smithsonian Open Access | CC0 (mostly images, 3D, data) | **Yes** | S: si.edu/openaccess/faq |
| Wikimedia Commons, Wikipedia (Kiwix ZIM), Internet Archive, Library of Congress | Per file or item; Archive disclaims rights accuracy | Yes if each item cleared, with attribution/share-alike | S: commons.wikimedia.org "Reusing content outside Wikimedia" |
| StoryWeaver (EPUB stories) | CC BY 4.0, ePub download | **Yes**; feeds the EPUB reader | S: prathambooks.org/cc |
| Blender open movies | CC BY 3.0 | Yes | S: creativecommons.org/2008/06/13/big-buck-bunny-beautiful-cc-licensed-3d-short |
| **Khan Academy** | CC BY-NC-SA 4.0; its help says use "incorporating it into a paid offering is NOT non-commercial" | **No** without a deal | S: support.khanacademy.org article 42929097425037 |
| **TED / TED-Ed** | TED terms: CC BY-NC-ND 4.0; commercial needs a licensing request (a library guide says TED-Ed on YouTube uses the standard YouTube licence: unresolved) | **No** | S: ted.com terms of use |
| **PBS KIDS / LearningMedia** | Personal or educational non-commercial; no redistribution | **No** | S: pbskids.org/privacy/termsofuse |
| OpenStax, Crash Course | OpenStax: one summary says CC BY-NC-SA, older sources CC BY. Crash Course: I believe NC, **could not verify** | Treat as No | S, M |
| Britannica; Common Sense Media ratings | Britannica API free only for non-commercial, 1,000 queries/day, else a deal; Common Sense API needs a partnership (ratings, not video) | Paid | S: encyclopediaapi.com; commonsensemedia.org/developers/api-overview |

BBC Bitesize and Nat Geo Kids: no licensing programme found; do not plan on them. **Kolibri** code is MIT [P: `learningequality/kolibri@develop:LICENSE`], each item carries a licence from a fixed set including NC/ND [P: `le-utils@main:le_utils/constants/licenses.py`], and its Android app is a Python server plus WebView, about 200 MB before content [S: kolibri.readthedocs.io/en/latest/install/android.html]. **Kiwix** Android is GPLv3-or-later [P: `kiwix/kiwix-android@main:README.md`]. Being in a Kolibri channel or Kiwix ZIM does not clear an item: Khan and TED content ships in both [S].

### 2.6 Self-hosting video
Cloudflare Stream lists $5 per 1,000 stored minutes per month and $1 per 1,000 delivered minutes [S: flarecalc.com/calculators/stream]. Bunny Stream lists about $0.005-0.01/GB stored and delivered in Europe/North America [S: bunny.net/pricing/stream]. At 480p (about 0.45 GB/h [I]): 20 min/day streamed per child costs about $0.60 per child-month on Cloudflare, about $0.03-0.05 on Bunny; a 150 h catalog costs about $45/month stored on Cloudflare; a 40 h starter pack (about 18 GB) downloaded once costs about $0.20 per device on Bunny. Hosting is cheap. **Rights and curation labour are the real cost.**

## 3. Options & trade-offs
| Option | For | Against | Call |
|---|---|---|---|
| A. YouTube only (literal ask) | Huge catalog, no hosting | Revocable, ads, no offline, four collisions | No |
| B. Offline licensed/open only | We own the stack, clean D2 | Smaller catalog, licensing work | **Base** |
| **C. B + gated YouTube + paid partners** | Day-one value, YouTube optional | Two player backends, curation cost | **Chosen** |
| D. NewPipe-style extraction/download | Best UX, no ads | Against the Terms, legal and reputational risk | **Reject** |
| E. Kolibri as runtime | Mature, MIT | Python server in image, loopback needs INTERNET (clashes with report 04), adult UI, content licences still ours | Not v1; borrow licence taxonomy |

## 4. Recommended design for Zune

### 4.1 Tiers
- **Tier 1, offline (v1 base):** Oak (if UK first), NASA, PhET, Commons/Wikipedia, Blender shorts, StoryWeaver into the EPUB reader. Native playback with **Media3** (Apache-2.0, 1.11.1 on 2026-09-10) [P: `androidx/media@release:LICENSE`, `RELEASENOTES.md`], no WebView and no INTERNET permission in the player; a separate downloader/updater holds the network permission and delivers signed content packs. Ship a ~40 h starter pack, fetch more over Wi-Fi.
- **Tier 2, YouTube (gated):** isolated WebView page on our own HTTPS origin, one iframe, MFK-only, no shield, link/window blocking in the client, ad hosts allowed, remote kill switch, fallback to Tier 1 on 153 or block.
- **Tier 3, partners:** deals with channel owners and publishers whose videos we host as files (Khan, TED, Britannica, kids catalogs), shrinking Tier 2 over time.

### 4.2 Curation operations
- **People [I]:** one education lead (standards), 2-3 part-time editors, two reviewers for under-8s and new channels. At about 35 videos per editor-day, a 1,500-video launch catalog is roughly 45 editor-days single review, 80 double.
- **Workflow:** channel vetting; editors watch in the official embed (never download); review form; publish; nightly health check; parent report button quarantining within 24 h; 10% quarterly re-review. ML only triages the queue from our own text, never YouTube data.
- **Health check:** batch `videos.list` (50 IDs per unit) for `privacyStatus`, `embeddable`, `madeForKids`, `regionRestriction`, `contentRating` [M]. Delist on any change and on client-reported 100/101/150/153; purge cached API fields at 30 days.
- **Parent overrides:** v1 block-only (channel, video, topic); "suggest a video" goes to editors. No parent-added channels, which would bypass review.
- **Schema (LRMI-aligned [S: dublincore.org/specifications/lrmi/1.1]):** `id, source(yt|file|partner), sourceId, licence, attribution, typicalAgeRange, topics[], standards[] (CCSS/NGSS/UK NC), type, durationSec, language, regions, editorialSummary (ours), reviewers[2], reviewedAt, nextReviewAt, safetyFlags, mfk, embeddable, lastApiCheckAt, status, delistReason`. Common Core's public licence covers the standards text [S: thecorestandards.org/public-license]; England's curriculum is OGL v3.0 [S]; NGSS terms look non-profit-oriented, so verify [S].
- **Mislabel exposure [I]:** never claim "100% safe"; describe the review process in the terms; counsel review with topic 11.

### 4.3 Tier 2 compliance checklist
Per-video MFK lookup at publish and nightly; our origin tagged child-directed in Search Console; no analytics or watch-history identifiers sent to third parties; no write actions; YouTube ToS link and acceptance in parent-portal enrolment; privacy policy; `strict-origin-when-cross-origin`; user taps play; API audit filed.

### 4.4 Steps to de-risk
1. File a written use case via the YouTube API Services form (support.google.com/youtube/contact/yt_api_form) asking: (Q1) may a child-directed commercial OS image embed MFK-only videos; (Q2) may we refuse navigation out of the player on a device with no browser; (Q3) is a playback-controls-only overlay acceptable; (Q4) do human age/topic labels count as derived metrics; (Q5) is there a device-partner route for an AOSP image without GMS.
2. File the Audit and Quota Extension Form before launch; a changed use case needs a re-audit [S].
3. Tag the origin domain, build the prototype with evidence captures, get counsel sign-off.
4. In parallel start Tier 3 outreach (Khan, TED, Britannica) and get Oak's terms for a paid product in writing.
5. Gate at 8 weeks: favourable answers mean flag-on for a pilot cohort; otherwise it stays off.

## 5. Risks & unknowns
- Policy text unread first-hand; wording and section numbers may differ from the summaries.
- YouTube can cut referrer access with only an appeals form as recourse. Mitigated by kill switch and Tier 1.
- Link "disabling" may be irreconcilable with D2: if YouTube insists the player stay fully clickable, D2 and Tier 2 cannot coexist. Ad clicks open advertiser pages the client must refuse, itself a link-disabling case.
- MFK-only narrows content for ages 10-14; Tier 1/3 must cover them.
- COPPA status of YouTube's collection through our embed is unresolved (topic 11).
- Oak is England-aligned (weak US fit); confirm its terms for a paid product.
- YouTube may refuse stale Chromium builds [I, unverified], tying us to the report 04 WebView cadence.
- Crash Course, OpenStax and TED-Ed licences unresolved.

## 6. Decisions needed from the founder
1. Approve CONDITIONAL GO: Tier 2 behind a kill switch, launch not dependent on it, dropped if YouTube refuses or is silent at 8 weeks.
2. If YouTube requires working in-player links, which wins: D2 or YouTube Videos?
3. First market: US (Common Core/NGSS, weaker Tier 1) or UK (Oak fits)? A1 assumes US.
4. Keep YouTube free inside the product (subscription pays only for portal, Tier 1, Tier 3)?
5. Accept MFK-only for under-13 bands, kids seeing YouTube's contextual ads, and block-only parent overrides in v1?
6. Budget for curation staff and Tier 3 licences, and who signs outreach to YouTube, Khan, TED, Britannica.

## 7. Load-bearing claims
| # | Claim | Source | Basis |
|---|---|---|---|
| 1 | Clients must check MFK per embedded video and turn off tracking; child-directed clients self-designate and may not use personalised ads | developers.google.com/youtube/terms/developer-policies | S |
| 2 | No overlays in front of the player; no removing, obscuring or disabling player links | developers.google.com/youtube/terms/developer-policies-guide and developer-policies | S |
| 3 | No ad modification/blocking, download/cache/offline, or background player; Play has removed apps citing YouTube-ToS misuse (cause unstated) | developer-policies; github.com/PierfrancescoSoffritti/android-youtube-player/issues/791 | S, P |
| 4 | Embed works in WebView without GMS via `https://www.youtube.com/iframe_api` and an https base-URL origin; Referer required (Error 153) | android-youtube-player@60efc356 `ayp_youtube_player.html`, `WebViewYouTubePlayer.kt`, `core/build.gradle` | P |
| 5 | `search.list` is 100 units in its own 10,000/day bucket from 2026-06-01; non-authorised data cached 30 days max | developers.google.com/youtube/v3/revision_history; developer-policies | S |
| 6 | Khan Academy: use inside a paid offering is not non-commercial (CC BY-NC-SA) | support.khanacademy.org/hc/en-us/articles/42929097425037 | S |
| 7 | Oak lessons/videos are OGL-compatible via API; restricted third-party lessons gated; bulk offline video download exists | `oaknational/oak-curriculum-api@main` `README.md`, `src/lib/queryGate.ts` | P |
| 8 | Disney $10M FTC settlement for mislabelled child-directed videos; amended COPPA compliance 2026-04-22 | natlawreview.com "No child's play"; davispolk.com "FTC prioritizes COPPA enforcement" | S |
| 9 | Kolibri is MIT with per-item licences incl. NC/ND; Kiwix Android is GPLv3+ | `learningequality/kolibri@develop:LICENSE`; `le-utils@main:le_utils/constants/licenses.py`; `kiwix/kiwix-android@main:README.md` | P |
| 10 | Media3 is Apache-2.0 and current (1.11.1, 2026-09-10) | `androidx/media@release:LICENSE`, `RELEASENOTES.md` | P |
