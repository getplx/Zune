# Zune research 13: Kid messenger, 1:1 video calling, and one comms backbone

Date: 2026-10-02. Tags: **[PRIMARY]** read in a real file or primary page this session (URL or repo@ref:path); **[SECONDARY]** reputable secondary or search-surfaced page; **[INFERRED]** my engineering judgement; **[MEMORY]** training knowledge, unchecked. Re-tested once: android.googlesource.com is still 403. Also unreachable: livekit.io, docs.livekit.io, legislation.gov.uk, law.cornell.edu, unicode.org. Reports 01-03 existed when I wrote this; 08 did not. Scope is D7, D8, D10 in `docs/REQUIREMENTS.md`.

## 1. Summary & recommendation

- **Build one thin first-party comms service ("Zune Comms")**: Go, REST + one multiplexed WebSocket per device, Postgres as the source of truth, Redis for fan-out. Do not adopt Matrix, XMPP or the Signal protocol for Stage 1. The authorization model is a parent-approved contact graph, not room membership, and all the off-the-shelf options need that logic bolted on plus a lot of removed features.
- **One identity and one contact graph** feed everything: messenger, video, walkie-talkie, and the cellular allowlists. People are *principals* (kid or guardian). A contact is an edge with per-channel grants, schedules, and a state machine. Cross-family edges need **both guardians' approval**, via a parent-issued invite code. No phone-number matching, no address-book upload, no kid-searchable directory.
- **Messages are server-readable**, envelope-encrypted at rest per family, with 180-day retention. Both families' guardians can read a thread, and the kid sees a notice saying so. No E2EE in Stage 1. It conflicts with D6/D7 review, server-side moderation and NCMEC reporting. WebAuthn PRF support is too uneven to hold a parent key reliably.
- **LiveKit is the single media plane** for both 1:1 video and live push-to-talk: Apache-2.0 server and Android SDK, built-in TURN, server APIs to end calls. Start on LiveKit Cloud (US region), keep the self-host path open. SFU rather than P2P, even for 1:1, because the server must be able to end a call and the parent can join later.
- **No recording, no covert listening in Stage 1.** Parents get metadata plus a remote "end call". Recording and monitoring law is unsettled once another family's child is on the call.
- **Push without GMS** is a persistent system-app connection (privileged FGS start, Doze allowlist), relaxed during scheduled quiet hours. UnifiedPush is not needed for first-party apps.
- **Launch US only (A1).** UK OSA, EU DSA and the lapsed EU scanning derogation make other markets a separate legal workstream.

## 2. Findings

**F1. Licences decide several options.**

| Component | Licence | Basis |
|---|---|---|
| Synapse (Matrix) | AGPLv3 *or* paid Element Commercial License (dual) | [PRIMARY] element-hq/synapse@develop:README.rst |
| matrix-rust-sdk; Continuwuity (Conduit fork) | Apache-2.0 | [PRIMARY] matrix-org/matrix-rust-sdk@main:LICENSE; continuwuity/continuwuity@main:LICENSE |
| libsignal (Signal protocol) | **AGPL-3.0** | [PRIMARY] signalapp/libsignal@main:LICENSE |
| ejabberd / Smack (XMPP client) | GPLv2 / Apache-2.0 | [PRIMARY] processone/ejabberd@master:COPYING; igniterealtime/Smack@master:LICENSE |
| Prosody | MIT | [SECONDARY] https://en.wikipedia.org/wiki/Prosody_(software) |
| LiveKit server; Android SDK | Apache-2.0 | [PRIMARY] livekit/livekit@master:LICENSE; livekit/client-sdk-android@main:LICENSE |
| Noto Color Emoji | font OFL-1.1; tools Apache-2.0 | [PRIMARY] googlefonts/noto-emoji@main:README.md, fonts/LICENSE |

**F2. Matrix on a no-GMS device is awkward.** Element X (the maintained Matrix client on matrix-rust-sdk) requires a push provider and has no background-sync mode; one issue reports UnifiedPush via ntfy still contacting `fcm.googleapis.com` [SECONDARY] https://github.com/element-hq/element-x-android/issues/6551 . Synapse is Python+Postgres, ops-heavy at scale [INFERRED].

