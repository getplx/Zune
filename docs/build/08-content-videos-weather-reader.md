# Content: curated videos (two tiers), weather lessons, EPUB reader and licences

## Purpose and scope

Specifies what the child sees in Videos, Weather and Reader and the pipelines behind them: catalog, licence register, signed content packs, Tier 1 offline video, Tier 2 YouTube made-for-kids (MFK) embeds behind a kill switch (D25), India weather with authored lessons, and the parent-approved EPUB library. Code: `zune/apps/{videos,weather,reader}`, `zune/backend/{content,weather}`.

**Stage 1** = every MUST works end to end by Z5 exit (`01-prerequisites-and-phases.md`); Tier 2 ships dark until the YouTube gate. **Stage 2** = PhET simulations, Wikipedia, multi-place weather, GNSS, live IMD data, reading statistics, Hindi (D20), publisher books.

Not covered: Guardian, policy engine (`03-lockdown-and-guardian.md`); WebView provider, cell-broadcast overlays (`02-os-image-and-product.md`); keys, ZuneUpdater internals (`04-device-signing-ota-release.md`); channel, portal pages, vault, `kill_state` (`05-backend-and-parent-portal.md`); Assistant (`07-ai-assistant.md`); app shells, TTS (`09-core-apps-and-design-system.md`); legal analysis (`11-compliance-and-privacy-engineering.md`); test execution (`12-testing-qa-and-acceptance.md`).

Evidence is mostly search summaries and GrapheneOS/LineageOS mirrors, not Google's `android-17.0.0_r1` tree: see Verify first.

## Decisions applied and reconciliations

**Reconciliations applied**

| Decision / report | Effect |
|---|---|
| D25, D2, D3, R06 | R06's Tier 3 (paid partners) joins Tier 1 as hosted files. Tier 2 = MFK-only, off by default, dropped at Y0+56 days without a written yes. Topic requests are answered from the signed catalog on the device; no `search.list` in production. |
| D26 | WebView only in Videos (Tier 2) and Reader; PhET HTML5 sims would be a third surface: Stage 2. |
| D23 vs R06, R09, R14, R20 bands | One enum `7-9`, `10-12`, `13-14` (05). Tier 2 is MFK-only in every band, so 13-14 relies on Tier 1. |
| D18, D20, D31 vs R06 (CCSS), R14 (NWS, WEA, °F, device location) | NCERT-style tags; SACHET, CPCB, IMD (pending); metric, IST; places from the portal only, no location permission. |
| D22, D24 vs R09 (ZuneComms) | ZuneUpdater downloads packs for Reader and Videos; Reader keeps no INTERNET; progress sync dropped. |
| R14, R20 corrections adopted | AQI from CPCB only (not Open-Meteo's 45 km model); dew point drives "sticky"; UV card at 3, escalate at 6; `place_id` authorisation; 8 explainers x 3 bands (not R14's 20); ISRO text verbatim only; StoryWeaver needs Pratham's written yes; IMD from a fixed IP only. |
| 05 BE-04, 15, 16, 41 | Egress hosts in `egress.yaml`; Tier 2 kill = `kill_state` level 1, `features=["videos_tier2"]`; `topic` approval for unmatched topics; Tier 2 hosts in `dns/allowlist.yaml`. |

## Requirements

**Catalog and licences**
- **CNT-01 MUST** Every video, book and authored asset has a `licence_register` row (§4.2): licence, archived evidence hash and date, `commercial_ok=true`, `counsel_status` `cleared` or `conditional`. `ingest` refuses anything else and any `sources.yaml` `excluded` source (Khan Academy, TED and TED-Ed, PBS KIDS, OpenStax, Crash Course, NCERT text, NDLI, BBC Bitesize, Nat Geo Kids [R06 §2.5, R20 §2.4]) lacking a written-deal reference.
- **CNT-02 MUST** Age, band, topic, safety flags, `std` (`{board:"NCERT",class,subject,theme}`: tags only, never NCERT text, figures or exercises) and `in_rating` (`U`, `U/A 7+`, `U/A 13+`; never 16+ or A [R20 §2.4]) are human labels, signed by two reviewers when `age_min` <= 8, else one; no ML or YouTube metadata sets them [R06 §2.2].
- **CNT-03 MUST** Gutenberg and Standard Ebooks titles need `pd_basis` showing public-domain status in India and the US, and Gutenberg header, footer and trademark text removed (VN-5).
- **CNT-04 MUST** Per-item Credits and a Licences screen in Videos and Reader show licence name, URI, author, source and changes as plain non-tappable text; licence texts ship in the pack; the portal shows live links.

