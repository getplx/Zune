export const meta = {
  name: 'zune-research',
  description: 'Zune kids-Android research (18 topics): research+verify topics, re-verify reports against primary AOSP sources, reconcile with founder decisions, cross-topic critic',
  phases: [
    { title: 'Research', detail: 'topic investigators write docs/research/NN-*.md' },
    { title: 'Verify', detail: 'one skeptic per report re-checks claims (prefers primary AOSP sources)' },
    { title: 'Reconcile', detail: 'edit reports to honour docs/REQUIREMENTS.md decisions' },
    { title: 'Critic', detail: 'cross-topic conflicts, gaps, founder decisions, roadmap' },
  ],
}

// ---------------------------------------------------------------------------
// HOW TO RUN (see docs/HANDOFF.md). Requires explicit opt-in to multi-agent
// orchestration (say "use a workflow" or turn ultracode on).
//
//   Workflow({ scriptPath: "<repo>/docs/handoff/research-workflow.js",
//              args: { mode: "research", topics: ["minimal-product", "no-browser"] } })
//
// args (all optional):
//   mode    : "research" (default: write report, then verify it) | "verify" (verify
//             existing reports only) | "reconcile" (revise existing reports against
//             docs/REQUIREMENTS.md) | "critic" (cross-topic critique only)
//   topics  : array of slugs; default = all 18
//   repo    : repo root, default /home/user/Zune
//   scratch : scratch dir for shallow clones, default /tmp/zune-scratch
//   concurrency note: the harness caps parallel agents at min(16, CPUs-2).
//
// Slugs: aosp-base hardware-target minimal-product no-browser parental-controls
//        curated-video ai-assistant walkie-talkie core-apps ota-security compliance
//        telephony-sms messenger-video weather-education snapdragon-hardware settings-minimal byo-distribution v1-provisioning-ops
// ---------------------------------------------------------------------------

const A = (typeof args === 'object' && args) ? args : {}
const MODE = A.mode || 'research'
const REPO = A.repo || '/home/user/Zune'
const OUT = `${REPO}/docs/research`
const SCRATCH = A.scratch || '/tmp/zune-scratch'

const BRIEF = `
PROJECT BRIEF (codename "Zune", repo getplx/Zune, working dir ${REPO})
A custom AOSP-based Android 17 OS image for children, sold as a product: clean minimal build, custom first-party apps only, NO web browser, NO YouTube access by any route, parents manage everything through a browser-based parental-control portal (the child device has no browser). Delivery is staged: Stage 1 = every feature exists end-to-end in its simplest form; Stage 2 = make it better.

READ FIRST, IN THIS ORDER: ${REPO}/docs/REQUIREMENTS.md (the founder's canonical resolved decisions D1-D16 and assumptions A1-A5; AUTHORITATIVE: where anything below or any earlier report conflicts with it, REQUIREMENTS.md wins) and ${REPO}/docs/HANDOFF.md (project state, what is verified, what is not). Existing reports are in ${OUT}/ (01 aosp-base, 02 hardware, 03 minimal product, 04 no-browser lockdown, 05 parental controls, 06 curated video, 07 AI assistant, 08 walkie-talkie/comms, 09 core apps, 10 OTA/signing/security, 11 compliance, 12 telephony+SMS, 13 messenger+video calling, 14 weather, 15 snapdragon-hardware, 16 settings-minimal, 17 byo-distribution, 18 v1-provisioning-ops); read the ones relevant to your topic if they exist. Several earlier reports were written BEFORE the founder put cellular calls/SMS, the messenger, video calling, weather and topic-driven video search in scope; where they assumed otherwise, say so under "Conflicts with earlier reports" and propose the corrected design.

KEY FOUNDER DECISIONS (summary of REQUIREMENTS.md): no browser; no way to reach YouTube (videos only inside the Zune Videos section, curated, gated by the child's age group or a topic the child asked about); cellular voice calls + SMS IN scope with parent-controlled inbound and outbound number allowlists; SMS NOT readable on the device but readable in the parent portal; in-product WhatsApp-like 1:1 messenger (text + emoji only, NO groups) under the same parental contact controls; video calling only with approved participants (other Zune kids; parent-side calling interface deferred); weather app that teaches kids about weather; walkie-talkie; ChatGPT-style AI assistant that accepts images; a MINIMAL Settings app (Wi-Fi and mobile data fully standard, everything else only if fairly required, nothing unnecessary; D14); the product supports only a small curated set of devices and high-end Snapdragon-class phones are acceptable, Pixels are NOT required (D13; supersedes the Pixel-first recommendation in report 02 until report 15 lands); the business model is to SELL THE IMAGE and let customers install it on their own qualified phones, no hardware sales (D15; report 17); in VERSION 1 the company flashes and re-locks the customer's qualified phone and hands it back (D16; report 18), self-install comes later. Assumed (unless REQUIREMENTS.md says otherwise): US launch market, no GMS.

FACTS ESTABLISHED SO FAR (verify, do not trust blindly): Android 17 = AOSP tag android-17.0.0_r1, build CP2A.260605.016, branch android17-release; AOSP publishes source only in Q2 and Q4; report 02 recommended Pixel 9a/10a (Tensor, zumapro) as the v1 hardware path but D13 reopens that: devices are now Snapdragon-first (report 15); AOSP 17 contains a native supervision framework (SupervisionManager); stock AOSP products include Browser2 (must not inherit unchanged).

ENVIRONMENT (this session should have AOSP access; VERIFY FIRST, once): run  git ls-remote https://android.googlesource.com/platform/manifest 2>&1 | head -3  and  curl -sS -m 15 -o /dev/null -w '%{http_code}' https://source.android.com/docs/setup/about/build-numbers .
- If AOSP is reachable: prefer PRIMARY sources: the real android-17.0.0_r1 tree. Use shallow, partial, single-project clones into ${SCRATCH}/ , e.g.  GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 --filter=blob:none --branch android-17.0.0_r1 https://android.googlesource.com/platform/frameworks/base ${SCRATCH}/frameworks_base  (use sparse-checkout for huge repos such as frameworks/base). Do ONE clone at a time, generous timeouts, delete clones when done, keep total scratch under ~15 GB. Also useful: https://android.googlesource.com/platform/manifest (tags/branches via git ls-remote), source.android.com and developers.google.com pages (WebFetch), dl.google.com (Pixel factory images licence text).
- If AOSP is still blocked (403 / EGRESS_BLOCKED): do NOT route around the policy. Fall back to GitHub mirrors reachable via raw.githubusercontent.com and public git clones (GrapheneOS/* branch 17 = real Android 17 trees; LineageOS/* branch lineage-24.0; aosp-mirror/* is STALE at android-16.0.0_r3) and WebSearch, and say clearly which claims could not be checked against Google's own source.
- github.com HTML pages and api.github.com may return 403: use raw.githubusercontent.com or git. This environment cannot BUILD AOSP (small disk/RAM); you inform design, you do not build.
- Training knowledge ends ~June 2026: anything time-sensitive (laws, carrier policy, API terms, licences, prices, device lineups) MUST be checked via search. Never invent URLs, versions, quotes, or statute numbers.

EVIDENCE RULES: tag every material claim [PRIMARY] (read in a primary source / real source file this session; give URL or repo@ref:path), [SECONDARY] (reputable news/docs), [INFERRED] (your judgement), [MEMORY] (training, unchecked). Prefer fewer, well-sourced claims. Be decisive: concrete recommendation + trade-offs, like a staff engineer advising a founder who must ship. Do NOT run git commit/push. Do NOT modify any file except the single file your task names. Do not ask the user questions; put founder decisions in decisionsForFounder (ordered by impact, each with a recommended default).
`

const REPORT_SPEC = (t) => `
DELIVERABLE
1) Write a structured markdown report to ${OUT}/${t.file} (max ~3,000 words; tables where useful). Sections: "Summary & recommendation", "Findings" (basis tags + source URLs), "Options & trade-offs", "Recommended Stage-1 design", "Stage-2 improvements", "Conflicts with earlier reports", "Risks & unknowns", "Decisions needed from the founder", "Load-bearing claims" (5-10 facts the recommendation rests on, with sources).
2) Then return the structured JSON result (schema enforced). reportPath must be ${OUT}/${t.file}.
`