**F3. Android 17 background rules (what I could confirm).**
- For apps targeting API 37, background audio playback, focus and volume calls need a foreground service with while-in-use capability, else they fail silently [PRIMARY] https://developer.android.com/about/versions/17/behavior-changes-17 . The pages I fetched list no other background-network or Doze change (absence is not proof; verify on Cuttlefish).
- `START_FOREGROUND_SERVICES_FROM_BACKGROUND` is `signature|privileged|...`, "not for use by third-party applications" [PRIMARY] aosp-mirror/platform_frameworks_base@android16-qpr1-release:core/res/AndroidManifest.xml (mirror stale; this code changes slowly).
- `allow-in-power-save` sysconfig is honoured from partitions with `ALLOW_OVERRIDE_APP_RESTRICTIONS`; `system_ext` is `ALLOW_ALL` [PRIMARY] same repo@ref:services/core/java/com/android/server/SystemConfig.java.
- FGS `remoteMessaging` has no runtime prerequisite; `phoneCall` needs `MANAGE_OWN_CALLS` [PRIMARY] https://developer.android.com/develop/background-work/services/fgs/service-types .
- Carrier NAT idle timeouts are said to be as short as ~30 s; persistent-connection apps report single-digit % daily battery [SECONDARY] https://github.com/binwiederhier/ntfy-android/pull/113 (not measured on our hardware).

**F4. WebRTC without GMS is solved.** LiveKit Android depends on `io.github.webrtc-sdk:android-prefixed` (144.7559.14) with no Play Services dependency [PRIMARY] livekit/client-sdk-android@main:gradle/libs.versions.toml, livekit-android-sdk/build.gradle. libwebrtc on API >= 29 treats any `isHardwareAccelerated()` MediaCodec as a usable hardware encoder, so Tensor's Codec2 names are not excluded [PRIMARY] webrtc-sdk/webrtc@m144_release:sdk/android/api/org/webrtc/HardwareVideoEncoderFactory.java. Encoder/decoder factories can be overridden [PRIMARY] LiveKitOverrides.kt. Tensor G4 lists H.264/H.265/VP9/AV1 encode, but none is used by Google's camera app, so real behaviour is unknown [SECONDARY] https://www.androidauthority.com/pixel-10-video-recording-av1-vp9-3586429/ .

**F5. LiveKit control surface.** RoomService has `DeleteRoom`, `RemoveParticipant`, `MutePublishedTrack`, `SendData`; tokens carry `hidden`, `canPublish`, `canSubscribe`, `recorder` grants; the server advertises "UDP/TCP/TURN" and multi-region [PRIMARY] livekit/protocol@main:protobufs/livekit_room.proto, auth/grants.go; livekit/livekit@master:README.md. Cloud prices (Ship $50 incl. 150k participant-min, $0.0005 overage, $0.12/GB down; Scale $500 incl. 1.5M, $0.0004, $0.10/GB) are from aggregator pages; the official page is blocked [SECONDARY] https://checkthat.ai/brands/livekit/pricing .

**F6. NAT reality.** Vendor blogs put TURN/relay use at 15-30% of WebRTC sessions, 25-35% for mobile-heavy apps [SECONDARY] https://www.forasoft.com/learn/video-streaming/articles-streaming/nat-stun-turn-ice-webrtc . With an SFU the client only needs outbound UDP, or TCP/TLS fallback, to one public endpoint.

**F7. Emoji.** Noto Color Emoji has tag `v2026-09-24-unicode18_0` [PRIMARY] `git ls-remote --tags googlefonts/noto-emoji`. Android 17 reportedly shipped without Emoji 17.0 [SECONDARY] https://blog.emojipedia.org/google-debuts-emoji-17-0-support/ , so we should bundle our own current font. `androidx.emoji2` is 1.7.0 (2026-09-23), but `emoji2-emojipicker` appears only as alpha (1.0.0-alpha03, 2023) on the release page I fetched [PRIMARY] https://developer.android.com/jetpack/androidx/releases/emoji2 . It has no age filter either way.