**Packs and Tier 1**
- **CNT-05 MUST** Content ships only as signed packs (§4.3) published after two staff approvals (as BE-43). ZuneUpdater verifies signature and each SHA-256 before install and keeps the old pack on failure; downloads need an unmetered network unless the parent allows mobile, resume with Range, and fetch an "essentials" subset first.
- **CNT-06 MUST** A revoked item disappears from Videos and Reader within 24 h of a manifest and 10 s of a policy `content.deny`.
- **CNT-07 MUST** Tier 1 plays in `app.zune.videos` by Media3 from `ContentStoreProvider` only; its `DataSource.Factory` rejects `http(s)`; it works offline.
- **CNT-08 MUST** Topic requests run on the device (SQLite FTS5 over `catalog.json`); query text never leaves it. No match shows "Not here yet" and Ask a grown-up, which sends `approval.request{kind:"topic"}` (BE-16); the parent may forward the phrase to editors without child identifiers.
- **CNT-09 SHOULD** Launch floors [INFERRED]: staff pilot 10 h of Tier 1 per band; external families 40 h [R06 §4.1], 6 h or more in 13-14.

**Tier 2 (YouTube)**
- **CNT-10 MUST** Off by default. On only when the global flag is on, the parent has accepted YouTube's Terms of Service, its privacy policy and our notice (consent purpose `third_party_video`, BE-30), and CNT-11 passes.
- **CNT-11 MUST** A video starts only if `caps.videos_tier2=1`, signed `tier2/state` is under 15 min old and `enabled`, the id is not revoked or denied, WebView is at least `min.webview` (OS-29), the band allows it, and the network is unmetered or the parent allowed mobile. Offline means unavailable.
- **CNT-12 MUST** `ytcheck` calls `videos.list` at publish and nightly (50 ids per call). An item stays live only if `status.madeForKids=true`, `embeddable=true`, `privacyStatus=public`, not live, no IN region block; any change or missing field delists within 24 h.
- **CNT-13 MUST** One WebView, one page `https://player.<zone>/v1/player.html#<videoId>`, one `YT.Player` iframe, with `autoplay=0`, `rel=0`, `fs=0`, `disablekb=1`, `playsinline=1`, `iv_load_policy=3`, `origin` set. The id matches `^[A-Za-z0-9_-]{11}$` and is in the catalog.
- **CNT-14 MUST** Navigation is locked (§4.4): top-frame navigation away from the page, new windows, non-http schemes, file and content access are denied; sub-resources load only from `tier2-hosts.yaml`; the only bridge is a `WebMessageListener` on the player origin.
- **CNT-15 MUST** Off-script guard: the page reads `getVideoUrl()` on each state change and each second; a changed id, `ENDED` or error 100, 101, 150 or 153 destroys the player within 1 s, tells the app and is counted. This blocks related-video taps (`rel=0` still shows same-channel videos [R06 §2.3]).
- **CNT-16 MUST** No overlay or shield on the player rectangle; no ad or tracker blocking inside allowed hosts; no download or offline copy; `LOAD_NO_CACHE`; cookies and storage cleared per session; third-party cookies off; no audio-only or background play.
- **CNT-17 MUST** Tier 2 tiles show our title, topic icon and duration; no YouTube thumbnail, title or channel name is stored; API-derived fields purge at 30 days [R06 §2.3].
- **CNT-18 MUST** Kill: `kill_state` `videos_tier2` (global scope needs two approvals, BE-15) removes the player on a connected device in 10 s and Tier 2 hosts from `dns/allowlist.yaml` within 1 h; decision-to-effect target 15 min [INFERRED].
- **CNT-19 MUST** Drop rule: Y0 is the day the YouTube request is filed (by W2, PRE-18). At Y0+56 days without a written yes to YQ1-YQ3 (§4.5), or on any refusal: flag false for good, `TIER2=false` at compile time, Videos out of `webview_callers.xml`, hosts removed, portal toggle hidden, ADR written.
- **CNT-20 MUST** A child Report button outside the player quarantines the item fleet-wide until a 24 h review (5 per device per day [R06 §4.2]). Parent control is block-only (`content.deny`: `video:`, `topic:`, `src:yt`); no parent-added channels or URLs.
- **CNT-21 MUST** Tier 2 is never a paid or tiered feature [R06 §2.2].