const TOPICS_A = [
  {
    slug: 'aosp-base', file: '01-aosp-base-release.md', title: 'Latest AOSP base release, branches, cadence, build host',
    focus: `Establish exactly what "latest default Android image" means as of 2026-10-02 and how to base the product on it.
- Confirm Android 17 AOSP tags/branches (android-17.0.0_r1, android17-release, android-latest-release, any QPR/Q4-2026 drop expectations), SPL, build IDs. Cross-check with GrapheneOS "17" branch manifest and LineageOS (which lineage-NN is Android 17? tag/branch names) via raw.githubusercontent.com or shallow clones.
- The new Q2/Q4-only AOSP publishing cadence: what exactly is published when; how does a downstream (us) get monthly security patches (is the security-only branch public? how do GrapheneOS/LineageOS/CalyxOS cope? what does this mean for a kids' product that must ship timely security fixes?). Quantify the risk and propose a mitigation strategy.
- Exact repo init/sync commands for the product (repo tool, manifest URL, branch, --depth/--partial-clone/--no-clone-bundle options, disk/time estimates, mirrors since googlesource may be slow/blocked in places). Recommended build host spec (CPU/RAM/disk/OS version), expected clean/incremental build time, ccache/remote cache options, Docker build image options.
- Build system mechanics that matter for a custom product: lunch/target naming in Android 16/17 (release configs such as trunk_staging / next, userdebug/user/eng), Soong vs Bazel status, how to define a custom product under device/<vendor>/<product> and vendor/<vendor>, local_manifests approach vs fork-the-manifest approach, how to track upstream AOSP without painful merges (patch-set strategy, minimal diff vs forked repos, GrapheneOS-style approach).
- Android 17 platform changes relevant to a locked-down kids OS (e.g., 16KB page size, Mainline modules, supervision/parental APIs if any, Advanced Protection, Private Space, large screen/desktop mode, permission changes, background restrictions, anything removed from AOSP).
- Dev/test targets for CI that need no hardware (Cuttlefish, emulator/goldfish, aosp_cf_*), and whether they work on cloud VMs.`,
  },
  {
    slug: 'hardware-target', file: '02-hardware-target.md', title: 'Hardware target & device-support strategy',
    focus: `Decide what physical devices the custom image will run on, because AOSP alone does not boot on arbitrary phones.
- Pixel path: current Pixel lineup (as of Oct 2026: which a/flagship models are supported; Pixel 10 series; Pixel 10a?), whether Google still publishes Pixel device trees/kernel/vendor blobs to AOSP (I recall Google stopped publishing device trees with Android 16/Pixel 10 - VERIFY with GrapheneOS statements and sources), how GrapheneOS handles Android 17 on Pixels (supported device list, what they build from, what they had to reverse/recreate), Pixel unlock + re-lock with custom AVB key support, binary driver blobs availability and licensing for redistribution in a commercial product, Pixel Android-support lifetimes, carrier-locked variants, pricing.
- Treble/GSI path: can a generic AOSP system image (GSI) run on many Treble devices for Android 17 (vendor-freeze, VSR requirements, GSI availability in 2026, quality/limitations like camera, fingerprint, DRM), implications for a kids product, and why/why not.
- ODM/OEM path: building a purpose-made kids phone with an ODM (Qualcomm/MediaTek/Unisoc), Android Go-like specs, BSP licensing, MOQ, lead times, certification burden, cost ranges; which vendors/boards are realistic for a startup; existing kid-phone makers (Pinwheel, Bark Phone, Gabb, Troomi, Fully Kiosk-based, etc.) - what hardware and OS base do they use and what can we learn.
- Other OEMs with unlockable bootloaders / AOSP-friendly (Fairphone, Motorola, Nothing, OnePlus?, Sony Xperia, Nokia/HMD, rugged phones). Which are officially supported by LineageOS at Android 17 (check LineageOS wiki/device repos via raw GitHub or search).
- Business models: (a) sell flashed refurbished/new Pixels, (b) sell image + installer for BYO device, (c) own-branded hardware via ODM, (d) hybrid. Rough unit economics and risks of each (warranty, returns, flashing at scale, secure-boot lock, carrier compatibility, e.g. VoLTE/IMS needs on carriers if cellular).
- Concrete recommendation: v0 dev target, v1 launch target, and long-term target; and a device-abstraction strategy so the product layer (vendor/zune) stays device-agnostic.`,
  },
  {
    slug: 'minimal-product', file: '03-minimal-product-config.md', title: 'Clean minimal AOSP product configuration',
    focus: `Design the "clean build, bare minimum services" product definition at the makefile level using REAL tree contents.
- Using shallow/partial clones (aosp-mirror platform_build @ android16-release or similar, plus GrapheneOS/LineageOS 17-era trees where available, and device/generic/*, packages/apps/*), enumerate how AOSP product makefiles compose (aosp_product.mk, handheld_system.mk, handheld_product.mk, handheld_vendor.mk, mainline_system.mk, core_minimal.mk, telephony variants, etc.). Identify exactly which makefile to inherit for the smallest viable phone-class product and what PRODUCT_PACKAGES it drags in.
- Produce a keep/remove/replace table for every default AOSP app/service/module in the Android 16/17 tree relevant to a phone: Launcher3/Quickstep, SystemUI, Settings, SetupWizard/Provision, Dialer, Telecom, Messaging, Contacts, Camera2, Gallery/Photos, DeskClock, Calculator, Music, Email, Calendar, Browser/WebView (note what AOSP actually ships for WebView in 17), QuickSearchBox, PackageInstaller, DocumentsUI, Bluetooth, NFC, Traceur, CaptivePortalLogin, Stk, CertInstaller, KeyChain, wallpapers, emoji/IME (LatinIME), TTS, Print, Health, etc. Flag which are hard dependencies of boot/SystemUI/Settings (can't remove) vs safe to remove, and which Mainline (APEX) modules matter.
- "Bare minimum services": how to disable/neuter system services and features cleanly (config.xml overlays via RRO / PRODUCT_PACKAGE_OVERLAYS, system properties, init.rc services, feature XMLs in permissions/, privapp-permissions allowlists, sepolicy implications, build-time flags to exclude NFC/Bluetooth/location/etc.). Be concrete and mark risks (e.g. removing something breaks CTS-less but still boot, SystemUI crash loops).
- Prior art: how GrapheneOS, CalyxOS, LineageOS, /e/OS, and any "minimal AOSP" or kiosk/kids/embedded products structure their vendor/ product trees and what pitfalls they hit. Include any open-source kids-OS or kiosk Android ROM projects you find.
- Output a proposed concrete skeleton: directory layout (device/zune, vendor/zune, packages/apps/Zune*), the zune_kids.mk with PRODUCT_NAME/BRAND/etc., AndroidProducts.mk, BoardConfig stub for generic target, and how apps get built in-tree vs prebuilt APKs. Include draft makefile snippets (clearly marked as draft/unverified-by-build) in the report.`,
  },
  {
    slug: 'no-browser', file: '04-no-browser-lockdown.md', title: 'Making "no internet browser" real: threat model & enforcement',
    focus: `"No browser" is the product's defining promise, and it is much harder than deleting a Browser APK. Produce a rigorous threat model and layered enforcement design.
- WebView reality: modern apps (EPUB readers like Readium, YouTube IFrame embeds, OAuth, Compose HTML) need a WebView provider. What does AOSP 17 ship/need (com.android.webview / chromium prebuilt, Trichrome, config_webview_packages.xml)? Options: keep stock WebView but constrain; build/ship Vanadium-like or a restricted WebView; remove WebView and use no web content at all (what breaks?). How can WebView be constrained to an origin allowlist at OS level vs app level (network security config, shouldInterceptRequest, proxy override, DNS)?
- Enumerate EVERY bypass vector and how to close it. At minimum: Intent ACTION_VIEW http(s)/ACTION_WEB_SEARCH resolution, Custom Tabs providers, Captive-portal login (CaptivePortalLogin opens a browser-like WebView on Wi-Fi sign-in), Settings help links/licenses, SMS/link handling, in-app browsers in third-party apps, PackageInstaller / unknown sources / sideloading (Play Store absent, but ADB install, USB OTG, file manager), DocumentsUI file open, PDF/HTML viewers, Share sheet, Cast/screen mirroring, Bluetooth/NFC beam, ADB/USB debugging/developer options/OEM unlock/fastboot/recovery/safe mode/factory reset, DNS-over-HTTPS and Private DNS, VPN apps, tethering/hotspot, alternate SIM data, VNC/remote apps, kids installing APKs, other users/profiles/Private Space/guest.
- Network-layer enforcement: OS-level egress allowlist (only Zune backend + approved content domains) - compare DNS filtering (bypassable), per-UID firewall via netd/eBPF (cgroup/skb) and ConnectivityManager firewall chains, GrapheneOS-style per-app Network permission, always-on locked-down VPN service, transparent proxy, SNI inspection, and what's feasible without root-of-trust compromise. Consider IPv6, QUIC, CDNs with shared IPs (YouTube's domains), DoH in apps.
- Policy plane: use of DevicePolicyManager / user restrictions (DISALLOW_INSTALL_UNKNOWN_SOURCES, DISALLOW_DEBUGGING_FEATURES, DISALLOW_FACTORY_RESET, DISALLOW_CONFIG_*, DISALLOW_ADD_USER, etc.), persistent preferred activities, hidden/suspended packages, lock-task/kiosk mode, vs baking restrictions into the framework (AOSP patches: intent resolver filter, PackageManager install gate, ro.* properties). Give a recommended split: what must be compiled into the image (tamper-proof) vs what is policy delivered by the parental-control backend.
- Build-time hardening: user build only, ro.adb.secure, no su, locked bootloader with custom AVB key, disabling fastboot unlock, removal of Developer settings, SELinux neverallow additions. Reference how GrapheneOS and enterprise/kiosk OS vendors do this.
- Output a bypass-vector table: vector | likelihood for a determined 10-14-year-old | mitigation | residual risk | where implemented (image/policy/network). Be honest that physical-access attacks (e.g. unlocking bootloader via parents' PC, flashing stock firmware) bound what's achievable, and say what that means for marketing claims ("no browser" vs "no web access").`,
  },
  {
    slug: 'parental-controls', file: '05-parental-controls-platform.md', title: 'Parental controls: browser-based portal + on-device enforcement + sync',
    focus: `Design the parental-control platform: parents use a web portal in their own browser; kid devices enforce policy.
- Android's native supervision/parental capabilities in Android 16/17 (SupervisionManager / supervision role / Family Link integration points, restricted profiles, DevicePolicyManager device-owner/profile-owner, Android Management API (needs Play/GMS?), "supervised user" flows). What is in pure AOSP vs requires Google Play Services/Family Link? Check actual sources (GrapheneOS/LineageOS trees, AOSP mirror android16 branches) not just docs.
- Enforcement architecture options: (a) Device Owner DPC app set via provisioning (QR/NFC/zero-touch not available without GMS?) (b) platform-signed privileged system service "ZuneGuardian" with framework hooks (c) hybrid. Recommend one with justification on tamper-resistance, update agility, and complexity. Include enrollment/pairing flow at first boot (SetupWizard replacement: parent scans QR / enters claim code from web portal), multiple children per family, multiple devices per child, parent role-sharing (co-parents, grandparents), and ownership transfer/resale.
- Policy model: screen-time budgets & schedules (bedtime/school mode), per-app allowlist & per-app limits, contacts allowlist (walkie-talkie/calls), content topic controls (curated videos, books), AI assistant settings and transcript review, camera/photo sharing permissions, remote lock, "find my device", SOS/emergency button, location sharing (opt-in; legal implications), reports/activity feed, approval requests from the child ("ask a parent"). Propose a concise JSON/proto policy schema, versioning, signed policy bundles, and offline enforcement when the network is down; trusted-time/clock-tamper protection.
- Sync/push WITHOUT FCM (no GMS): WebSocket/MQTT/gRPC streaming with a foreground service, UnifiedPush/ntfy, SMS wakeups, OEM push; battery and Doze implications; reliability; what other de-Googled OSes do. Recommend one.
- Backend & web portal stack: auth for parents (passkeys/OAuth/email OTP, MFA), multi-tenant family data model, device attestation (Android Key Attestation) binding device to account, API design, tech stack options with a concrete recommendation (e.g. TypeScript/Go/Kotlin, Postgres, Redis, object storage, hosting regions), security (child-data encryption, audit logs, RBAC), observability, GDPR/COPPA data minimization hooks, cost sketch for 1k/10k/100k devices. The portal must be usable on mobile browsers (parents on phones) - PWA?
- Existing open-source MDM/parental projects worth reusing or learning from (Headwind MDM, Flyve MDM, Android Enterprise samples like TestDPC/NetworkPolicy, Kids-focused OSS). Licenses.
- Tamper resistance and what the child can do (uninstall guardian, clock change, factory reset, safe mode) and mitigations tied to the image.`,
  },
  {
    slug: 'curated-video', file: '06-curated-learning-video.md', title: 'Curated YouTube/learning video: legality, tech, alternatives',
    focus: `The founder wants "curated YouTube videos based on topics of learning". Determine if/how this is allowed and technically feasible on a no-browser, probably no-GMS device, and what to do instead/in addition.
- YouTube API Services Terms of Service & Developer Policies as of 2026 (and Required Minimum Functionality / embedded-player policy): what is permitted for a third-party app that embeds a hand-picked allowlist of videos for children; restrictions on ad blocking/removal, background play, download/offline caching, modifying the player, obscuring UI, separate-from-YouTube-branding, user data handling, "made for kids" (MFK) handling and COPPA obligations when embedding (youtube-nocookie.com, data collection and ads on MFK content), YouTube's stance on kid-focused third-party clients, and whether a commercial hardware+OS product needs express permission/audit (quota extension compliance audit). Cite the actual policy pages (search; WebFetch may work for developers.google.com/youtube, if EGRESS_BLOCKED say so and rely on search + secondary sources, flagged).
- Technical feasibility w/o GMS: IFrame Player API inside a locked-down WebView (what origin allowlist/network rules it needs, how it conflicts with the no-browser promise and the egress allowlist, CDN/domain list stability), Android YouTube Player API status, YouTube Data API v3 for metadata (quota 10,000 units/day default, caching limits), NewPipe-style extraction is NOT acceptable (ToS) - state clearly. Embeddability and takedown/removal handling, region restrictions, live-chat/comments/recommendations suppression (rel=0 behaviours changed), end-screen/related video leakage into the open YouTube site (can the kid click out?), age-restricted content, ads on MFK.
- Curation operations: how to curate by topic/grade/curriculum (Common Core/NGSS/UK national curriculum), who curates (editors, partners, ML pre-filter + human review), update workflow, parent overrides (add/remove channels), reviewer tooling, metadata schema, legal exposure for mislabeled content.
- Alternatives and complements with clean licenses and offline support: Kolibri (Learning Equality) and its content licensing, Kiwix offline Wikipedia/Wikibooks/Khan/TED mirrors, Khan Academy (license is CC BY-NC-SA - commercial problem?), PBS KIDS/Crash Course/TED-Ed licensing terms, NASA/Smithsonian/Library of Congress public-domain, Internet Archive, Wikimedia Commons, StoryWeaver, OpenStax, Blender open movies; paid licensing partners (e.g. Britannica, BBC Bitesize?, Nat Geo Kids, Common Sense) - verify each license claim via search; self-hosting video (HLS) cost. 
- Recommended tiered content strategy (Tier 1 offline licensed/open content, Tier 2 YouTube-embed behind strict compliance, Tier 3 partner content) with a clear go/no-go on YouTube for v1 and exact steps to de-risk (e.g., contact YouTube API compliance / partnership team).`,
  },
  {
    slug: 'ai-assistant', file: '07-ai-assistant.md', title: 'Kid-safe AI assistant: architecture, models, safety, policy',
    focus: `Design an AI assistant for children on a no-GMS, no-browser device.
- Architecture: cloud-hosted LLM behind a Zune backend gateway (auth, parent policy, moderation, logging, rate limits, cost control) vs on-device small model vs hybrid with offline fallback. Evaluate on-device options on mid-range phone hardware in 2026: Gemma/Qwen/Phi/Llama small models, llama.cpp, MediaPipe LLM Inference / LiteRT-LM, ExecuTorch, MLC; note Android AICore/Gemini Nano need GMS/Google components (verify) so are not available. Realistic latency, RAM, battery, quality; recommendation per tier.
- Voice-first UX for kids who may not type/read well: on-device STT (whisper.cpp, Moonshine, Vosk, sherpa-onnx; Android SpeechRecognizer needs a recognition service which AOSP lacks), TTS (AOSP/Pico status, eSpeak-NG, Piper, Kokoro, sherpa-onnx), wake word / push-to-talk, child-voice accuracy issues, languages.
- Safety design (the core): layered guardrails - system prompt/persona (tutor not companion), input and output classifiers/moderation, age bands (5-7, 8-10, 11-13), topic allowlists, refusal+redirect patterns, self-harm/abuse/grooming disclosure handling & escalation to parents, PII scrubbing and no personal-data collection, no romantic/parasocial dependency design, hallucination controls for education (grounding in curated content, citations), prompt-injection/jailbreak resistance from children, transparency to parents (transcript review vs child privacy, age-appropriate), rate limits/time budgets, evaluation harness + red-team datasets for kids, incident response. Cite credible guidance (Common Sense Media AI risk assessments, UNICEF AI-for-children guidance, UK ICO AADC, NIST, etc.) - verify via search.
- Model/vendor options and terms: Anthropic Claude API, OpenAI, Google Gemini, Mistral, open-weights self-hosted. CHECK each vendor's current usage policy / terms on minors and on products directed at children (e.g., Anthropic's usage policy and API terms regarding under-18 end users and required safeguards; OpenAI's policies; Google Gemini API terms re COPPA) and state what is required (age verification? parental consent? additional safeguards? prohibited?). This is a go/no-go factor - be precise and cite.
- Regulatory touchpoints specific to AI + minors in 2026: California SB 243 (companion chatbots), FTC 6(b) inquiry on AI chatbots & kids, COPPA amendments, EU AI Act (prohibited practices/minors), UK Online Safety Act, state AI laws - verify status via search and summarize what binds a product like ours.
- Cost model per active child per month (token costs at typical usage, voice costs), caching and small-model routing strategies; privacy architecture (zero-retention endpoints, data processing agreements, regional hosting).
- Recommended v1 scope for the assistant (e.g., homework helper / curious-questions tutor / story-maker with strict limits) and a "what we will NOT build" list.`,
  },
  {
    slug: 'walkie-talkie', file: '08-walkie-talkie-comms.md', title: 'Walkie-talkie / safe kid-to-kid communication',
    focus: `Design a push-to-talk "walkie talkie" feature for children, plus the minimal safe messaging story, on a no-GMS device.
- Transport options compared with a decisive recommendation: (1) live half-duplex PTT over WebRTC with an SFU (LiveKit, mediasoup, Janus, Pion), (2) store-and-forward short voice clips over HTTPS (Opus/Ogg) - Zello/Voxer-style, (3) Mumble/Murmur, (4) Matrix/Element Call (MLS/E2EE), (5) local/offline modes: Wi-Fi Direct, Wi-Fi Aware (NAN), BLE, Bluetooth classic, and Android's Nearby (needs GMS - verify) for same-room/neighbourhood use without internet. Codec (Opus at 12-24 kbps), jitter buffers, background audio/foreground-service constraints on Android 17, hardware PTT key support, headset buttons, battery impact, bandwidth per hour, latency numbers.
- Identity & trust: parent-approved contact graph across different families (both parents must approve; invite codes/QR at in-person meetups), no discovery/search by strangers, block/report, per-contact time windows, "school mode" silence, SOS/emergency call-parent priority channel.
- Privacy & safety vs E2EE: parent visibility options (none / metadata only / recorded and reviewable for a retention window), recording consent laws (one-party vs all-party consent states, GDPR), child-safety obligations (CSAM reporting duties e.g., 18 U.S.C. 2258A for providers who gain actual knowledge, NCMEC), grooming detection feasibility on voice, content moderation of voice (ASR+classifier cost), abuse reporting. Be concrete about what is legally required vs recommended.
- No-GMS push for incoming calls/PTT wake-ups: persistent connection strategies, battery, reliability on Android 17 background limits, high-priority wakeups; compare with how other de-Googled systems do it.
- Telephony: whether to support cellular voice/SMS at all; VoIP is not a PSTN service and cannot dial emergency numbers - what disclosures/regulatory notes apply (FCC interconnected VoIP rules, E911, Kari's Law/RAY BAUM'S) if we ever add outbound calling; recommended v1 position.
- Hosting/cost: SFU capacity per vCPU, bandwidth costs per 10k kids, region strategy, build-vs-buy (LiveKit Cloud vs self-host, Agora/Twilio/Daily/Vonage) and their child-directed-service terms (COPPA-compliant DPAs).
- Provide a protocol + data-flow sketch and a v1 MVP cut (smallest shippable walkie-talkie).`,
  },
  {
    slug: 'core-apps', file: '09-core-apps-stack.md', title: 'First-party app suite: stack, in-tree vs APK, per-app design',
    focus: `Define the first-party app suite and engineering approach for a single-OS-version (Android 17 only) product.
- App list & MVP scope for each: Launcher/home (kiosk-style, large targets, parent-configured, role HOME; fork Launcher3/Lawnchair vs Compose from scratch), Setup/onboarding wizard (replace SetupWizard; parent pairing), Camera (AOSP Camera2 status in Android 17 tree; CameraX-based kid camera; no geotags, parent controls), Photos/Gallery (MediaStore-based; private; parent-sharing; no cloud by default), Journal (private-by-default diary: text, drawing, stickers, voice notes, mood; parent visibility policy), Notebook (notes, handwriting/stylus via Jetpack Ink, drawings, PDF export), EPUB reader (see below), AI assistant UI, Walkie-talkie UI, Learning videos UI, plus "anything else not related to browsing": clock/alarm/timer, calculator, voice recorder, drawing/art, music/audio player (offline), contacts-lite, calendar/homework planner, flashlight, weather (needs internet - via backend), maps/"where's mom" (parent-visible location), file manager-lite, games (curated offline), coding/Scratch-like (offline), dictionary. Prioritize into v1 / v1.1 / later with rationale.
- EPUB reader specifically: Readium Kotlin Toolkit (BSD; its EPUB navigator uses WebView - conflict/synergy with the no-browser design), alternatives that avoid WebView (crengine/KOReader-based engines, FBReader (GPL), Librera, Moon+ (proprietary) - check licenses and feasibility), accessibility (OpenDyslexic, TTS read-aloud, text sizing), reading progress sync, kid-friendly book sources (Project Gutenberg, Standard Ebooks, StoryWeaver, African Storybook, OpenStax, Internet Archive) and their licenses, parent-approved library, DRM/LCP for commercial books, children's e-book age ratings. Verify license/maintenance status via GitHub raw files.
- Engineering stack (2026 best practice): Kotlin, Jetpack Compose + Material 3 (or custom kid design system), Hilt/Koin, Room + SQLCipher or Android Keystore-backed encryption, WorkManager (works without GMS - verify), CameraX (works without GMS - verify), Media3, Jetpack Ink, Coil, Ktor/OkHttp, gRPC/protobuf, Gradle vs Soong (Android.bp) builds for in-tree apps; module layout of a monorepo (apps/*, libs/*, backend/*, os/*); shared "zune-core" SDK for policy checks, telemetry, auth; design-system + accessibility (reading levels, large touch targets, i18n/RTL), crash reporting & analytics without Google Firebase (self-hosted Sentry/ACRA/PostHog) with child-data minimization.
- In-tree (platform-signed, privileged, Android.bp android_app / android_app_import) vs APK-on-system-partition vs updatable via our own store: recommendation with trade-offs on updatability, privileges (privapp-permissions), signing, SELinux domains, and testability. Dependencies on GMS that commonly break apps (Firebase, Play Services Location, ML Kit, Maps) and replacements.
- Testing: Robolectric/Compose UI tests/Macrobenchmark, Cuttlefish-based instrumentation in CI, device farm, accessibility tests, kid usability testing protocols.
- Team/sequence estimate: person-weeks per app for MVP, suggested build order, what to buy/OSS vs build.`,
  },
  {
    slug: 'ota-security', file: '10-ota-signing-security-supply-chain.md', title: 'Release engineering: signing, OTA, verified boot, anti-theft, build infra',
    focus: `Plan the release/update/security backbone of a shipped custom Android product.
- Release signing: own platform/release/media/shared/networkstack keys vs AOSP test keys (never ship test keys); how to generate (development/tools/make_key, generate_verity_key), key custody (HSM/cloud KMS, offline root, split duty), sign_target_files_apks / releasetools flow, APEX/APK key handling (apex_payload keys), AVB custom key (avb_pkmd) and lock/unlock behavior on the chosen hardware, rollback index protection, key rotation/compromise plan.
- OTA: A/B (virtual A/B) updates via update_engine, ota_from_target_files full & incremental, update client app (what AOSP ships, GrapheneOS Updater, LineageOS Updater, hawkBit, Mender), server hosting (static CDN + metadata), staged rollouts, forced security updates for kids' devices, rollback safety, update windows respecting bedtime/battery/Wi-Fi, delta size, bandwidth cost, update lifecycle/EOL policy (how long do we promise?).
- Security patch pipeline given AOSP's Q2/Q4-only source drops (cross-reference topic 01 but focus on process): monthly SPL cadence, tracking Android Security Bulletins, who gets patches (Pixel factory images vs AOSP security branch vs GrapheneOS's approach), kernel (GKI) updates, vendor blobs updates, Chromium/WebView updates (WebView is a huge attack surface - monthly), Mainline module updates (no Google Play system updates without GMS - how do APEX modules update? what do GrapheneOS/LineageOS do?).
- Device hardening: SELinux enforcing, memory-safety hardening (hardened_malloc, MTE on supported SoCs, etc., GrapheneOS-style hardening - what is portable), disabling debugging in 'user' builds, fastboot/OEM-unlock policy, Factory Reset Protection WITHOUT GMS (persistent data block, ro.frp.pst, PersistentDataBlockManager) / anti-theft / lost mode / remote wipe, Key Attestation to bind a device to a parent account and detect tampered/unlocked devices, secure erase, encrypted storage (FBE), screen lock for kids (no PIN vs parent-set), secure boot guarantees vs a determined child with a PC.
- Build infrastructure: CI for AOSP (cloud VMs: sizes, spot pricing, build times, caches (ccache, remote caching), artifact storage), reproducible builds, SBOM/licence scanning (GPL kernel source obligations), build verification tests (Cuttlefish boot smoke test, CTS-lite/VTS subsets feasible without GMS, own instrumentation tests), release gates, staging devices; GitHub Actions self-hosted runners vs buildbot vs Jenkins; estimated monthly cost.
- Factory flashing & provisioning at scale: fastboot/AVB key flashing, locking bootloader, provisioning jigs, per-device identity and key provisioning, QA, labeling, returns/RMA reflash flow, web-based flasher (WebUSB) for BYO devices (note: needs a browser on the PC - fine), customer-facing install instructions.
- Telemetry/crash reporting without Google and with minimal child data; vulnerability disclosure program; incident response for a kids' product.`,
  },
  {
    slug: 'compliance', file: '11-compliance-legal-regulatory.md', title: 'Compliance, legal & regulatory map for a kids OS',
    focus: `Map the legal and regulatory obligations that bind a company selling a children's Android-based OS/devices with AI, voice chat, cameras and cloud services. This is research, not legal advice, but be specific and cite.
- US: COPPA (amended rule - confirm publication, effective date, compliance deadline; verifiable parental consent methods; data retention; third-party disclosures; "directed to children" + actual knowledge; safe harbor programs like kidSAFE/PRIVO/ESRB Privacy Certified), state kids' privacy laws (California Age-Appropriate Design Code status after litigation, other states), California Digital Age Assurance Act (AB 1043?) which reportedly imposes duties on OPERATING SYSTEM providers to collect user age at setup and expose an age-bracket signal API to apps (VERIFY: bill number, effective date 2027?, exact obligations, whether a kids-only OS is affected/exempt), Utah/Texas App Store Accountability Acts (status/injunctions; does an OS with no app store count?), California SB 243 (companion chatbots) and other AI-minor laws, KOSA status, FTC enforcement trends against kids' apps/devices (cite recent actions), CPSIA/children's product rules (is a phone "designed or intended primarily for children 12 or younger" -> children's product certificate, third-party testing, lead/phthalates, tracking labels? battery/ASTM F963 if toy-like).
- EU/UK/other: GDPR Art. 8 (age of digital consent by member state), GDPR-K/EDPB guidance, UK Age Appropriate Design Code + Online Safety Act + ICO guidance, EU Digital Services Act minors guidelines, EU AI Act (prohibited practices/transparency/minors), EU RED/CE and Cyber Resilience Act (CRA) obligations for products with digital elements (timeline: reporting from Sep 2026? full Dec 2027 - verify), EU Radio Equipment Directive cybersecurity delegated act (Aug 2025) for internet-connected radio equipment/childcare products, Canada/Australia (Australia under-16 social media ban scope & whether messaging/walkie-talkie is covered), India DPDP Act (verifiable parental consent) - prioritize by likely launch markets and recommend a launch-market sequence (e.g., US first? UK/EU later?).
- Hardware/radio certification when selling devices: FCC Part 15/22/24/27 and PTCRB/GCF/carrier certification if we modify certified phones (re-flashing software on certified hardware: when does it trigger a permissive change or new certification? Pixels sold as refurb), CE-RED, battery shipping (UN38.3), WEEE/RoHS, import duties, warranty law; carrier certification if cellular is enabled; E911/VoLTE.
- Open-source and IP: AOSP Apache-2.0, GPL-2.0 Linux kernel + source-offer duty, LGPL/GPL components, vendor blobs redistribution licenses (Pixel binaries licence terms), Android trademark & logo guidelines (can we say "Android"? "Based on Android Open Source Project"?), no GMS/Play (what that means for branding/compat claims), licences of every component recommended (Readium BSD-3, etc.), the codename "Zune" (Microsoft's former product - trademark risk; recommend a name-clearance check), patent exposure (video codecs: H.264/HEVC/AAC royalty obligations when shipping a device/OS - AVC/HEVC pools, Opus royalty-free), font/emoji licences.
- Operational: privacy program (data map, DPIA/COPPA data inventory, DPAs with processors incl. LLM vendor, SOC 2/ISO 27001/ISO 27701 path, age-appropriate privacy notices, children's deletion rights & parent access/export), content-moderation duties, mandatory reporting of CSAM (18 U.S.C. 2258A), terms of service for parents vs children, insurance, security incident notification laws, accessibility law (ADA/EAA European Accessibility Act applies June 2025 to consumer electronics/e-books?). 
- Output: a risk-ranked compliance matrix (obligation | applies when | severity | design implication | owner | cost/lead-time) and a "build-in-from-day-one" checklist, plus what to ask a lawyer first.`,
  },
]