**F8. Parent-key E2EE is fragile.** WebAuthn PRF works in Chrome/Edge desktop >= 128 and Chrome Android >= 130; Safari 18+ only with iCloud Keychain platform passkeys; Firefox only with hardware keys; cross-device/QR flows return no PRF output [SECONDARY] https://www.corbado.com/blog/passkeys-prf-webauthn .

**F9. Precedents.** Messenger Kids: parents approve contacts and can download chats; a 2019 bug let group chats link kids to contacts their parent had not approved, which is why groups stay out [SECONDARY] https://techcrunch.com/2019/07/23/facebook-fails-to-keep-messenger-kids-safety-promise . iOS 26 pauses FaceTime audio/video on-device when nudity is detected, default on for under-13 accounts [SECONDARY] https://9to5mac.com/2025/07/02/facetime-in-ios-26-will-freeze-your-call-if-someone-starts-undressing/ . Perspective API shuts down end of 2026, so do not build moderation on it [SECONDARY] https://arxiv.org/html/2604.25580v2 .

**F10. Law (see section 4.7).** Amended COPPA Rule: effective 2025-06-23, compliance by 2026-04-22, written retention policy, separate consent for third-party disclosure [SECONDARY] https://www.davispolk.com/insights/client-update/ftc-prioritizes-coppa-enforcement-new-compliance-obligations-take-effect . The REPORT Act added enticement and child sex trafficking to 18 U.S.C. 2258A reports and raised preservation to one year; no duty to monitor [SECONDARY] https://www.globalchildexploitationpolicy.org/content/gpp-ncmec/us/en/policy-advocacy/reporting-by-online-platforms.html . Eleven states require all-party consent to record calls (CA, DE, FL, IL, MD, MA, MT, NV, NH, PA, WA) [SECONDARY] https://vibe.us/blog/one-party-two-party-consent-states/ ; parental "vicarious consent" exists only where courts adopted it and needs good faith [SECONDARY] https://caselaw.findlaw.com/court/us-6th-circuit/1030215.html .

## 3. Options & trade-offs

**3.1 Messenger stack** (1:1 text+emoji, receipts, offline, 100k kids)

| Option | For | Against | Verdict |
|---|---|---|---|
| Matrix (Synapse/Conduit + rust-sdk) | Receipts/offline/multi-device free; E2EE later | Authz is room-based, so we write a module/appservice to enforce the parent graph and expose reading; must disable federation, groups, media repo, previews; Synapse AGPL or commercial licence; Element X push gap (F2) | Reject for Stage 1 |
| XMPP (Prosody + Smack) | Standards for receipts, MAM archive, stream management [MEMORY]; roster subscription resembles our edge; all permissive except ejabberd | Parent graph, schedules, call-kill, portal reads and moderation still custom (Lua/Erlang modules); second runtime; Smack is dated | Best "buy" fallback |
| Signal protocol | Strong E2EE | libsignal AGPL; kills parent review and server moderation | Reject |
| MQTT | Tiny keepalive | No store, ACLs, history | Not needed |
| **Custom WS + Postgres** | Exact semantics; moderation in-line; smallest attack surface; one runtime | We own reliability (idempotency, ordering, resync) | **Recommend** [INFERRED] about 3k lines for 1:1 text |

**3.2 Parent visibility and crypto**

| Mode | Parent review | Server moderation / 2258A | Breach impact | Cost |
|---|---|---|---|---|
| **A. Server-readable, per-family envelope encryption** | Full, instant | Full | DB-only leak = ciphertext; app/KMS compromise = plaintext within retention | Low |
| B. E2EE, parent browser as extra recipient (PRF/passkey) | Only if parent key present; history lost on key loss | Client-side only | Smallest | High; PRF gaps (F8) |
| C. Client-side escrow to parent key | Same as B | Weak | Medium | High |
| D. Metadata + flagged excerpts | Partial | Needs plaintext anyway | Smaller | Low; Stage 2 per-age mode |

Recommend A with schema hooks: `visibility_mode`, `enc_key_id`. Disk-level encryption alone is a checkbox; field-level keys per family are what protect against backup or SQL leaks.

**3.3 Media plane**

