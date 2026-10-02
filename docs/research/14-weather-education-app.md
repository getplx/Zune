# Zune research 14: Weather app that teaches children about weather

Date: 2026-10-02. Scope: D9 in `docs/REQUIREMENTS.md`. Tags: **[PRIMARY]** read in a real source file or primary page this session (URL or repo@ref:path); **[SECONDARY]** reputable page or search summary; **[INFERRED]** my engineering judgement; **[MEMORY]** training knowledge, unchecked.
Access note: android.googlesource.com is still 403 (tested once, not retried). weather.gov, api.weather.gov, api.met.no, open-meteo.com, openweathermap.org, tomorrow.io, ftc.gov, nextgenscience.org, noaa.gov and nasa.gov were also blocked, so vendor terms come from GitHub sources of the vendors' own sites where possible (Open-Meteo), from cloud.google.com (reachable), and otherwise from search summaries tagged SECONDARY. Reports 01-04, 12 and 13 existed when I wrote this; 05-11 did not.

## 1. Summary & recommendation

- **Backend-proxied, cached, coarse-location weather.** Devices only call the Zune backend (a `weather` module in report 13's Go service). The backend talks to vendors from one server identity with coordinates snapped to a ~5 km grid; no device ID, account ID or precise coordinate goes upstream.
- **Open-Meteo (paid commercial plan) primary, MET Norway fallback, NWS for US alerts.** Open-Meteo's free API is non-commercial only, so Zune must subscribe or self-host. It has the richest teaching variables (cloud layers, CAPE, pressure, UV, dew point), and its AGPL code can be self-hosted commercially, which is the exit if the vendor changes terms [PRIMARY]. **Google Weather API is ruled out**: its terms forbid use "in a weather app" [PRIMARY].
- **Stage 1 location is parent-set (city/ZIP in the portal), not device location.** AOSP has no network location provider, GrapheneOS's calls Apple's undocumented endpoint, and Mozilla Location Service is dead. Parent-set places avoid collecting child geolocation. Alerts for the child's *actual* position come from the OS's network-geotargeted WEA.
- **Keep CellBroadcastReceiver in the image, with one overlay** (`link_method=none`). The Weather app never replaces the OS alert UI; it adds a calm follow-up card and safety actions and notifies parents.
- **Education is authored, not generated:** 20 vetted explainers in three age bands, triggered on device by live conditions, plus 6 safety cards. Open "why" questions go to the Assistant (report 07), grounded in the same pack and parent-visible. No LLM inside Weather.
- **Sensors are optional**; Stage 1 does not depend on them.
- **Cost is small but not zero**: tens to low hundreds of dollars a month in beta; at 100k devices plan on an Enterprise quote or self-hosting.

## 2. Findings

### 2.1 Data sources (commercial, child-directed product)

| Source | Coverage / commercial terms | Caching, alerts, extras | Cost: beta / 10k / 100k devices (assumptions below) | Verdict |
|---|---|---|---|---|
| **Open-Meteo** | Global. Free tier: <10,000 calls/day, non-commercial only; "apps that have subscriptions" and "commercial products" count as commercial. Subscription grants commercial licence; data CC BY 4.0 [PRIMARY] | Data may be cached (CC BY). No alerts. Cloud layers, CAPE, freezing level, pressure, dew point, UV, US AQI, sunrise/sunset, 80-year history; pollen Europe only [PRIMARY] | Call budgets per month: Standard 1M, Professional 5M, Enterprise 50M+ [PRIMARY]; about $29 and $99 for the first two [SECONDARY, Stripe table unreadable]. 10k: Professional. 100k: Enterprise quote or self-host | **Primary** |
| **MET Norway Locationforecast** | Global, CC BY 4.0/NLOD, free incl. commercial; unique User-Agent mandatory (generic gets 403); contact before >20 req/s [SECONDARY] | Must honour Expires/If-Modified-Since. Alerts Norway only. Cloud fractions, UV clear-sky | $0 at fallback volumes | **Fallback** |
| **NWS api.weather.gov** | US only. "Public domain... any lawful purpose" if you do not claim it as yours, imply endorsement, or alter then present as official [SECONDARY, weather.gov/disclaimer]. User-Agent with contact email required; limits undocumented, retry after ~5 s [SECONDARY]; API key planned, free access to continue [SECONDARY] | HTTP caching headers; 2.5 km grid; coordinates max 4 decimals; `/points` then `/gridpoints` two-step [PRIMARY weather-gov/api@694ed0f:general-faqs.md]. Alerts as GeoJSON/CAP incl. `event`, `severity`, `urgency`, `instruction`. No UV, no pressure forecast | $0 at any scale (6.3M calls/month is ~2.4 req/s, vs undocumented limits) | **US alerts**; forecast backup |
| OpenWeather One Call 3.0 | Global, ODbL-based, on-screen attribution [SECONDARY] | Alerts, AQ, UV | 1,000 calls/day free, then ~EUR 0.0014/call [SECONDARY, sources disagree]: ~EUR 1.8k (10k) / 8.8k (100k) a month | Reject (cost) |
| Tomorrow.io | Free plan: commercial use prohibited for evaluation/self-generated accounts [SECONDARY] | Minutely, alerts | From ~$50 [SECONDARY] | Reject |
| WeatherAPI.com | Global; free tier reportedly allows commercial use [SECONDARY, unverified] | Alerts, AQ, astronomy | Reported $7/3M, $25/5M, $65/10M calls [SECONDARY] | **Plan B**; read ToS first |
| Visual Crossing, Meteomatics | Visual Crossing: commercial incl. free tier ≤1,000 records/day, $0.0001/record; Meteomatics: sales-quoted [SECONDARY] | 50-year history (VC) | See terms | Stage 2 history option / skip |
| **Google Weather API** | Terms §21.1: may not use content "in a weather app or weather model whose primary purpose is to provide weather information"; §21.2 caching 1 h (current/hourly), 24 h (daily), alerts 1 h [PRIMARY, Service Specific Terms, last modified 2026-06-10] | Alerts yes | ~$0.15/1,000 after 10k free/month [SECONDARY] | **Unusable**; also contradicts A3 |
| ECCC (Canada), DWD/ICON (Germany), ECMWF open data | Open licences permitting commercial use with attribution (ECCC end-use licence; DWD GeoNutzV/CC BY; ECMWF CC-BY) [SECONDARY; Open-Meteo licence page lists them PRIMARY] | Raw model/CAP feeds; Open-Meteo already ingests them | n/a | Stage 2 per-country alerts |

Cost assumptions [INFERRED]: distinct 0.05-degree place cells ≈ 0.3 x devices at 10k and 0.15 x at 100k (US metro clustering); demand-driven hourly refresh over 14 waking hours = ~1.3M (10k) / ~6.3M (100k) raw calls per month. The pricing page's calculator weights a call (10 variables over 14 days = 1 unit, scaling with variables x models) [PRIMARY]; if plan budgets use the same weights, our ~25-36 variables mean 2.5-3.6 units per call, so 3-4.5M and 16-23M units. Whether plan budgets apply that weighting is unconfirmed.

**Self-hosting Open-Meteo**: "available for non-commercial and commercial use"; the Docker image pulls CC-BY-4.0 data from Open-Meteo's S3; 8 GB RAM minimum (16 recommended), 100 GB NVMe; code AGPL-3.0 [PRIMARY open-meteo/open-meteo@b06f476:docs/getting-started.md]. **Vendor risk**: Open-Meteo may change terms "effective immediately" and end a subscription "with or without notice"; Swiss law; logs "may contain geographical coordinates", kept 90 days; no child-specific clause [PRIMARY open-meteo-website@a8dd5c8:src/routes/en/terms/+page.svelte]. Attribution requires "a link next to any location Open-Meteo data are displayed" [PRIMARY ...licence/+page.svelte]; under D1/D2 that means plain text on device and the live link in the parent portal (decision 6).

### 2.2 Location without GMS

- AOSP has no network location provider. GrapheneOS ships its own `NetworkLocation` app (MIT) that holds `INSTALL_LOCATION_PROVIDER` and queries **Apple's undocumented `gs-loc.apple.com/clls/wloc`** or a GrapheneOS proxy of it [PRIMARY GrapheneOS/platform_packages_apps_NetworkLocation@17 (474472e):src/.../ApplePositioningService.kt, AndroidManifest.xml]. A commercial child product should not depend on an unlicensed Apple endpoint [INFERRED].
- Mozilla Location Service has returned 403 since 2024-03-27. Its successor BeaconDB is "experimental... may be inaccurate", with an MLS-compatible API [SECONDARY https://beacondb.net/, https://github.com/beacondb/beacondb]. Self-hosted Ichnaea would need our own Wi-Fi corpus [INFERRED]; IP geolocation is city-grade at best [MEMORY].
- COPPA: "geolocation information sufficient to identify street name and name of a city or town" is personal information, unchanged by the 2025 amendments; compliance date 2026-04-22 [SECONDARY https://www.federalregister.gov/documents/2025/04/22/2025-05904/childrens-online-privacy-protection-rule]. Zune already collects PI (accounts, messages), so full COPPA applies; the aim is not to add child geolocation. Legal reading belongs to report 11.

### 2.3 Alerts

- The Android 17 tree includes `packages/apps/CellBroadcastReceiver` and `packages/modules/CellBroadcastService` [PRIMARY GrapheneOS/platform_manifest@17:default.xml lines 738, 799]; cell broadcast ships as the `com.android.cellbroadcast` Mainline APEX, and that design "streamlines carrier testing" because OEMs cannot modify it [SECONDARY https://source.android.com/docs/core/ota/modular-system/cellbroadcast]. Report 12 already keeps it.
- FCC: carriers handle four alert classes (National, Imminent Threat, AMBER, Public Safety); National Alerts cannot be opted out [SECONDARY https://www.federalregister.gov/documents/2025/03/18/2025-04125/wireless-emergency-alerts-emergency-alert-system]. NWS products that trigger WEA include Tornado Warning, Flash Flood Warning (considerable/catastrophic only), "destructive" Severe Thunderstorm Warning, Extreme Wind, Hurricane/Typhoon, Tsunami and Dust Storm [SECONDARY https://www.weather.gov/news/072221-svr-wea].
- **Two defaults to change.** CellBroadcastReceiver defaults `link_method` to `smart_linkify` (tappable URLs in alert text); the string is overlayable [PRIMARY GrapheneOS/platform_packages_apps_CellBroadcastReceiver@17 (59d96c7):res/values/config.xml:266, overlayable.xml:108, CellBroadcastAlertDialog.java getLinkMethod]. Set `none` via RRO (report 04 row 6 already wants no auto-link in CB). Several channels carry `override_dnd=true` (config.xml:126-129), so emergency alerts can sound at night; keep, but tell parents.
- Unverified: device-side geofencing lives in CellBroadcastService (source unreadable here). Its behaviour with no network location provider needs a device test.

### 2.4 Education design and content sources

- **NGSS codes verified** [SECONDARY, nextgenscience.org pages surfaced by search]: K-ESS2-1 (observe local weather patterns), K-ESS3-2 (purpose of forecasting for severe weather), 3-ESS2-1 (tables/graphs of seasonal weather), 3-ESS2-2 (climates of regions), 3-ESS3-1 (weather-hazard design solutions), 5-ESS2-1 (Earth-systems interactions; it does not say "water cycle"), MS-ESS2-4 (water cycling), MS-ESS2-5 (air masses and weather), MS-ESS2-6 (unequal heating, rotation, circulation).
- **England National Curriculum has no codes**; statements: Year 1 science "observe changes across the four seasons... weather associated with the seasons"; KS1 geography "seasonal and daily weather patterns in the United Kingdom"; Year 4 "evaporation and condensation in the water cycle" [SECONDARY https://assets.publishing.service.gov.uk/media/5a806ebd40f0b62305b8b1fa/PRIMARY_national_curriculum_-_Science.pdf]. UK alignment is Stage 2 (UK launch is a separate legal workstream, report 13).
- **Licences.** US federal works are generally public domain unless a credit says otherwise [SECONDARY https://library.noaa.gov/blogs/news-research-highlights/question-of-the-quarter-noaacopyright]; NWS name/logo are trademarks. NASA content is generally not copyrighted, but its insignia and marked third-party items are not [SECONDARY https://climatekids.nasa.gov/image-use/]. Most Met Office web content is reusable under the Open Government Licence with attribution [SECONDARY https://www.metoffice.gov.uk/policies/open-data-policy]. Wikimedia Commons mixes licences including CC BY-SA, so review per asset [MEMORY]. Use Owlie Skywarn facts, not the character, until cleared [INFERRED].
- **LLM vs authored.** RAG over curated sources reduces but does not remove hallucination [SECONDARY https://www.sciencedirect.com/science/article/pii/S2666920X25000578]. A wrong sentence about tornado or lightning safety is unacceptable, so safety content is authored.
- **Climate anxiety.** In a 10-country survey of 10,000 people aged 16-25, 75% said "the future is frightening" [SECONDARY https://researchportal.bath.ac.uk/en/publications/climate-anxiety-in-children-and-young-people-and-their-beliefs-ab/]. Guidance: age-appropriate amounts, validate feelings, action-oriented framing [SECONDARY https://www.apa.org/monitor/2025/06/youth-climate-anxiety-action].

### 2.5 Android platform

- Environment sensors "are not always available" except light; types include `TYPE_PRESSURE`, `TYPE_AMBIENT_TEMPERATURE`, `TYPE_RELATIVE_HUMIDITY` [PRIMARY https://developer.android.com/develop/sensors-and-location/sensors/sensors_environment]. Pixel 9a and 10a list a barometer [SECONDARY https://support.google.com/pixelphone/answer/7158570]; for Snapdragon devices it varies by model, region and year (Galaxy S25 and Xiaomi 15 list one; OnePlus 13 regional specs differ; Motorola Edge varies by year) [SECONDARY, GSMArena search summaries]. D13 makes this a per-device capability check.
- **WorkManager needs no GMS**: `createBestAvailableBackgroundScheduler` returns `SystemJobScheduler`, and work-runtime's `build.gradle` has no play-services/gcm/firebase dependency [PRIMARY androidx/androidx@androidx-main:work/work-runtime/src/main/java/androidx/work/impl/Schedulers.java; work/work-runtime/build.gradle]. Minimum periodic interval is 15 minutes [PRIMARY https://developer.android.com/develop/background-work/background-tasks/persistent/getting-started/define-work]. `updatePeriodMillis` for AppWidgets is at least 30 minutes [PRIMARY https://developer.android.com/develop/ui/views/appwidgets/advanced].

## 3. Options & trade-offs

| Decision | Choice and why |
|---|---|
| Primary provider (vs NWS-only, WeatherAPI, OpenWeather) | **Open-Meteo.** NWS lacks UV, pressure and cloud layers, is US-only, and has undocumented limits; the teaching rules need those variables. OpenWeather costs ~10x at scale. Mitigate vendor risk with an adapter interface, MET Norway fallback, stale-while-error and the self-host path |
| Cost path | Per-call plan until ~5-10k devices, then price a self-hosted node (16 GB, NVMe; likely low hundreds of dollars a month [INFERRED]) against an Enterprise quote |
| Location (vs GNSS, Wi-Fi/cell service, IP) | **Parent-set in Stage 1.** GNSS needs sky view and a permission; Wi-Fi/cell services add a vendor that sees BSSIDs; IP is wrong behind carrier NAT [MEMORY] |
| Alerts (vs WEA-only, CAP-only) | **Both, with roles**: WEA is the OS siren; NWS CAP via backend feeds calm cards, parent notices and non-WEA types (watches, heat, flood advisories) |
| Explanations | **Hybrid, authored core**: templated live sentences plus authored explainers; the Assistant answers open questions grounded in the pack |
| Home tile | **Signature-protected ContentProvider tile** in ZuneHome; an AppWidget needs a host and Glance widget for a launcher we own anyway [INFERRED] |

## 4. Recommended Stage-1 design

**4.1 Backend (inside the Zune comms service).** Postgres `places(place_id, geoname_id, name, admin1, country, lat_q, lon_q, tz, nws_zone, nws_county)` seeded from GeoNames (CC BY 4.0, per Open-Meteo's licence page [PRIMARY]), so the portal never calls a third-party geocoder; `family_places(family_id, place_id, label)`. Redis cache per place cell with single-flight coalescing, circuit breaker and stale-while-error; TTLs: current/hourly 60 min, daily 3 h, alerts 2 min; refresh only cells a device requested within the TTL. One vendor-facing identity and `User-Agent` (company + contact). Alerts: poll NWS `alerts/active` per state with active places, match to zone/county, fan out. Strip URLs from all alert and forecast text server-side.

```
GET /v1/weather/places/{place_id}/bundle   (device auth, units from family setting)
 -> {current, hourly[48], daily[7], sun, uv, aqi, alerts[], updated_at, valid_until,
     attribution[], schema:1}
GET /v1/weather/content-pack?since=ver     (signed manifest: explainers, safety cards, rules)
PUSH weather.alert {place_id, nws_event, severity, headline, instruction, expires}
PUT  /v1/parent/children/{id}/weather      {places[], units, level_override, alert_notify}
```

Push reuses report 13's persistent system connection; the Weather app holds no connection of its own.

**4.2 Location.** The parent picks Home (and optionally School) in the portal; the child device has no location permission for Weather. UI always says "Weather for Home (City)". Parent copy: "Alerts here are for the places you set. Emergency alerts on the phone follow where the phone is."

**4.3 Alerts.** NWS `event` maps to a safety card and a policy:

| Class | Examples | Child device | Parent |
|---|---|---|---|
| WEA-covered | Tornado/Flash Flood/Extreme Wind/Hurricane warnings | **No sound or notification from Weather**; OS WEA fires; Weather shows a calm banner + safety card on next open | Push + portal |
| Other warnings | Severe Thunderstorm, Winter Storm, Excessive Heat | One quiet notification in waking hours, banner, card | Push + portal |
| Watches/advisories | Flood Watch, Heat Advisory, Dense Fog, Wind | In-app banner only | Portal |

Child-facing text is Zune's own plain wording labelled "for kids"; the original NWS headline and instruction sit under "For grown-ups", so we never present altered content as official [SECONDARY, NWS terms]. Cards: thunderstorm/lightning, tornado, flood, heat, winter cold/ice, wildfire smoke/air quality. Each ends "Tell a grown-up near you", no red flashing, no countdown. Reviewed by a qualified meteorologist before beta (decision 3).

**4.4 Education.** Age band comes from the child profile (5-7, 8-10, 11-13), parent-overridable.

| Band | Style | Standards (US) | Example hook |
|---|---|---|---|
| 5-7 | Icons, 1-2 sentences, no formulas, read-aloud later | K-ESS2-1, K-ESS3-2 | "Cloudy today. Clouds are tiny water drops floating up high." |
| 8-10 | Numbers, cause and effect, predict-then-check, simple graphs | 3-ESS2-1/2, 3-ESS3-1, 5-ESS2-1 | "Humidity 90%: the air is holding lots of water, so it feels sticky." |
| 11-13 | Mechanisms, data reading, weather vs climate | MS-ESS2-4/5/6 | "Pressure fell 4 hPa in 3 hours: a low is arriving, so rain and wind." |

Stage-1 library: **20 explainers x 3 bands** (clouds and types, why rain, water cycle, thunder and lightning, wind, why hot/cold, humidity, air pressure, UV and sun safety, fog and dew, snow and ice, rainbows, seasons, weather vs climate, fronts and air masses, heat safety, cold safety, lightning safety, flood safety, tornado safety) plus 6 safety cards and one multiple-choice check each. Rules run **on device** against the bundle, e.g. `weather_code` rain + `cloud_cover_low` high -> "Why does it rain?"; `cape` high with thunder code -> thunder/lightning; `pressure_msl` falling >3 hPa/3 h -> pressure; `uv_index` >= 6 -> sun safety; at most 3 chips shown. Four interactive visuals in Compose Canvas: animated water cycle, cloud gallery against today's sky, live wind arrow, "what to wear". A templated one-line summary ("Cloudy and cool, take a jacket") is rules, not LLM. Climate content stays factual and local-weather framed in Stage 1; no catastrophe imagery or alarm colours.

**4.5 App.** Kotlin + Compose, Room cache (`Place`, `ForecastSnapshot`, `AlertSnapshot`, `ExplainerSeen`), no WebView (report 04), no Linkify, INTERNET only to the Zune backend. Refresh on open plus WorkManager hourly (CONNECTED, battery-not-low); offline shows the last snapshot ("Updated 3 h ago") and bundled explainers. Units from the family setting (US: F, mph, inches). One alert notification channel; no daily-nudge notifications. Accessibility: TalkBack labels, 48 dp targets, no colour-only meaning, font scaling. "Ask why" opens the Assistant with a context bundle (place, conditions, explainer IDs); "Today's weather note" opens a prefilled Journal entry (assumes a Journal intent, report 09 absent). No third-party SDKs; aggregate server counters only.

**4.6 Stage-1 MVP scope.** Current + 48 h + 7 days + alerts (NWS) + 20 explainers + 6 safety cards + 4 visuals + launcher tile + Journal note + parent place/units/alert settings + MET Norway fallback adapter + CellBroadcast `link_method=none` overlay.

## 5. Stage-2 improvements

Predict-then-check and cloud-match games; 3-ESS2-1-style graphs from the child's journal; multi-place plus optional coarse GNSS "I am here" (one-shot, rounded on device, parent opt-in); capability-gated barometer/light experiments; GLOBE Observer cloud citizen science (child-participation terms to check [SECONDARY https://www.globe.gov/en/globe-data/data-entry/globe-observer]); climate stories for 11-13 with a parent toggle; Spanish and UK/metric locales with Met Office/NC alignment; per-country alerts (ECCC, DWD, Meteoalarm; verify licences then); pollen and moon phase; self-hosted Open-Meteo node; read-aloud once TTS exists; tuned Assistant "why" Q&A.

## 6. Conflicts with earlier reports (01-11)

- **02 (hardware)**: "no voice/SMS... WEA acceptance unverified" and Pixel-first are superseded by D4 and D13. WEA is now in scope and mandatory; a barometer cannot be assumed on Snapdragon devices.
- **03 (minimal product)**: lists CellBroadcast as "DECIDE (Q1), drop the UIs if Wi-Fi/data-only". Now **KEEP** CellBroadcastReceiver + Service with an RRO (`link_method=none`). FusedLocation stays GNSS-only; Weather needs no WebView. The "Learn" app may consume the same content pack.
- **04 (no-browser)**: consistent; adds that CellBroadcast's default `smart_linkify` and Open-Meteo's "link next to data" rule both touch the link ban.
- **12 and 13**: consistent (12 keeps CB with 24-hour history; 13's backend and push are reused for a `weather` module).
- **05, 07, 09, 11 absent**: assumed 05 holds age band and parent settings, 07 accepts a context intent and logs for parents, 09 exposes a Journal entry API, 11 owns the COPPA/state-law reading.

## 7. Risks & unknowns

1. Open-Meteo can change or end terms at will; exact prices are unverified (Stripe table); Enterprise quote or self-host needed at scale.
2. NWS rate limits are undocumented and an API key is coming; MET Norway and vendor terms here are search-summary only.
3. WEA geofencing and carrier acceptance without a network location provider and with a non-stock OS are untested.
4. Content accuracy and editorial burden: 60 variants plus safety cards need a science-education reviewer and a meteorologist.
5. COPPA/state-law interpretation of coarse location plus device identity is for counsel (report 11), not me.
6. A kid may read the forecast as a safety guarantee; copy must say alerts follow the set place and the phone's emergency alerts are separate.
7. Sensor availability differs across D13 devices.
8. Place-cell and refresh assumptions behind the cost table are estimates [INFERRED].

## 8. Decisions needed from the founder (impact order, default first)

1. Approve an Open-Meteo commercial subscription for beta, with a self-host evaluation before ~5-10k devices. **Default: yes.**
2. Stage-1 location: parent-set places only, no device location. **Default: yes.**
3. Fund a science-education reviewer and a meteorologist safety-card review before beta. **Default: yes.**
4. Authored content plus Assistant-grounded Q&A, no LLM inside the Weather app. **Default: yes.**
5. WEA always on and not child-disableable; overlay `link_method=none`; parent copy about night alerts. **Default: yes.**
6. Attribution without a browser: plain text on device, live link in parent portal, with written confirmation from Open-Meteo. **Default: yes.**
7. Own mascot instead of Owlie Skywarn. **Default: own.**
8. Launch in US English/imperial; Spanish as first Stage-2 locale. **Default: yes.**

## 9. Load-bearing claims

| # | Claim | Source | Basis |
|---|---|---|---|
| 1 | Open-Meteo free API is non-commercial only; commercial plans or self-hosting required; data CC BY 4.0; self-host allowed commercially | open-meteo-website@a8dd5c8:src/routes/en/terms/+page.svelte; open-meteo@b06f476:docs/getting-started.md | PRIMARY |
| 2 | Google Weather API terms bar use in a weather app, and cap caching at 1 h/24 h | https://cloud.google.com/maps-platform/terms/maps-service-terms §21.1-21.2 (2026-06-10) | PRIMARY |
| 3 | Open-Meteo exposes cloud layers, CAPE, pressure, UV, US AQI; pollen Europe only | open-meteo-website@a8dd5c8:src/routes/en/docs/options.ts; air-quality-api/+page.svelte | PRIMARY |
| 4 | NWS API: no key, User-Agent required, 2.5 km grid, 4-decimal coordinates, cacheable, alerts endpoints; data public domain | weather-gov/api@694ed0f:general-faqs.md; https://www.weather.gov/disclaimer | PRIMARY / SECONDARY |
| 5 | GrapheneOS's network location uses Apple's undocumented wloc endpoint; AOSP has no network provider; MLS ended | GrapheneOS/platform_packages_apps_NetworkLocation@17:ApplePositioningService.kt; https://beacondb.net/ | PRIMARY / SECONDARY |
| 6 | Android 17 tree contains CellBroadcastReceiver and Service; link_method defaults to smart_linkify and is overlayable | GrapheneOS/platform_manifest@17:default.xml; platform_packages_apps_CellBroadcastReceiver@17:res/values/config.xml:266 | PRIMARY |
| 7 | National Alerts cannot be opted out; NWS warnings trigger WEA (tornado, flash flood, etc.) | https://www.federalregister.gov/documents/2025/03/18/2025-04125/wireless-emergency-alerts-emergency-alert-system; https://www.weather.gov/news/072221-svr-wea | SECONDARY |
| 8 | Street-level geolocation is COPPA personal information; amended rule compliance date 2026-04-22 | https://www.federalregister.gov/documents/2025/04/22/2025-05904/childrens-online-privacy-protection-rule | SECONDARY |
| 9 | WorkManager runs via JobScheduler without GMS; min periodic 15 min; widget updates min 30 min | androidx/androidx@androidx-main:work/work-runtime/.../Schedulers.java; developer.android.com pages cited in 2.5 | PRIMARY |
| 10 | Pixel 9a/10a have barometers; Snapdragon flagships vary; only the light sensor is near-universal | developer.android.com sensors_environment; https://support.google.com/pixelphone/answer/7158570 | PRIMARY / SECONDARY |