const TOPICS_B = [
  {
    slug: 'telephony-sms', file: '12-telephony-calls-sms-allowlists.md', title: 'Cellular calls + SMS with parent-controlled allowlists on a custom AOSP 17 image',
    focus: `Founder decisions D4-D6: cellular voice calls and SMS are in scope; the parent controls which numbers can call the device and which numbers the child can call/communicate with; SMS must NOT be readable on the device but must be readable in the parent portal.
1) AOSP telephony reality in Android 17: which apps/modules ship in AOSP for calling and messaging (Telecom, TeleService/Phone, TelephonyProvider, Dialer, InCallUI, Messaging, CellBroadcastReceiver, Stk, carrier config, IMS, euicc/LPA), which have been removed from AOSP, and what GrapheneOS/LineageOS ship instead (check real trees). What is the minimum set for working voice+SMS+emergency calling+WEA, and what must be written ourselves?
2) Call allowlist enforcement, designed to be tamper-proof against a determined child: roles and APIs (default DIALER role + InCallService, CALL_SCREENING role / CallScreeningService, Telecom CallsManager hooks, BlockedNumberContract), vs a framework patch in Telecom that rejects non-allowlisted inbound/outbound calls regardless of which app asks. Cover every bypass: tel: intents from other apps, MMI/USSD codes (*#06#, call-forwarding *21*, *67#, conference/merge calls, voicemail, third-party/emergency dialer shortcuts, hidden dialer secret codes, Settings > call forwarding / call barring, SIP/VoIP accounts, WiFi calling, number normalisation (E.164, international, short codes, premium numbers), spoofed caller ID (is STIR/SHAKEN verification status exposed to the platform on Android 17? verify Call.Details caller-number-verification APIs), hidden/withheld numbers, carrier voicemail. Emergency numbers (911/112/988 etc.) must ALWAYS work: legal/technical requirements and how an allowlist coexists with them (emergency callback, E911 location). Parent numbers always allowed. Offline behaviour: cached signed allowlist, fail-closed vs fail-open policy.
3) SMS design: becoming the default SMS role app that receives SMS_DELIVER but never renders messages; upload to parent portal (encrypted in transit and at rest), local handling/deletion, offline queue, MMS (picture/group MMS - recommend disable or capture?), RCS (confirm unavailable without Google Jibe/Messages), short-code/OTP messages, spam, sending SMS from the child device (assumption A2: child neither reads nor sends SMS; confirm technical consequences of that), parent reply path, SMS-based carrier provisioning/OMA messages and carrier-required system SMS handlers that must keep working, ensuring no other component displays SMS text (notifications, lock screen, Settings, Assistant, backup/restore, adb), data retention, wiretap/interception and consent law angles (US federal/state, GDPR for third-party senders) - state what must be disclosed and what a lawyer should confirm.
4) Carrier/SIM/modem realities for a custom OS: IMS/VoLTE and carrier-config on a non-certified OS (US carriers' device-certification/IMEI allowlisting for VoLTE; 3G sunset; what GrapheneOS reports about carrier compatibility), eSIM vs physical SIM and the LPA/eSIM provisioning without Google (Pixel 10 US models reportedly eSIM-only - VERIFY), MVNO/kid-phone SIM partnerships (how Gabb, Pinwheel, Troomi, Bark Phone, etc. do it and which networks), wholesale SIM/data/voice platforms (e.g. Twilio Super SIM, Telnyx, 1NCE, Soracom, Pelion - check suitability for consumer voice/SMS), per-line cost range, number porting, billing/subscription model, Wireless Emergency Alerts (CellBroadcastReceiver must stay; carrier requirements), hearing-aid-compat/other mandatory device requirements, regulatory (FCC, PTCRB/GCF/carrier certification when software changes - cross-check report 11 if present).
5) Parent-portal data/UX requirements for this feature: call log, number allowlist/blocklist management, per-contact schedules (school hours), pending approvals ("unknown number tried to call"), SMS inbox UI, audit trail, notifications; schema sketch.
6) Stage-1 MVP vs Stage-2 improvements.`,
  },
  {
    slug: 'messenger-video', file: '13-kid-messenger-and-video-calling.md', title: 'WhatsApp-like 1:1 kid messenger + 1:1 approved video calling (and unification with walkie-talkie)',
    focus: `Founder decisions D7-D8 (+D10): an in-product messenger between Zune kids: 1:1 only, no groups, text + emoji only, under the same parental contact controls as calls/SMS; video calling only with approved participants (other Zune kids, or parents via a parent-side interface that is deferred); also a walkie-talkie (push-to-talk).
1) Product + trust model: identity and contact discovery WITHOUT phone-number scraping; how two kids from different families become contacts (parent-A and parent-B both approve; invite code/QR/phone-number-confirmation by parents), unified contact graph reused by calls/SMS allowlists, messenger, video, walkie-talkie; blocking/reporting; schedules (school/bed time); what happens when a parent revokes a contact; contact removal vs history retention.
2) Parent visibility vs privacy vs security: founder says messenger sits "within the same parental control capabilities as SMS" (parent can review). Compare: server-readable-with-at-rest-encryption, E2EE with parent as an extra recipient device/key (parent browser holds key via WebCrypto/passkeys - feasible?), client-side escrow, metadata-only modes. Recommend one for Stage 1 and explain implications (breach impact, legal reporting duties such as 18 U.S.C. 2258A, COPPA data minimisation, recording-consent laws for video/voice). Text moderation (profanity, bullying, PII, grooming patterns, link neutralisation since no browser) and what is realistic on-device vs server in Stage 1.
3) Messenger tech: build on an existing protocol vs custom: Matrix (Synapse/Dendrite/Conduit + a Kotlin SDK/matrix-rust-sdk; licence AGPL for Synapse? check), XMPP (ejabberd/Prosody + Smack), Signal-protocol libs, MQTT, or a simple custom WebSocket/gRPC service with Postgres. Evaluate for 1:1 text+emoji, delivery receipts, typing indicators, offline delivery, multi-device (kid has one device; parent has browser), scale to 100k kids, ops burden, licensing cost, no-GMS push (persistent connection foreground service vs UnifiedPush vs polling; Android 17 background limits, Doze; battery) - recommend ONE stack. Emoji: AOSP Noto Color Emoji version/licence (OFL), emoji picker (AndroidX emoji2/emoji picker works without GMS? verify), skin tones, safe-emoji filtering (e.g. block sexual/violent/drug emoji for age bands), sticker/GIF exclusion (Stage 2).
4) 1:1 video calling: libwebrtc on Android without GMS (Google's WebRTC build, webrtc-sdk/android, LiveKit Android SDK, Stream, Jitsi, Pion), camera/mic permission model on a kids OS (privacy indicators), codecs (VP8/VP9/H.264/AV1 hardware encoders on candidate devices), signalling over the same backend, STUN/TURN (coturn) and NAT traversal reality (symmetric NAT on mobile carriers - TURN relay share), SFU vs P2P for 1:1, bandwidth per call-hour and cost per 10k kids, parent monitoring/ability to end calls remotely, call schedules, safety (no screen-recording of other child?, snapshot detection, nudity detection on video feasibility), recording policy. The deferred parent-side video calling: browser WebRTC from the parent portal (WebRTC works in browsers) - sketch the architecture so Stage 1 does not block it.
5) Reconcile with walkie-talkie (report 08 if present): propose ONE comms backbone (identity, contact graph, push channel, media plane) shared by messenger, walkie-talkie, video calling and (for parent visibility) the portal. Recommend whether to use LiveKit (open source, Apache-2.0; Cloud vs self-host) as the real-time media plane for both PTT and video. Provide a protocol/data-flow sketch and a service diagram in text.
6) Compliance touchpoints specific to kid-to-kid communication (COPPA, UK AADC/Online Safety Act "user-to-user service" duties, EU DSA minors, CSAM reporting, state laws), what changes if kids from different families can message.
7) Stage-1 MVP vs Stage-2 improvements (e.g. photos/voice notes/reactions/groups much later).`,
  },
  {
    slug: 'weather-education', file: '14-weather-education-app.md', title: 'Weather app that teaches children about weather',
    focus: `Founder decision D9: a Weather app that also educates children about weather when they look at it, on a no-GMS, no-browser device.
1) Data sources for a commercial child-directed product, with licences/terms verified: US National Weather Service api.weather.gov (public domain? rate limits, User-Agent requirement, US-only), Open-Meteo (non-commercial free tier vs commercial plans - verify pricing/terms), MET Norway Locationforecast (CC BY 4.0 + terms), OpenWeather, Tomorrow.io, WeatherAPI, Meteomatics, Visual Crossing, Google Weather API, Environment Canada, DWD/ICON, ECMWF open data. Compare coverage, accuracy, cost at 10k/100k devices, caching rules (some ToS forbid caching or redistribution), alerts support, UV/air-quality/pollen/astronomy data, historical/climate data, commercial-use permission, attribution. Recommend a primary + fallback and a backend-proxy design (device never talks to third-party weather APIs directly; cache at backend; privacy: coarse location only; no device identifiers sent upstream).
2) Location without GMS: parent-set home/school location vs device location. AOSP has no network location provider (no Google NLP): options (GNSS-only, cell-ID/Wi-Fi geolocation services such as BeaconDB / Mozilla Location Service status / self-hosted Ichnaea / commercial APIs, IP geolocation), what GrapheneOS does, privacy and COPPA implications of collecting child geolocation (precise vs coarse; COPPA treats geolocation sufficient to identify street-level as personal information), recommended minimal approach for Stage 1 (e.g. parent-set city + optional coarse location) and Stage 2.
3) Severe weather and alerts: Wireless Emergency Alerts via CellBroadcastReceiver (must stay in the image - confirm from AOSP/carrier requirements) vs NWS CAP alerts via backend; how to present alerts to children calmly with safety actions ("what to do in a thunderstorm / tornado / heat wave / flood"), parent notification of severe weather, and not duplicating or conflicting with the OS emergency alert UI.
4) Educational design: age bands (5-7, 8-10, 11-13), learning goals aligned with NGSS (e.g. K-ESS2-1, 3-ESS2-1/2, MS-ESS2-5/6) and other curricula (UK national curriculum; verify codes you cite), contextual "Why is it...?" explainers tied to the live forecast (e.g. today it's cloudy: what kind of cloud, why rain, why thunder follows lightning, what is humidity/pressure/wind/UV), interactive visuals (animated water cycle, cloud identification, wind arrows, temperature "what to wear"), weather journal that integrates with the Journal app (observations, predict-then-check games, hands-on experiments), device sensor tie-ins (barometer/ambient light/temperature sensors - which exist on candidate phones? Pixel barometer yes? verify), seasonal/climate content (age-appropriate, factual, sensitive to climate anxiety), accessibility, i18n/units (C/F, mm/in), offline behaviour/caching, low-bandwidth. Content sourcing with clean licences: NOAA/NWS education resources & Owlie Skywarn (US government works - verify), NASA Climate Kids/GLOBE (verify), UK Met Office education resources (verify licence), Wikimedia Commons, CC-BY sets; plus whether to generate explanations with an LLM (accuracy/hallucination risk, moderation, cost) vs author a vetted content library (recommend hybrid: authored core + LLM-assisted Q&A grounded in it, parent-visible).
5) Technical design of the app: Kotlin/Compose, widgets and lock-screen/launcher integration, notification policy for kids, battery/network use, WorkManager background refresh without GMS (verify), data model, backend API sketch, telemetry minimisation, localisation; Stage-1 MVP (current + 7-day + alerts + 20 explainers) vs Stage-2 improvements (games, sensors, citizen science, climate stories, multi-location).
6) Compliance touchpoints: children's location data, third-party API data-sharing (vendor receives lat/long), attribution requirements.`,
  },
]