| Option | Verdict |
|---|---|
| P2P + coturn | Cheapest bytes, but cannot force-end a call, NAT-fragile, parent join needs renegotiation |
| **LiveKit Cloud now, self-host later (same Apache-2.0 code)** | **Recommend**: no Stage-1 ops, server-side kick, hidden/recorder participants available later |
| Self-host day 1 | Right at scale; premature ops now |
| Jitsi / Stream / Pion | Conference-shaped / proprietary SaaS / toolkit; none fits as well |

**3.4 Push without GMS:** persistent connection (**recommend**) vs UnifiedPush (extra distributor app, aimed at third-party apps) vs polling (misses live calls and PTT). We own the OS, so the connection is a privileged system service.

## 4. Recommended Stage-1 design

### 4.1 Trust model and contact graph
- **Principals:** `guardian` (portal login, passkeys) and `kid` (created by a guardian, bound to a paired device). Opaque UUIDs; a display name and avatar chosen from a fixed set by the guardian. No username search.
- **Edges:** one row per pair. `state`: proposed, active, revoked, blocked. Per-side `grants` {msg, video, ptt} and optional schedule. **Effective permission = edge active AND both sides' grants AND both schedules open AND neither account suspended.** PSTN contacts live in the same table as unilateral endpoints (inbound/outbound/SMS-forward flags) set by one guardian. The device keeps a signed policy snapshot and fails closed.
- **Invite flow (Stage 1):** Guardian A creates a one-time 10-char code/link/QR (48 h expiry, rate-limited), sends it out of band or via an SMS the portal sends to a number A typed. Guardian B opens it, sees A's verified name and A's kid's first name and avatar, attests "I know this family", picks which kid, and sees the consent line: "both families can read this conversation". Edge goes active. Kid-initiated QR bump is Stage 2 and also needs both approvals.
- **Anti-abuse:** edge cap (25 per kid [INFERRED]), invite throttles, T&S alert when one guardian invites many families. The weakest link is Guardian B's judgement; a hostile adult still needs a purchased device and a guardian account.
- **Revoke:** either guardian, effective immediately: messages blocked, live call or PTT ended server-side, the other side sees a neutral "not available". The thread leaves both kid devices; the portal keeps it for the retention period unless a safety hold applies; re-adding needs a new handshake.
- **Block/report (kid):** Block hides at once and notifies the kid's guardian, who can lift it. Report sends the last 20 messages to the T&S queue and the guardian.
- **Schedules:** per-kid, per-channel windows (school, bed), enforced on the server (messages deferred but stored; call and PTT tokens refused) and in the device UI. 911 and parent contacts are exempt.

### 4.2 Backbone

```
 Kid device (Zune OS)                        Cloud
 +----------------------------+     +--------------------------------------------+
 | Messenger | Walkie | Video |     |  LB/TLS                                     |
 |   UI         UI       UI   |     |    |                                        |
 |  Comms Service (priv-app,  |<WS->| comms-api (Go, stateless x3)                |
 |  1 WebSocket, FGS+Doze     |     |  - authN device/guardian   - policy engine  |
 |  allowlist, policy cache)  |     |  - msg service + moderation pipeline        |
 |  LiveKit Android SDK       |     |  - call/PTT orchestrator (token minting)    |
 +-------------+--------------+     |  - T&S + NCMEC job   - audit log           |
               | UDP / TCP / TLS    +------+----------------------+---------------+
               v                           |                      |
        +--------------+  webhooks   +-----v----+  +-------+  +---v-----+
        | LiveKit (SFU |------------>| Postgres |  | Redis |  |  KMS    |
        | + TURN)      |<--RoomSvc---+ (graph,  |  |pub/sub|  | per-    |
        +------^-------+   API       |  msgs)   |  +-------+  | family  |
               | (Stage 2)           +----------+             | DEKs    |
 Parent portal (browser SPA) --REST/WS--> comms-api            +---------+
   passkeys, thread viewer, flags, approve/revoke, end call
   (later) livekit-client-js joins as guardian principal
```

**WS protocol sketch (JSON, versioned):** `hello{device_token, cursor}` -> `ready{cursor, policy_ver}`. `msg.send{cid, conv, body}` -> `msg.ack{cid, id, seq, status: accepted|blocked(code)}`; peer receives `msg.new`, returns `msg.delivered`. `policy.update{ver}` triggers a signed policy fetch. `call.invite/accept/decline/end` and `ptt.open/ptt.invite` carry short-lived LiveKit tokens (identity = principal id, TTL <= 10 min). Offline delivery: every message writes `user_events(user_id, cursor)` rows for both parties; reconnect sends `cursor` and receives the gap. Client `cid` makes sends idempotent; per-conversation `seq` orders them.