**Curation**
- **CNT-22 MUST** Curation runs in the staff console (05 §4.8), roles `content` (editor) and `content_lead` (approver), different people, audited. Editors view Tier 2 items only in the official embed; no download, scraping or extraction tools [R06 §2.3]. `ytcheck` runs nightly; 10% of items are re-reviewed quarterly; licence evidence is re-fetched yearly and on terms changes.

**Weather**
- **CNT-23 MUST** Weather has no location permission and talks only to `weather.<zone>`. Places come from the portal's GeoNames India picker; coordinates snap to 0.05 degrees before any vendor call; no device, family or child id goes upstream; one company `User-Agent` with a contact address.
- **CNT-24 MUST** Adapters: Open-Meteo on a paid commercial plan (never the free API); MET Norway as automatic fallback; IMD off until an agreement, then from one fixed egress IP only; Google Weather API never.
- **CNT-25 MUST** `/bundle` serves only `place_id` values in the calling device's child places, rate-limited per device, with `attribution[]`, `valid_until`, `degraded` [R14 §4.1].
- **CNT-26 MUST** SACHET CAP is polled at most once per 5 min, with ETag; alerts map through reviewed `alert-map.yaml` and an unmapped event alarms; child text is authored; official text is labelled "Official text, links removed"; no alert string holds a URL.
- **CNT-27 MUST** Weather never suppresses the OS cell-broadcast alert. It shows a calm banner and safety card, plus at most one low-importance notification per CAP identifier for class `warning`, outside bedtime, with no sound override. Parent copy says Weather alerts cover the places set and the phone's own emergency alerts follow the phone.
- **CNT-28 MUST** AQI shows a CPCB category from a station within 25 km [INFERRED], with station and time; otherwise AQI is hidden.
- **CNT-29 MUST** Authored pack: 8 explainers x 3 bands and 6 safety cards (heat wave, lightning, cyclone, flood, air quality, cold wave), each tagged `std` and with a check question. It signs only with `REVIEW.json` entries from a science-education reviewer and an Indian meteorologist, and a passing reading-level lint (grade 4, 6, 8 [INFERRED]).
- **CNT-30 MUST** No LLM call inside Weather. "Ask why" sends explainer ids and condition values, never a place name, to Assistant.
- **CNT-31 MUST** Metric, IST, English; no map in Stage 1 (boundary depiction is legally sensitive [R20 §2.5]); stale data reads "Updated N h ago" up to 12 h, then "Can't update".