const TOPICS_C = [
  {
    slug: 'snapdragon-hardware', file: '15-snapdragon-device-selection.md', title: 'Curated high-end Snapdragon device set: which phones, which BSP route, relock, cellular, AI',
    focus: `Founder decision D13: the product is limited to a small, curated set of supported devices; high-end Snapdragon-class devices are acceptable and Pixels are not required. This REOPENS report 02 (Pixel/Tensor-first). Produce the device-selection and BSP strategy for a Snapdragon-based kids OS.
1) Candidate devices (as of Oct 2026) built on high-end Snapdragon (8 Elite, 8 Elite Gen 5, 8 Gen 3, 8s Gen 4, 7-series where relevant): OnePlus 13/15, Sony Xperia 1 VII, ASUS ROG Phone 9/10, Nothing Phone (3), Motorola Edge/Razr/flagship (note the reported 2027 Motorola-GrapheneOS flagship partnership in report 02 - verify what it covers and whether it is Snapdragon), Xiaomi/Poco/Redmi, Samsung Galaxy S (note: Galaxy S25/S26 use Snapdragon; US bootloaders are locked, Knox fuse), Fairphone 6, Honor/Oppo/Realme/iQOO/Vivo, plus any Qualcomm reference designs/MDK devices. For each: SoC, price, US availability and band/VoLTE certification, bootloader unlock policy and process, whether a bootloader can be RELOCKED with a custom AVB key (Verified Boot green state; Google documents avb_custom_key; which OEMs support it), OEM firmware/security-update promise and Android 17 timing, kernel (GKI version), eSIM, camera/modem quality, hardware-backed keystore/StrongBox, thermal/battery, size/ruggedness for kids, repairability, LineageOS/other community Android 17 support. Rank against a written Device Support Contract (MUST: AVB custom-key relock, OEM unlock can be disabled after provisioning, A/B, AIDL HALs/VINTF, hardware keystore, fastboot flashable, 8 GB+ RAM).
2) Qualcomm BSP / AOSP-support routes - the crux: (a) retail phone + generate vendor module from the OEM's stock firmware (adevtool-style; check whether tooling exists for non-Pixel Snapdragon phones, legal and technical limits of vendor blob extraction), (b) LineageOS-style device trees (git repos exist for many Snapdragon phones; quality, camera/IMS/VoLTE support, licensing of extracted blobs), (c) Qualcomm public sources: CodeLinaro/CAF (git.codelinaro.org, LA.* tags, kernel msm-*), Qualcomm Linux/Android releases, what is public vs licensed, GKI on Snapdragon, whether Qualcomm provides AOSP 17 BSP only to OEM/ODM licensees (QPM/commercial agreement) and how a startup gets access (Qualcomm Developer Network? Thundercomm? an ODM such as Longcheer/Huaqin/Wingtech/Tinno/Ragentek?), (d) OEM partnership (Motorola, HMD, Fairphone, Sony, Nothing) where the OEM builds our image or grants unlock/keys, (e) own-design phone via an ODM on a Snapdragon platform. Include Qualcomm's long-term support programme (Google Requirements Freeze / GRF, announced update lifetimes for 8 Elite and others), vendor-support-window rules (VSR / FCM) for Android 17, and what a vendor-frozen BSP means for monthly security patches.
3) Retail-flash vs manufacturer-built is an OPEN FORK (assumption A4): analyse both honestly - tamper resistance (an UNLOCKED bootloader means the child or anyone with a PC can flash stock or anything, and Android shows an orange boot warning), warranty/returns, certification (FCC/PTCRB/carrier when we modify and resell), price (high-end Snapdragon phones cost $600-1,200+: what does that do to the business model, a kids' product at that price, trade-in/refurb options, subscription/financing), supply stability and MOQ, who owns the monthly patch burden.
4) What Snapdragon buys the product: on-device AI via the Hexagon NPU (Qualcomm AI Engine Direct/QNN, AI Hub, Genie, ExecuTorch/LiteRT QNN delegates; feasibility of on-device speech-to-text, TTS and small LLMs for the kid AI assistant, offline fallback), video-calling hardware codecs, camera ISP (Spectra) HAL accessibility from custom camera apps, modem (X-series) and carrier certification, 5G/VoLTE/VoWiFi. And what it costs: HAL/BSP complexity, vendor blobs, closed camera stack. Explicitly cross-check against Pixel/Tensor so the founder can compare apples to apples.
5) Recommendation: a short list of 1-3 launch devices, a v0 dev device, the BSP route, the key/relock plan, the price implication, and what to do about report 02 (keep Pixel as a dev/reference device?). Include a Device Support Contract and the minimal evidence needed per device before qualification (a bring-up checklist: boot, relock, VoLTE on target carriers, camera, audio, GPS, charging, OTA).`,
  },
  {
    slug: 'settings-minimal', file: '16-minimal-settings-app.md', title: 'Minimal Settings app: what stays, what goes, what is parent-gated, how to build it',
    focus: `Founder decision D14: a Settings capability with the MINIMUM settings; mobile data and Wi-Fi remain "as it is" (fully standard); everything else only if fairly required; nothing unnecessary.
1) Inventory the real Android 17 Settings: use shallow/sparse clones of GrapheneOS/platform_packages_apps_Settings (branch 17), LineageOS android_packages_apps_Settings (lineage-24.0), and SettingsLib/SettingsIntelligence/SystemUI (QS tiles, Internet dialog), frameworks/base Settings.* intents, plus the supervision settings screens. List every top-level and second-level screen, the aconfig/feature flags and config_* resources that can hide things, how Settings Panels/Slices (e.g. the Internet connectivity panel opened by SystemUI), SetupWizard/provisioning, emergency/SOS, eSIM/SIM management (MobileNetworkSettings), data usage, Network & internet, VPN/Private DNS/proxy/static-IP fields, hotspot/tethering, NFC, USB preferences, developer options, Users, Accounts, Backup, Print, Cast, Nearby Share, Notifications, App info, Permissions manager, Privacy dashboard, Digital Wellbeing, Safety & emergency, Battery, Storage, Display, Sound, Accessibility, Date & time, Language, Reset, About phone, Software update, wallpapers.
2) Produce the decision table, every item classified: KEEP-CHILD (child can change), KEEP-READONLY (shown but not changeable), PARENT-GATED (needs parent PIN/approval from the portal or the Android 17 Supervision PIN), HIDDEN/REMOVED, FORCED (system-controlled, e.g. automatic date & time so the child cannot defeat screen-time rules). Wi-Fi and mobile data stay standard per D14: define exactly what that includes (scan/connect/forget/add network with password/QR if camera permits, saved networks, data toggle, roaming toggle, data usage/limit view, airplane mode, preferred network type, APN, SIM/eSIM management - which of these sub-items still must be parent-gated or hidden because they are bypass vectors for the no-browser/egress controls: Wi-Fi proxy, static IP/DNS, Private DNS, VPN, tethering, MAC randomisation, Wi-Fi Direct, captive-portal sign-in which needs a browser-like screen: coordinate with report 04 if present). Also include what is "fairly required" for a phone product: emergency info/SOS, location for E911, accessibility essentials, language, volume/ringtone/vibration, brightness/display timeout/font size, Bluetooth for headphones, battery, storage low warnings, software update status, About (IMEI/legal notices/open-source licences), reset (parent-gated).
3) Implementation options with a decisive recommendation: (A) keep AOSP Settings and hide/disable screens via RRO overlays + flags + removing activities in a thin fork, (B) maintain a slim fork of packages/apps/Settings with most screens deleted, (C) write a brand-new Zune Settings app (Compose) that implements the required Settings intents and Panels so SystemUI/framework/other modules do not crash, (D) hybrid: custom kid-facing Settings UI + hidden AOSP Settings for parent/engineering. Evaluate effort, upgrade/rebase cost against AOSP Q2/Q4 drops, tamper resistance (child must not reach hidden screens via intents, deep links, search, SystemUI long-press, notification shade, Settings Provider writes via adb or other apps), crash-safety (what breaks when screens are missing: SetupWizard, SystemUI QS tiles, Wi-Fi/Internet dialog, telephony carrier-config flows, emergency, DocumentsUI, accessibility shortcuts), and interplay with the SupervisionManager PIN framework. Cover SystemUI quick-settings/status bar trimming (tiles, long-press targets, lock-screen shortcuts, power menu) and the Settings search provider.
4) Parent portal side: which settings the parent can remotely set or lock (Wi-Fi allowlist? data cap? bedtime display?), how the on-device Settings enforces policy offline, how a parent PIN is created and recovered (Android 17 supervision PIN recovery), what happens on factory reset.
5) Accessibility and usability for kids (large targets, icons, reading levels, i18n) and for visually impaired kids (TalkBack equivalents in AOSP: Accessibility Suite is Google-only; what ships in AOSP? verify) - decide the minimum accessibility set.
6) Stage-1 MVP vs Stage-2 improvements, plus a concise screen map (ASCII tree) of the final Settings and the work breakdown.`,
  },
]