### 4.3 Messenger
- Body: Unicode text only, <= 500 chars, no attachments, links, stickers or GIFs. Sent/delivered ticks in Stage 1; read receipts and typing indicators off (social pressure, little value).
- **Emoji:** own Compose picker built from Unicode `emoji-test.txt` and an **age-band allowlist** (two bands: ~5-9, ~10-13). The denylist covers sexual-connotation, weapon, drug/alcohol and gesture codepoints plus sequences (e.g. eggplant+splash). The server re-validates every message. Skin tone is a stored per-kid preference. Bundle the current Noto Color Emoji tag in the system image (OFL permits).
- **Moderation, server-side, in the send path (<20 ms):** normalise (NFKC, strip zero-width, leetspeak map), then
  1. *Hard block with kid-friendly notice*: URLs/domains, phone numbers, emails, street-address patterns, app handles ("snapchat", "@name"), severe profanity and slurs.
  2. *Deliver and flag to portal*: bullying, self-harm cues, secrecy ("don't tell your parents"), "send a pic", age/location probes, meet-up asks.
  3. *Async ML* is Stage 2. Sending kids' text to a vendor classifier is a COPPA third-party disclosure question; prefer a self-hosted model.
  On-device does only instant UX checks (emoji set, length, URL/PII regex); the server is authoritative.
- Keyboard: the system IME must offer no GIF, sticker, cloud suggestion or emoji search (dependency on report 03; see section 6).

### 4.4 Video, walkie-talkie, parent-side hook
- **Video:** `call.invite` over WS; the callee shows an incoming-call screen via a self-managed Telecom call (`MANAGE_OWN_CALLS`, `phoneCall` FGS) so it coexists with cellular calls. Room `call_<uuid>`, 2 tokens, camera+mic. Cap 360p/24 fps (~0.64 Mbps incl. audio [INFERRED]). VP8 default; enable hardware H.264 only after a 9a/10a bench (F4).
- **Safety:** `FLAG_SECURE` on call and chat windows blocks screenshots and capture [PRIMARY] aosp-mirror/platform_frameworks_base@android16-qpr1-release:core/java/android/view/WindowManager.java ; pre-grant `CAMERA`/`RECORD_AUDIO` to Zune apps only; keep SystemUI privacy indicators and sensor toggles [MEMORY]; portal shows live call status and an **End call** button (`DeleteRoom`); no recording; no hidden listening.
- **Walkie-talkie:** live-only, ephemeral audio room per pair, Opus. The Walkie screen pre-joins subscribe-only so the button just publishes; the peer's Comms Service auto-joins on `ptt.invite`. Peer offline means "not available" (no voice clips, since stored child voice is a consent and breach liability). Parent sees metadata (who, when, how long).
- **Deferred parent-side calling fits already:** the authz function is principal-agnostic, guardian-to-own-kid edges exist implicitly, tokens come from the same endpoint, and the portal adds `livekit-client-js` plus Web Push [MEMORY for JS SDK licence]. Nothing in Stage 1 hard-codes "kid".

### 4.5 Device connection and battery
One WebSocket for all channels, owned by a privileged in-tree service (`ZuneComms`): `START_FOREGROUND_SERVICES_FROM_BACKGROUND`, an `allow-in-power-save` entry in `vendor/zune/sysconfig`, reconnect on `ConnectivityManager` callbacks. Adaptive heartbeat (probe up from ~30 s, remember per network type). In scheduled quiet hours it relaxes to 15-30 min check-ins, since nothing may be delivered then; parent "end"/lock commands still land. Target <= 3% battery/day idle [INFERRED, unmeasured].