**Reader**
- **CNT-32 MUST** `app.zune.reader` declares no `INTERNET`, no cleartext, no `ACTION_VIEW` of http(s); CI checks the built APK.
- **CNT-33 MUST** Readium Kotlin `EpubNavigatorFragment` pinned to the version recorded at Z5 start (R09: 3.4.0); external links inert; the system TTS voice-install flow never called.
- **CNT-34 MUST** Ingest and open reject EPUBs with `<script>`, `<iframe>`, `<object>`, remote URLs, external entities or oversize files; blocked requests are counted.
- **CNT-35 MUST** A title appears only if its band matches and the parent approved it (`content.allow` holds `book:` or `shelf:<band>`; the portal's "Approve starter shelf" is one explicit action); deny wins.
- **CNT-36 SHOULD** Weather exposes a read-only `content://app.zune.weather.tile/summary` (temperature, condition id, icon id, updated-at, place label) to `app.zune.launcher` only, caller-checked by package and `zune-apps` digest, for 09 APP-11; it returns the last cached value and nothing when suspended or absent.

## Design and build instructions

### 4.1 Components and paths

```
zune/backend/content/   cmd/{ingest,packbuild,ytcheck,curate}  player/v1/{player.html,player.js}   # curate = staff-console API: queue, review form, two-reviewer approval, delist, licence rows
                        tier2-hosts.yaml  sources.yaml  schema/{catalog-v1,licence-v1}.json  data/
zune/backend/weather/   adapters/{openmeteo,metno,imd,sachet,cpcb}  alert-map.yaml  thresholds.yaml  content/{explainers,cards,REVIEW.json}
zune/apps/{videos,weather,reader}/    zune/apps/updater/ (04) gains ContentStoreProvider
```
`player.<zone>` is a static, cookie-free hostname routed to `content`, separate from the portal origin (BE-39).

### 4.2 Catalog and licence register

```json
{"id":"v_8f3k2","kind":"video|book","tier":1,"src":"file|yt","src_id":"<sha256>|<11-char id>","licence_id":"lic_12",
 "title":"<=60 chars, ours","age_min":7,"age_max":10,"bands":["7-9","10-12"],"topics":["water-cycle"],
 "std":[{"board":"NCERT","class":5,"subject":"evs","theme":"water"}],"in_rating":"U","dur_s":412,"flags":[],
 "reviewers":["u1","u2"],"status":"live|quarantined|delisted","yt":{"mfk":true,"embeddable":true,"checked_at":"..."}}
```
`licence_register(id, source, licence, licence_url, attribution, commercial_ok, derivatives_ok, share_alike, evidence_sha256, evidence_at, counsel_status, deal_ref, pd_basis, recheck_at)`.

Sources (unverified, VN-4, VN-5): in after checks: NASA media (no logos), Blender films (CC BY 3.0), StoryWeaver (CC BY 4.0, Pratham's written yes first), ISRO (verbatim, attributed), Wikimedia Commons per file, Standard Ebooks and Gutenberg (CNT-03; NASA and ISRO text enters Reader only as verbatim EPUBs we build); conditional: Oak (OGL v3.0, UK curriculum), DIKSHA per item; paid written deals, hosted as files: Khan Academy, TED-Ed, Britannica, Indian children's channels; Stage 2: PhET, Wikipedia.

### 4.3 Packs and delivery

Pack = `manifest.json` plus detached signature by the `content` key (algorithm as `channel`, 05 V2): `files[{id,path,sha256,bytes}]`, `catalog_sha256`, `revoked[]`, `kid`, `ver`. Video: H.264 480p MP4 `faststart`, AAC, English WebVTT if available, about 0.4 GB per hour [R06 §2.6, INFERRED]. Books: EPUB plus OPDS 2.0 `library.json`. Weather: `explainers.json`, `cards.json`, `rules.json`, also bundled in the APK. Packs are per band over a shared file store.

```
packbuild -> S3 zune-content (ap-south-1) -> CloudFront dl.<zone>  (tokened URLs, REL-20)
ZuneUpdater: manifest -> verify sig (key pinned in /system_ext/etc/zune/content_pub_*.pem) -> fetch missing (Wi-Fi, Range)
  -> verify sha256 -> atomic swap -> delete revoked
ContentStoreProvider (a read-only provider inside `app.zune.updater`, authority `app.zune.content`): caller in {videos,reader,weather} AND zune-apps cert digest
  -> openFile(id) | catalog(); else SecurityException
```

### 4.4 Tier 2 player

```kotlin
// settings: javaScriptEnabled, allowFileAccess=false, allowContentAccess=false, setSupportMultipleWindows(false),
//   cacheMode=LOAD_NO_CACHE, mediaPlaybackRequiresUserGesture=true, third-party cookies off; CNT-11 checked before load
shouldOverrideUrlLoading = { r -> r.url.toString() != pageUrl }                 // deny all but our page
shouldInterceptRequest   = { r -> if (Tier2Hosts.allows(r.url.host)) null else blockedResponse() }
onCreateWindow = false;  addWebMessageListener("zune", setOf(PLAYER_ORIGIN)) { type, code -> /* state|error|off_script */ }
fun end() { loadUrl("about:blank"); clearCache(true); WebStorage.getInstance().deleteAllData(); CookieManager.getInstance().removeAllCookies(null) }
```
`tier2-hosts.yaml` is measured, not copied from firewall guides [R06 §2.3]: log every host the page requests on a dev Pixel and in headless Chromium, dated, re-measured monthly. It includes Google's ad hosts (blocking them is ad blocking); ad clicks open new windows or top navigations and are refused (YQ2). `Referrer-Policy: strict-origin-when-cross-origin` keeps our origin visible and avoids Error 153.

### 4.5 YouTube rules that collide with Zune, and the decision each needs [S; VN-1]

| YouTube rule | Zune element | Choice | Decision |
|---|---|---|---|
| No overlay over the player | R04 touch shield | Dropped; client blocks navigation | None |
| Do not disable player links | D2 | We refuse navigation | YQ2. Default (D25): D2 wins; if links must work, drop Tier 2 |
| No ad blocking; MFK embeds carry ads | DNS allowlist | Ad hosts allowed | Accept ads; parent notice; kill on an ad incident |
| No charging, gating, download, offline or background play; derived metrics need amendment | PIN, time locks, paid product, offline mode, age labels | Tier 2 unpriced, online only, human labels | YQ3, YQ4 |
| MFK per video; tracking off; child-privacy duties | Disclosure to Google | CNT-10, CNT-12 | Counsel (DPDP); designation at Y0 |

Filed at Y0 with the YouTube API Services form [R06 §4.4]: **YQ1** may a child-directed commercial OS embed MFK-only videos; **YQ2** may we refuse navigation out of the player; **YQ3** are playback-control overlays, PIN and time locks acceptable; **YQ4** do human labels count as derived metrics; **YQ5** is there a device-partner route without GMS; **YQ6** is the audit form needed at default quota. Planned filing 2026-10-19 (W2, nothing filed yet), so Y0+56 days is 2026-12-14.

### 4.6 What the child sees

Tier 2 off: Videos shows Tier 1 shelves (topic icons, then band) and search over Tier 1, nothing greyed or hinting at online videos; a search matching only Tier 2 gives "Not here yet". Switched off mid-playback: the player goes in 10 s with "That video isn't available right now". Tier 2 on: its tiles join the shelves; Report sits below the player.

### 4.7 Curation, quota, cost

Workflow: channel vetting, editor review, second reviewer (always for `age_min` 8 or less and new channels), publish, nightly check. Review form: accuracy, band fit, accent, frightening content, product placement, religion, caste, communal sensitivity. At about 35 videos per editor-day [R06 §4.2], 240-400 videos (40 h) is 14-23 editor-days double-reviewed. YouTube: `videos.list` costs 1 unit per call, so N items cost ceil(N/50) per night against 10,000 a day; `search.list` (100 units) is editor-only [R06 §2.3]. Tier 1 transfer cost = devices x GB each x CDN price. Open-Meteo calls per month = cells x refreshes x 30; 100 cells x 16 x 30 = 48k, far below the 1M Standard plan [R20 §2.5, unverified]; alarm at 70%.

### 4.8 Weather

```
GET /v1/weather/places                    -> [{place_id,label,district,state}]    (the child's places only)
GET /v1/weather/places/{place_id}/bundle  -> {schema:1,current,hourly[48],daily[7],sun,uv,aqi:{cpcb:{cat,station,at}|null},
   alerts[{id,src:"sachet|imd",event,cls:"warning|advisory",kid_text,official_text,onset,expires}],updated_at,valid_until,degraded,attribution[]}
```
`weather_place(place_id,geoname_id,name,district,state,lat_q,lon_q,tz)` comes from GeoNames (CC BY 4.0 [R14 §4.1]). Redis cell cache with single-flight, circuit breaker, stale-while-error; TTLs current and hourly 60 min, daily 3 h, alerts 5 min. The app refreshes on open and hourly (WorkManager), every 15 min during a `warning` [INFERRED]. `weather` egresses through the allowlist proxy on one Elastic IP (IMD allowlisting [R20 §2.5]).

Alert path: SACHET poll; match by polygon if the CAP has one, else by district name through a reviewed table, else drop and alarm; `alert-map.yaml` maps CAP event to card and class (Extreme or Severe, or IMD orange or red, is `warning`); `notify` (05) tells guardians once per identifier, with no child name; CAP `Update` and `Cancel` follow `references`; IMD colour always has a text label.

On-device `rules.json` (at most 3 chips): rain code plus high low-cloud -> rain; `uv>=3` -> sun safety, escalating at 6; dew point above `sticky_dew_c` -> humidity; pressure fall over `pressure_drop_hpa_3h` (3 [R14]) -> pressure. The meteorologist sets every threshold except UV and pressure before signing. Explainers: clouds, rain and water cycle, monsoon and seasons, thunder and lightning, wind and cyclones, heat and dew point, UV and sun safety, air quality and haze. Card template: what it is, what to do now, what not to do, tell a grown-up; no red flashing, countdown or catastrophe imagery.

### 4.9 Reader

Compose hosts the legacy `EpubNavigatorFragment` (the Compose navigators are experimental [R09 F6]). Readium's in-process interception serves publication resources; every other request is blocked and counted; external-link callbacks are no-ops. Read-aloud with sentence highlight (voice-first at age 7) is a SHOULD through 07's engine; reading progress stays on the device. `library.json` (OPDS 2.0) holds source, licence, attribution, band, reading level, flags. Books open through `ContentStoreProvider`; if Readium cannot open `content://` (VN-6), the provider copies the hash-checked file into Reader's private directory.

### 4.10 Interfaces other sections must provide

- 03: capabilities `weather`, `reader`; policy `content{allow,deny,mobileOk}`; `kill.features` incl. `videos_tier2`; Guardian sets `DISALLOW_CONFIG_CELL_BROADCASTS` [R14 §2.3].
- 05: host `player.<zone>`; role `content`; purpose `third_party_video`; signed `GET /v1/content/tier2/state`; `egress.yaml` for `sachet.ndma.gov.in`, `api.met.no`, Open-Meteo, `data.gov.in`, IMD, `www.googleapis.com` [MEMORY]; a Guardian-minted short-lived device token for REST calls by Tier B apps and ZuneUpdater.
- 04: content-pack artifact class (`type: content`, REL-23) and the `content` key (§4.4 inventory), both added; the provider lives in `app.zune.updater` (§4.3).
- 02: `internet-holders.txt` gains `app.zune.videos`, `app.zune.weather`; CellBroadcastReceiver stays (OS-09) with RRO `link_method=none`, `enable_text_copy=false`, toggles hidden, MCC 404/405 kept.
- 07: "ask why" intent. 09: shelves, Weather tile.

## Acceptance criteria and tests

- **CNT-T01** `ingest` rejects an item with no licence row, `commercial_ok=false` or an excluded source; a Gutenberg file keeps no trademark header; Credits and Licences screens show every shipped licence and URI as untappable text, the portal page has live links.
- **CNT-T02** A tampered file, bad signature or truncated download leaves the old pack; a revoked id leaves both apps in 24 h, in 10 s via `content.deny`.
- **CNT-T03** In airplane mode Tier 1 plays and a "volcano" search returns hits; no query text leaves the device; an `http` URL fails in the `DataSource`; a no-match query sends one `topic` approval.
- **CNT-T04** Tier 2 refuses to start for each failing condition of CNT-11 (policy off, stale state, revoked, old WebView, metered, offline).
- **CNT-T05** A test MFK video plays; `ytcheck` delists a non-MFK, private or non-embeddable test id on its next run.
- **CNT-T06** Tapping the YouTube logo, title, an ad or a related video opens no window or other page; a changed id or `ENDED` removes the player within 1 s and increments a counter.
- **CNT-T07** `videos_tier2` kill removes the player in 10 s on a Pixel and hosts leave DNS within 1 h; no app view overlaps the player; cache and cookie stores are empty after a session; the drop runbook, run in staging, leaves no `youtube` string in the release APK or `webview_callers.xml`.
- **CNT-T08** Weather has no location permission (`aapt`) or map view; a foreign `place_id` returns 403; a vendor outage falls back to MET Norway with `degraded=true`; AQI is hidden with no CPCB station in range.
- **CNT-T09** A replayed SACHET fixture gives one notification per identifier, no URL in any string and an alarm on an unmapped event; Cancel clears the banner.
- **CNT-T10** CI rejects a weather pack missing a sign-off or failing reading-level lint; children 7-9 finish the check questions unaided at 80% or more [R09 §4.4].
- **CNT-T11** Reader APK has no `INTERNET`; a hostile EPUB (script, iframe, remote image, external link) renders inert and is counted; an unapproved title is invisible.

## Verify first

| ID | Claim | Why uncertain | How to verify | If false |
|---|---|---|---|---|
| VN-1 | YouTube rules in §4.5, `status.madeForKids` and `embeddable` fields, `videos.list` 1 unit, `search.list` own bucket, 30-day cache, child-directed designation [R06, summaries] | Official pages unread | Read the developer policies, required minimum functionality, policy answer 9664901, API docs; file YQ1-YQ6; call `videos.list` on test ids | Adjust CNT-10 to CNT-21; if links must work, drop Tier 2 (CNT-19) |
| VN-2 | Our origin keeps Referer (no Error 153) in Vanadium WebView; playback works with third-party cookies off; `addWebMessageListener` works; `getVideoUrl()` exposes related-video switches; host list is stable; YouTube may refuse stale Chromium [R06 F4, §2.3, I] | Untested; hosts drift | Dev Pixel, MFK test video, monthly host measurement | `loadDataWithBaseURL` origin; other state polling; domain-level allowlist; else drop Tier 2 |
| VN-3 | ZuneUpdater can verify and serve packs; the caller-certificate check works; Guardian mints REST tokens [I] | Design assumption | Z5 spike on Pixels | Provider moves to a Tier A component; tell 04, 05 |
| VN-4 | Oak OGL covers a paid product; NASA, ISRO, StoryWeaver (bulk, in-app), Blender, Wikimedia terms allow this use [R06 §2.5, R20 §2.4, S] | Pages blocked | Archive each page; written confirmations from Oak, Pratham, ISRO; counsel | Remove the source |
| VN-5 | A plain-text licence URI satisfies CC BY attribution without a browser; IT Rules 2021 Part III ratings apply [R20 S]; public-domain basis in India (life plus 60 years [MEMORY]); Gutenberg trademark terms | Counsel questions | Counsel; Gutenberg terms | Summary text on screen, links in portal; `in_rating` internal; pre-cleared authors only |
| VN-6 | Readium 3.4.0 (BSD-3, interception, `content://` open, external-link hook, script handling), Media3 1.11.1 current, 480p H.264 plays on both Pixels [R09 F6, S] | Mirrors and docs | Read source at the pinned version; hostile EPUB; play test | Copy to private file; patch or native renderer; pin newest |
| VN-7 | SACHET feed URL, ETag, area format, events, languages, licence; CPCB data on `data.gov.in` (registration, licence, coverage, bands); IMD terms, charges, fixed-IP rule [R20 S, MEMORY] | Unread | Sample the feed 30 days; register; read terms; write to IMD | District-name matching; hide AQI; SACHET only |
| VN-8 | Open-Meteo Standard price, call weighting, commercial host, attribution rule; MET Norway terms [R14, R20 S] | Pages blocked | Read terms; subscribe; test | Professional plan or self-host [R14] |
| VN-9 | Cell broadcast in Google's tree: `always_on`, `link_method`, `enable_text_copy`, toggle flags, `DISALLOW_CONFIG_CELL_BROADCASTS`, MCC 404/405, carrier acceptance of non-tappable text [R14, R20] | Mirrors only | Read `packages/modules/CellBroadcast` at the tag; SACHET test alert | Patch the APEX; tell 02 |
| VN-10 | NCERT class-to-age (about class 2 to 9 for ages 7-14), theme titles, UV 3 and 6, CPCB bands [MEMORY]; a 40 h pack is about 16 GB over hand-over Wi-Fi; every other [INFERRED] value | Memory, estimates | Education lead and meteorologist; measure at Z5 | Tag by theme; reviewer sets values; smaller essentials subset |

## Risks, open gates and out of scope

1. **Thin India-fit open video**, especially 13-14; floors (CNT-09) may fail without paid partners.
2. **YouTube may refuse or stay silent**; launch does not depend on it (D25).
3. **Related-video and ad exposure** in the embed is reduced (CNT-15), not removed.
4. **Weather safety-text errors**: authored, two reviewers, no LLM.
5. **Public-domain misjudgement** (India versus US); **WebView update burden** (02 OS-28).
6. **Heavy first download** on Indian mobile data (CNT-05, VN-10).

Gates:
- **[GATE: before build]** Pin Readium, Media3, `androidx.webkit` at Z5 start; VN-2 and VN-6 spikes recorded.
- **[GATE: before staff pilot]** YouTube request filed by W2; licence register `cleared` for the pilot pack; weather pack signed by both reviewers; VN-9 passed.
- **[GATE: before external family]** Counsel on Tier 2 third-party consent (DPDP), IT Rules ratings, public-domain method; written confirmations (Pratham, ISRO, Oak if used); Tier 2 approved in writing or dropped (CNT-19).
- **[GATE: before charging]** Paid partner licences signed; Tier 2 in no price (CNT-21); IMD agreement only if IMD data is promised.

Out of scope: Hindi (D20), PhET, Wikipedia, NCERT text, parent-added channels, watch history, GNSS, sensors, weather maps, music, coding, on-device LLM.