const TOPICS_D = [
  {
    slug: 'byo-distribution', file: '17-byo-image-distribution-installer.md', title: 'Selling the image: legal distribution, installer/flasher, device qualification, updates, licensing',
    focus: `Founder decision D15: the company SELLS THE OS IMAGE (software); customers bring a qualified phone from a curated list and install it themselves. No hardware sales. This revives the "BYO installer" path that report 02 rejected, and it interacts with D13 (curated high-end Snapdragon devices). Produce the end-to-end design for getting a working, updatable image onto a customer's own phone, and for monetising it.
1) What may legally be in the image we sell. AOSP is Apache-2.0; the Linux kernel is GPL-2.0 (source offer); but phones need OEM proprietary vendor blobs/firmware/modem/bootloader. Compare: (a) ship only system-side partitions (system, system_ext, product, possibly boot) and keep the phone's own stock vendor/firmware (Treble split; what vendor/FCM/VSR levels does an Android 17 system image require, GSI-style compatibility, what breaks), (b) installer downloads the OEM's own stock firmware at install time and extracts/derives blobs locally on the customer's machine (adevtool/extract-files style; legal posture), (c) redistribute blobs ourselves (OEM licence terms; Google's Pixel terms as a reference; Qualcomm/OEM licences), (d) a device-specific image built from LineageOS-style device trees. For each: legality, device coverage, relock/AVB feasibility, update path, engineering cost. How do LineageOS, GrapheneOS, CalyxOS, /e/OS (Murena), iodé, Volla, and any commercial BYO or kids-OS vendor handle this, and what do they charge? Include trademark/branding limits (using "Android", OEM names), EULA content, and what is actually protectable when the base is open source (our closed-source apps, backend service, installer, brand).
2) The installer/flasher. Web-based (WebUSB + fastboot; GrapheneOS and CalyxOS web installers) vs desktop app vs CLI; OS support (Windows USB drivers, macOS, Linux, ChromeOS), failure modes. Pre-flight checks (exact model/codename/region, carrier-locked or not, OEM-unlocking availability, stock firmware version and anti-rollback counters, battery, active A/B slot), bootloader unlock flow (data wipe, OEM waits such as Xiaomi's unlock delay, OnePlus/Motorola/Sony/ASUS/Nothing portals), flashing sequence, re-locking with our own AVB custom key where the device supports it (and how the verified-boot state/orange warning looks when it cannot relock), post-install verification via key attestation, hand-off to parent-portal enrolment (QR/claim code), anti-bricking safeguards, recovery/unbrick guides, support load per install, telemetry/consent in the installer. Note the installer runs on the PARENT's computer in a browser/desktop app - the child device still has no browser.
3) Device qualification program. A written Device Support Contract and test matrix; qualification lifecycle and cost per device; firmware-version pinning; regional/carrier variants; how many devices a small team can realistically support (GrapheneOS = Pixels only; LineageOS = 200+ with community maintainers); initial list size recommendation (1-3) given high-end Snapdragon preference (cross-check report 15 if present); governance for adding/removing devices; what to promise customers about EOL.
4) Updates for BYO devices. A/B OTA via update_engine and our own update server; who ships modem/bootloader/vendor firmware updates once the OEM updater no longer applies (legal and technical); security-patch cadence given AOSP Q2/Q4 source drops (cross-check reports 01 and 10); anti-rollback and downgrade protection; what happens if the customer accepts an OEM OTA by accident; bricked-device policy; end-of-support policy; staged rollout and rollback.
5) Business model and licensing. Software licence and subscription structure (one-time image licence vs per-child or per-family subscription vs both), why the CLOUD SERVICES (parent portal, AI, messaging, video calling, curated video) are the real paywall and how activation/entitlement works (device bound to parent account, hardware key attestation, offline grace period, what happens if a parent stops paying: device must remain safe and callable in emergencies), piracy/leak risk of the image, payments on a web storefront (parents, not children; taxes/VAT), refunds and bricked-phone liability, consumer-protection law (EU/UK/US), support cost per customer, comparable pricing (GrapheneOS donations, Murena paid installs and subscriptions, kids-phone subscriptions $15-20/mo).
6) Compliance shift. What disappears when we do not sell hardware (FCC/PTCRB/CE-RED equipment authorisation as manufacturer, CPSIA children's-product certification of the phone - verify whether a software product marketed for kids on third-party phones is a "children's product") and what remains or appears (carrier acceptance depends on the retained stock modem/IMS firmware and IMEI/model, warranty void, consumer-protection, export/encryption rules for software, COPPA/GDPR still apply, the legal position of telling customers to unlock bootloaders). Be specific and cite; flag counsel questions.
7) Consequences for other reports: 04 no-browser (if a phone cannot be relocked, enforcement cannot rely on verified boot: define the unlocked-state mitigations, refusing enrolment when attestation shows an unlocked bootloader, and honest marketing claims), 05 parental controls, 10 OTA/signing (our AVB/OTA keys on customers' devices; key custody), 12 telephony (VoLTE/IMS preserved from stock firmware?), 15 device selection, 02 (BYO was rejected there: re-evaluate and state what changes).
8) Recommendation, Stage-1 MVP (e.g. web installer for 1-2 qualified devices, manual qualification, licence + subscription via parent portal) and Stage-2 improvements. List the founder decisions in order of impact, with defaults.`,
  },
]