### 4.6 Capacity and cost [INFERRED]
- **100k kids:** ~100k always-on WebSockets on 3-4 nodes. At 100 msgs/kid/day: 10M/day, ~115/s average, ~1.2k/s peak, ~1 GB/day; one partitioned Postgres primary suffices.
- **Video, 10k kids** (10% make one 10-minute call a day = 600k participant-min/month): Ship plan ~$275 plus ~2.9 TB egress at $0.12/GB ~$345, so **about $0.06 per kid per month**; ~0.6 GB and ~$0.13 per 1:1 call-hour. At 100k kids on Scale ~$5k/month; self-hosting later saves an estimated 60-80%. Revisit at $3-5k/month. Messaging infra for 10k kids: a few hundred dollars per month.

### 4.7 Compliance touchpoints
| Area | What changes when kids of different families talk | Stage-1 action |
|---|---|---|
| COPPA | Child text, voice and video are personal information; the other family is not the consenting parent; processors (LiveKit, KMS, any classifier) need contracts | Consent screens name both families' visibility; written retention policy; DPAs; counsel on "support for internal operations" |
| 18 U.S.C. 2258A | Operator reports enticement/CSAM it learns of; preserve 1 year | NCMEC ESP registration, named T&S owner, 24 h SLA, legal-hold vault, law-enforcement request process |
| Recording laws | Parent monitoring a call touches another family's child; 11 all-party states | No recording or covert listening; both families accept call terms at link time |
| UK OSA / AADC | A text and video messenger is likely a user-to-user service; duties live since 2025 [SECONDARY]; the SMS/MMS, 1:1 live voice and email exemptions probably do not cover it [MEMORY] | No UK launch in Stage 1 |
| EU DSA | Private messaging is outside "online platform" and small firms are exempt from Art. 28 [SECONDARY] https://www.cms-digitallaws.com/en/dsa/recital-14/ ; the voluntary CSAM-scanning derogation lapsed 3 Apr 2026 [SECONDARY] https://dig.watch/updates/eu-eprivacy-derogation-csam-detection-expires | No EU launch in Stage 1; server-side scanning would need a new legal basis |
| US states | Minor-messaging and app-store age laws are moving [MEMORY] | Counsel check before launch |

## 5. Stage-2 improvements
Kid-initiated QR bump with dual approval; typing and read receipts as parent toggles; per-age visibility (metadata + flagged excerpts for 11-13); self-hosted ML moderation and grooming scoring; parent-side video/voice and consented live listen-in with a visible indicator; on-device sender-side nudity detection that pauses video (Apple precedent) [INFERRED: ~1 fps, unbenchmarked]; hardware-encoder tuning; warm-room PTT; curated first-party stickers; voice notes and photos (with scanning and consent); reactions; device-key attestation; optional parent-key E2EE tier; self-hosted LiveKit; groups only much later, with the Messenger Kids lesson encoded as a test (a group must never connect unapproved pairs).