const TOPICS_E = [
  {
    slug: 'v1-provisioning-ops', file: '18-v1-flash-and-deliver-operations.md', title: 'Version-1 delivery: customers contact us, we flash the image on their qualified phone and hand it back',
    focus: `Founder decisions D15-D16: we sell the image; in VERSION 1 the first batch of users contact us, WE flash the image onto their qualified phone (and re-lock it with our own key) and give it to them; customer self-install comes later. Phones are assumed customer-supplied. Design this service so a small team can run a safe, repeatable pilot.
1) Customer journey end to end: first contact (a web form/email; parents use a browser, the child device has none), eligibility check against the qualified-device list (model/codename/region variant, carrier-locked or financed phones, stock firmware version, battery and physical condition, Google-account/FRP lock and OEM account locks such as Samsung Knox/KG, Xiaomi account, Motorola/Verizon locks, OEM-unlock waiting periods that some vendors impose), intake logistics (in-person vs mail-in; shipping, insurance, tracking, chain of custody, loaner/spare phone so the child is not left without one), explicit data-wipe consent and backup advice (unlocking the bootloader ERASES the phone), SIM/eSIM handling (eSIM profiles are lost on wipe; carrier re-issue), hand-over with parent-portal enrolment (QR/claim code), a short onboarding, and after-sales support/returns.
2) Flashing and provisioning station: bill of materials (PC, powered USB hubs, cables, charging), software (fastboot scripts or tooling, per-device image selection, flashing avb_custom_key, fastboot flashing lock, disabling OEM unlocking, key-attestation verification, per-device identity and logging), where signing keys live (images pre-signed in the release pipeline; the AVB private key must never sit on a station), throughput at 10 / 100 / 1,000 devices, unbrick and recovery procedures, the QA checklist (boot, locked state, VoLTE and SMS on a test SIM per carrier, camera, audio, GPS, charging, Wi-Fi/BT, supervision enrolment, a no-browser audit and a no-YouTube-route audit), secure erase on return, reflash/RMA, and how the same artifacts and pre-flight checks become the later customer installer (report 17).
3) Legal and policy for a flash-as-a-service: customer agreement (data wipe, warranty effects, brick risk and liability cap, consumer-protection rules by region), custody of customer property and insurance, personal data in our hands (IMEI, photos, PINs: never retain; deletion proof), OEM warranty statements for unlocked/modified phones for the candidate OEMs (verify per OEM), carrier terms on modified devices, handling of OEM firmware/blobs when we write our image to their phone (keep the customer's stock vendor partitions where possible; cross-check report 17), pilot/beta terms, children's data once enrolled (COPPA/GDPR consent flow for parents), and incident response.
4) Pilot design for "the first bunch of users": recommended cohort sizes (e.g. 10, then 25, then 100), selection criteria (families, ages, qualified phones, carriers), success metrics (install success rate, minutes per device, support tickets, parent satisfaction, child-safety incidents, bypass attempts, battery life, call/SMS reliability), feedback loop, OTA updates from day one, kill-switch and rollback plan, privacy review gates, communication to parents.
5) Costs and staffing: hands-on time per device, number of people, tooling, shipping and spare-phone float, support cost for 10 / 100 / 1,000 devices; what breaks first when volume grows; the threshold at which to build the self-install flow.
6) Dependencies and conflicts with other reports: 02 (factory flow and Pixel assumptions), 10 (flashing at scale, key custody), 15 (qualified-device list; relock MUST), 17 (BYO installer now a v2 concern), 12 (telephony QA per carrier), 04 (locked-state guarantee), 05 (enrolment).
7) Recommendation, Stage-1 MVP of the service (smallest repeatable pilot) and Stage-2 improvements, plus founder decisions in order of impact with defaults (e.g. pilot size, in-person vs mail-in, pricing of the flash service).`,
  },
]

const ALL = [...TOPICS_A, ...TOPICS_B, ...TOPICS_C, ...TOPICS_D, ...TOPICS_E]
const wanted = Array.isArray(A.topics) ? A.topics : null
const TOPICS = ALL.filter((t) => !wanted || wanted.includes(t.slug))
if (wanted) {
  const unknown = wanted.filter((s) => !ALL.find((t) => t.slug === s))
  if (unknown.length) throw new Error(`unknown topic slug(s): ${unknown.join(', ')}`)
}

// Items already flagged as unverifiable without Google's own sources. Verifiers (and
// researchers re-running these topics) must settle them against android-17.0.0_r1.
const EXTRA_VERIFY = {
  'aosp-base': `
- Does the tag android-17.0.0_r1 really carry build ID CP2A.260605.016 and SPL 2026-06-05 (report 01 says SPL is 2026-06-05, not the 2026-07-01 quoted elsewhere)? Check build/release (release configs aosp_current / cp2a / trunk_staging, flag_values, build_config/*.scl or equivalent) in the tag.
- Which of these exist on android.googlesource.com: branches android17-release, android17-security-release, android17-qpr1-release / qpr2-release (git ls-remote), tags android-security-17.*? Report 01 could not check. Also what is the exact Q4-2026 drop branch/tag name, if already visible?
- Is the supervision framework (android.app.supervision.SupervisionManager, SupervisionAppService, ROLE_SUPERVISION / ROLE_SYSTEM_SUPERVISION, config_systemSupervision, config_allowedSupervisionRolePackages, config_defaultSupervisionProfileOwnerComponent, flags supervision_manager_apis / enable_supervision_manager_policy_apis) actually present and ENABLED in the android-17.0.0_r1 tree (frameworks/base, packages/apps/Settings, build/release)? Report 01 inferred it from GrapheneOS's tree.
- What does android-17.0.0_r1's build/make/target/product (handheld_product.mk, aosp_product.mk, base_*.mk, mainline_system.mk) actually include? Browser2, Camera2, Gallery, Dialer, Messaging, WebView provider (external/chromium-webview / packages/apps/WebViewBootstrap), HTMLViewer? Produce the authoritative keep/remove input for report 03.
- Confirm Siso default / Bazel removal / lunch syntax / Cuttlefish arm64 target names, repo sync size with --partial-clone (measure with git count-objects or by listing project sizes if feasible), and recommended build-host numbers from source.android.com/docs/setup/start/requirements.`,
  'hardware-target': `
- Read Google's actual licence/terms on Pixel factory images and driver binaries (developers.google.com/android/images, /android/drivers, dl.google.com licence text) and state precisely whether a for-profit company may pre-flash and sell Pixel devices with a modified image and Google's firmware/blobs. Report 02 could only see a search summary.
- Confirm from android-17.0.0_r1's manifest (default.xml) that no device/google/<pixel> trees or Pixel driver blobs are in AOSP, and what the Cuttlefish/ generic targets are.
- Verify against source.android.com the AVB custom-key documentation (verifiedboot, avb_custom_key) and whether Pixel 9a/10a relock with a custom key works on Android 17; check Android 17 vendor support rules (VSR/FCM) relevant to older vendor images.
- Re-check Pixel 10a / 9a availability, pricing and support end dates on Google's own pages, and whether Pixel 10-series US SKUs are eSIM-only (matters for cellular in report 12).`,
}