## 6. Conflicts with earlier reports (01-11)
- **02 (hardware) and 03 (minimal product):** both say v1 is Wi-Fi plus optional data SIM with no voice/SMS (02 decision 3, 03 Q1). D4 supersedes that, and messenger, video and walkie-talkie also need data away from Wi-Fi, so a data-capable SIM or eSIM becomes part of the product.
- **03:** keeps stock `LatinIME` (needs the no-GIF, no-cloud-suggestion, no-emoji-search configuration from 4.3, possibly a patch under 03's Q7 budget). Its product list has `ZuneWalkie` but no messenger, call UI or comms service; add `ZuneComms` to the in-tree privileged set (with `privapp-permissions`) and `ZuneMessenger`/`ZuneCall` as prebuilt apps. 03's `vendor/zune/sysconfig/` is where the power-save allowlist goes.
- **02:** Tensor G4 is fine for software VP8 and plausible for hardware H.264; untested. **01:** no conflict (no-GMS premise matches).
- **08 (walkie-talkie/comms) was not present.** The brief says it assumed no telephony in v1; if it also proposed its own transport, identity or push channel, this report replaces that with the shared backbone and LiveKit. **05, 07, 11** were also absent: 05 must adopt the contact graph, visibility mode and retention default, 11 the consent flow.

## 7. Risks & unknowns
1. Persistent-connection battery and carrier NAT timeouts are unmeasured; a bad result forces a relay or longer-interval design.
2. Guardian B's approval is the safety gate; social engineering of parents is the main cross-family threat.
3. The server-readable store is a high-value target; one breach of children's chats is existential. Needs KMS discipline, break-glass staff access, audit logs.
4. T&S and NCMEC readiness is a staffing dependency for the first cross-family contact.
5. Android 17 background behaviour for a privileged service, and hardware-codec behaviour under WebRTC on Tensor, are inferred, not tested.
6. LiveKit Cloud prices and DPA terms are secondary or unverified; rules-only moderation will miss subtle grooming and bullying.
7. Not verified: current emoji2-emojipicker releases, AOSP's bundled emoji version, exact OSA exemptions, state laws.
8. Building our own messenger risks reliability bugs; mitigated by idempotent sends, sequence numbers, and an XMPP fallback if the schedule slips.

## 8. Decisions needed from the founder (by impact)
1. **Both families' guardians read the whole thread, kid told so.** Default: yes. Alternative: metadata-only for older kids.
2. **Dual-guardian approval via a parent-issued code; no kid-initiated discovery in Stage 1.** Default: yes.
3. **No recording and no covert listening on video or walkie-talkie.** Default: yes; revisit with counsel.
4. **Launch US only; exclude UK/EU from Stage 1.** Default: yes.
5. **Fund T&S and NCMEC reporting before the first cross-family link goes live.** Default: named owner, 24 h SLA.
6. **Custom comms service rather than Matrix/XMPP.** Default: custom; XMPP as fallback.
7. **LiveKit Cloud first, self-host past ~$3-5k/month.** Default: US region plus a DPA.
8. **Retention: 180 days content, 13 months metadata.** Default: as stated.
9. **Require a data plan on every device** (conflict with 02/03). Default: yes.
10. **Age bands for emoji and moderation tuning.** Default: 5-9 and 10-13.

## 9. Load-bearing claims
| # | Claim | Evidence | Basis |
|---|---|---|---|
| 1 | Synapse is AGPLv3 or a paid commercial licence | element-hq/synapse@develop:README.rst | PRIMARY |
| 2 | libsignal is AGPL-3.0 | signalapp/libsignal@main:LICENSE | PRIMARY |
| 3 | LiveKit server and Android SDK are Apache-2.0; server has TURN; RoomService has DeleteRoom/RemoveParticipant; tokens have hidden/canPublish grants | livekit/livekit@master:LICENSE, README.md; livekit/protocol@main:protobufs/livekit_room.proto, auth/grants.go | PRIMARY |
| 4 | LiveKit Android uses webrtc-sdk with no Play Services dependency; libwebrtc accepts any hardware-accelerated MediaCodec on API >= 29 | livekit/client-sdk-android@main:livekit-android-sdk/build.gradle; webrtc-sdk/webrtc@m144_release:sdk/android/api/org/webrtc/HardwareVideoEncoderFactory.java | PRIMARY |
| 5 | Privileged apps may start FGS from background; `allow-in-power-save` is honoured in system_ext | aosp-mirror/platform_frameworks_base@android16-qpr1-release:core/res/AndroidManifest.xml; services/core/java/com/android/server/SystemConfig.java | PRIMARY |
| 6 | Android 17 requires a while-in-use FGS for background audio (targetSdk 37) | https://developer.android.com/about/versions/17/behavior-changes-17 | PRIMARY |
| 7 | Element X needs a push provider and may still touch FCM under UnifiedPush | https://github.com/element-hq/element-x-android/issues/6551 | SECONDARY |
| 8 | Amended COPPA: effective 2025-06-23, compliance 2026-04-22, retention policy, separate third-party consent | https://www.davispolk.com/insights/client-update/ftc-prioritizes-coppa-enforcement-new-compliance-obligations-take-effect | SECONDARY |
| 9 | REPORT Act: enticement reportable, 1-year preservation, no duty to monitor | https://www.globalchildexploitationpolicy.org/content/gpp-ncmec/us/en/policy-advocacy/reporting-by-online-platforms.html | SECONDARY |
| 10 | WebAuthn PRF is not reliable across browsers/credential types; 11 states are all-party consent | https://www.corbado.com/blog/passkeys-prf-webauthn ; https://vibe.us/blog/one-party-two-party-consent-states/ | SECONDARY |