const RESEARCH_SCHEMA = {
  type: 'object',
  properties: {
    slug: { type: 'string' },
    title: { type: 'string' },
    reportPath: { type: 'string' },
    recommendation: { type: 'string', description: 'The decisive recommendation in 4-8 sentences' },
    keyFacts: { type: 'array', items: { type: 'string' } },
    loadBearingClaims: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          claim: { type: 'string' },
          evidence: { type: 'string', description: 'URL, or repo@ref:path, or "none"' },
          basis: { type: 'string', enum: ['PRIMARY', 'SECONDARY', 'INFERRED', 'MEMORY'] },
        },
        required: ['claim', 'evidence', 'basis'],
      },
    },
    stage1Mvp: { type: 'string' },
    stage2Improvements: { type: 'array', items: { type: 'string' } },
    conflictsWithEarlierReports: { type: 'array', items: { type: 'string' } },
    risks: { type: 'array', items: { type: 'string' } },
    decisionsForFounder: { type: 'array', items: { type: 'string' } },
    crossTopicDependencies: { type: 'array', items: { type: 'string' } },
  },
  required: ['slug', 'title', 'reportPath', 'recommendation', 'keyFacts', 'loadBearingClaims', 'risks', 'decisionsForFounder'],
}

const VERIFY_SCHEMA = {
  type: 'object',
  properties: {
    slug: { type: 'string' },
    results: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          claim: { type: 'string' },
          verdict: { type: 'string', enum: ['CONFIRMED', 'CORRECTED', 'UNVERIFIED', 'REFUTED'] },
          evidence: { type: 'string' },
          correction: { type: 'string' },
        },
        required: ['claim', 'verdict', 'evidence'],
      },
    },
    severeIssues: { type: 'array', items: { type: 'string' } },
    reportUpdated: { type: 'boolean' },
  },
  required: ['slug', 'results', 'severeIssues', 'reportUpdated'],
}

const RECONCILE_SCHEMA = {
  type: 'object',
  properties: {
    slug: { type: 'string' },
    conflicts: { type: 'array', items: { type: 'object', properties: { decision: { type: 'string' }, conflict: { type: 'string' }, revision: { type: 'string' } }, required: ['decision', 'conflict', 'revision'] } },
    revisedRecommendation: { type: 'string' },
    reportUpdated: { type: 'boolean' },
  },
  required: ['slug', 'conflicts', 'revisedRecommendation', 'reportUpdated'],
}

const researchPrompt = (t) => `${BRIEF}

YOUR TOPIC: ${t.title}
${t.focus}
${EXTRA_VERIFY[t.slug] ? `\nCARRY-OVER ITEMS that an earlier run could not check against Google's own sources (settle them now if AOSP is reachable):${EXTRA_VERIFY[t.slug]}\n` : ''}
If a report for this topic already exists at ${OUT}/${t.file}, read it first and IMPROVE it in place (keep what is right, fix what is wrong, mark changes [REVISED]); otherwise write it fresh.
${REPORT_SPEC(t)}`

const verifyPrompt = (t, claims) => `${BRIEF}

You are an independent SKEPTIC. A researcher wrote the report at ${OUT}/${t.file} on: "${t.title}".
${claims ? `Their load-bearing claims:\n${JSON.stringify(claims, null, 2)}\n` : 'Read the report and take its "Load-bearing claims" section (and anything tagged [SECONDARY], [INFERRED] or [MEMORY]) as your checklist.\n'}
YOUR JOB: try to REFUTE or correct the report. Read it fully first. Then re-check every load-bearing claim and any other suspicious claim (version numbers, dates, legal citations, API/policy behaviour, "X is unavailable without GMS", licence terms, prices, carrier requirements, device specs) using DIFFERENT sources/queries than the author, preferring PRIMARY sources: if AOSP is reachable, check Android-behaviour claims against the real android-17.0.0_r1 tree rather than blogs or GrapheneOS/LineageOS forks. Pay special attention to anything the report could only support from secondary sources, and to anything time-sensitive in 2026. Also check for internal inconsistency, for violations of docs/REQUIREMENTS.md, and for obvious omissions (especially bypass routes a determined child could use, and legal duties).
${EXTRA_VERIFY[t.slug] ? `\nCarry-over items the author could not check:${EXTRA_VERIFY[t.slug]}\n` : ''}
Default to UNVERIFIED rather than CONFIRMED when you cannot find independent evidence. Do not rubber-stamp.
Then EDIT the report in place (Edit tool; ONLY ${OUT}/${t.file}): fix wrong statements inline prefixed [CORRECTED]; replace any earlier "## Verification (second pass)" section with a new final section "## Verification (second pass)" containing a table: claim | verdict | evidence | correction (state the date and whether AOSP primary sources were available). Return the structured result; reportUpdated=true only if you actually edited the file.`

const reconcilePrompt = (t) => `${BRIEF}

You are the RECONCILER for the report at ${OUT}/${t.file} ("${t.title}"). Read ${REPO}/docs/REQUIREMENTS.md, then the whole report, then any other report you need (they are in ${OUT}/).
For each founder decision D1-D16 and assumption A1-A5 that touches this topic, decide whether the report's recommendation conflicts with it (typical conflicts: "no voice/SMS in v1" vs D4-D6; any design that lets the child reach YouTube or a browser vs D1-D3; assumptions about walkie-talkie/messaging scope vs D7-D8, D10; AI scope vs D11; weather vs D9).
Then EDIT the report in place (ONLY ${OUT}/${t.file}): do not delete the original analysis; mark changed statements [RECONCILED] and append a final section "## Reconciliation with founder decisions" with a table: decision | conflict? | revised design/recommendation | effect on cost/risk. Update the report's Summary so it no longer contradicts REQUIREMENTS.md. Return the structured result.`

const criticPrompt = (done) => `${BRIEF}

You are the CROSS-TOPIC CRITIC. Read ALL reports in ${OUT}/ (00 is yours to write; 01-14 are the inputs; some may be missing) completely, including their verification and reconciliation sections.
Find: (1) CONFLICTS between reports that would break the product (e.g. no-browser vs WebView needs of an EPUB reader / video player / captive portal; no-GMS vs push, location, ML Kit, key attestation; egress allowlist vs YouTube domains and "no YouTube exit" vs the IFrame player's links; E2EE vs parental visibility vs mandatory reporting; hardware choice vs cellular/VoLTE/eSIM and relock; Q2/Q4 AOSP cadence vs a monthly patch promise; privileged in-tree apps vs updatability; OS-level age-signal laws; SMS interception/consent law vs product design) - for each name the reports, explain the failure, and propose a concrete resolution; (2) GAPS - important topics no report covers (onboarding/setup flow, accessibility, i18n, support/returns, pricing/subscriptions and payments on a no-browser device, content-moderation ops, hardware audio/PTT, emergency features, education research, team/hiring, go-to-market) and which deserve research next; (3) FACT RISKS - claims that remain UNVERIFIED/REFUTED and matter; (4) the minimum FOUNDER DECISIONS needed to unblock engineering, ordered by how much they change the plan, each with a recommended default; (5) a phased roadmap (Phase 0 foundation ... Phase N) with exit criteria, consistent with Stage 1 (everything exists) and Stage 2 (better).
Write ${OUT}/00-cross-topic-critique.md (markdown, <= 3,000 words) AND return it structured. Only write that one file.`

const CRITIC_SCHEMA = {
  type: 'object',
  properties: {
    conflicts: { type: 'array', items: { type: 'object', properties: { reports: { type: 'string' }, issue: { type: 'string' }, resolution: { type: 'string' } }, required: ['reports', 'issue', 'resolution'] } },
    gaps: { type: 'array', items: { type: 'object', properties: { topic: { type: 'string' }, why: { type: 'string' } }, required: ['topic', 'why'] } },
    factRisks: { type: 'array', items: { type: 'string' } },
    founderDecisions: { type: 'array', items: { type: 'object', properties: { decision: { type: 'string' }, recommendedDefault: { type: 'string' }, impact: { type: 'string' } }, required: ['decision', 'recommendedDefault', 'impact'] } },
    roadmap: { type: 'array', items: { type: 'object', properties: { phase: { type: 'string' }, goals: { type: 'string' }, exitCriteria: { type: 'string' } }, required: ['phase', 'goals', 'exitCriteria'] } },
  },
  required: ['conflicts', 'gaps', 'factRisks', 'founderDecisions', 'roadmap'],
}

const countVerdicts = (v) => v.results.reduce((a, x) => { a[x.verdict] = (a[x.verdict] || 0) + 1; return a }, {})
let out = { mode: MODE, topics: TOPICS.map((t) => t.slug) }

if (MODE === 'research') {
  phase('Research')
  const results = await pipeline(
    TOPICS,
    (t) => agent(researchPrompt(t), { label: `research:${t.slug}`, phase: 'Research', schema: RESEARCH_SCHEMA }),
    (r, t) => {
      if (!r) { log(`research:${t.slug} returned nothing - skipping verification`); return null }
      return agent(verifyPrompt(t, r.loadBearingClaims), { label: `verify:${t.slug}`, phase: 'Verify', schema: VERIFY_SCHEMA })
        .then((v) => ({ research: r, verification: v }))
    },
  )
  const done = results.filter(Boolean)
  const missing = TOPICS.filter((t) => !done.find((d) => d.research.slug === t.slug)).map((t) => t.slug)
  if (missing.length) log(`NOT COMPLETED: ${missing.join(', ')}`)
  out.completed = done.map((d) => ({
    slug: d.research.slug, path: d.research.reportPath, recommendation: d.research.recommendation,
    stage1Mvp: d.research.stage1Mvp, conflictsWithEarlierReports: d.research.conflictsWithEarlierReports,
    decisionsForFounder: d.research.decisionsForFounder, risks: d.research.risks,
    verification: d.verification ? { counts: countVerdicts(d.verification), severeIssues: d.verification.severeIssues } : null,
  }))
  out.missing = missing
} else if (MODE === 'verify') {
  phase('Verify')
  const results = await parallel(TOPICS.map((t) => () => agent(verifyPrompt(t, null), { label: `verify:${t.slug}`, phase: 'Verify', schema: VERIFY_SCHEMA })))
  out.verified = results.filter(Boolean).map((v) => ({ slug: v.slug, counts: countVerdicts(v), severeIssues: v.severeIssues, reportUpdated: v.reportUpdated }))
} else if (MODE === 'reconcile') {
  phase('Reconcile')
  const results = await parallel(TOPICS.map((t) => () => agent(reconcilePrompt(t), { label: `reconcile:${t.slug}`, phase: 'Reconcile', schema: RECONCILE_SCHEMA })))
  out.reconciled = results.filter(Boolean)
} else if (MODE === 'critic') {
  phase('Critic')
  out.critic = await agent(criticPrompt(), { label: 'critic', phase: 'Critic', effort: 'high', schema: CRITIC_SCHEMA })
} else {
  throw new Error(`unknown mode "${MODE}" (research | verify | reconcile | critic)`)
}

return out
