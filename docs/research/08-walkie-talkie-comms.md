# Zune research 08: Walkie-talkie (push-to-talk) and safe kid-to-kid voice

Date: 2026-10-02. Scope: D10, with D4, D5, D7, D8 from `docs/REQUIREMENTS.md`. Tags: **[PRIMARY]** read in a real file or primary page this session; **[SECONDARY]** secondary source, including figures carried over from reports 12 and 13 that I could not re-check; **[INFERRED]** my judgement or arithmetic; **[MEMORY]** training knowledge, unchecked. Only developer.android.com and GitHub were reachable and the WebSearch budget ran out, so every statute, FCC rule, vendor price and vendor child-data term below is unverified and tagged accordingly.

## 1. Summary & recommendation

- **Build push-to-talk as Opus frames relayed over Zune's own authenticated WebSocket (the "Zello-style" model [MEMORY]), not as a WebRTC SFU room.** Half-duplex 1:1 speech at 16 kbps does not need an SFU, ICE or UDP. A relay needs no third-party processor of children's voice, has no join latency, and gives the server a policy hook on every frame. At 10k kids it costs tens of dollars per month in bandwidth, against roughly $5k to $7k on LiveKit Cloud with join-on-press [INFERRED from secondary prices]. This changes only the walkie-talkie transport in report 13 section 4.4. LiveKit stays for 1:1 video and is the Plan B for PTT.
- **Cloud-only in v1.** Nearby Connections is GMS-only. Wi-Fi Aware and BLE need per-device qualification and give no parental visibility offline, so they are a Stage 2 "near me" mode between approved contacts.
- **Identity and trust: report 13's contact graph, unchanged.** The server ends open streams at schedule windows and on revoke.
- **Parent visibility in v1 is metadata only.** "Recorded and reviewable for 72 hours" is a per-edge, both-guardian opt-in on the same relay, held until counsel signs off. We never claim to detect grooming in voice.
- **Telephony:** cellular voice and SMS use the carrier's native VoLTE path (report 12), so 911 always works from the real dialer. Zune PTT and video are closed-loop and never bridge to the PSTN.
- **Android 17 forces one structural choice.** Transmit starts from the visible Walkie activity. Incoming playback runs in a privileged system service holding `MODIFY_AUDIO_SETTINGS_PRIVILEGED`, so it is not silenced in the background.

## 2. Findings

**F1. Android 17 background audio.** All apps need a visible activity or a non-`SHORT_SERVICE` foreground service (FGS) to play audio, take focus or change volume; apps targeting API 37 also need while-in-use (WIU) capability. Failures are silent. Telecom VoIP apps are "unlikely to be impacted" [PRIMARY] https://developer.android.com/about/versions/17/changes/bg-audio . In the Android 17 tree, holders of `MODIFY_AUDIO_SETTINGS_PRIVILEGED`, `MODIFY_AUDIO_ROUTING` or `MODIFY_PHONE_STATE`, and UIDs below `AID_APP_START`, are exempt; apps targeting below API 37 get only partial enforcement; the first two permissions are `signature|privileged` [PRIMARY] GrapheneOS/platform_frameworks_base@17:services/core/java/com/android/server/audio/HardeningEnforcer.java, core/res/AndroidManifest.xml. I read only the Java focus path.

**F2. Microphone.** A `microphone` FGS cannot be created from the background or a `BOOT_COMPLETED` receiver [PRIMARY] https://developer.android.com/develop/background-work/services/fgs/service-types . Screen-off transmit is not an ordinary-app feature.

**F3. Waking a no-GMS device.** Doze suspends network and ignores wake locks; `setExactAndAllowWhileIdle` fires at most once per 9 minutes per app; a battery exemption gives network plus partial wake locks [PRIMARY] https://developer.android.com/training/monitoring-device-state/doze-standby . GrapheneOS describes the standard recipe: FGS, battery exemption, polling throttled on reliable networks [PRIMARY] GrapheneOS/grapheneos.org@main:static/faq.html. ntfy's persistent connection costs "about 0-1% of battery in 17h" on the author's phone (n=1) [PRIMARY] binwiederhier/ntfy@main:docs/faq.md. Element X's F-Droid flavour is `AlarmManager`-only, which its docs call unreliable for network work [PRIMARY] element-hq/element-x-android@develop:docs/notifications.md. Carrier NAT drops idle sockets at 25 to 60 s [SECONDARY via report 13].

**F4. Nearby Connections is unusable.** The open-source `google/nearby` (Apache-2.0) has platform implementations for `apple`, `g3` and `windows` only, and its Android sharing README drives `com.google.android.gms` intents, so the Android build is closed [INFERRED]. microG's `play-services-nearby` implements only Exposure Notification [PRIMARY] google/nearby@main:internal/platform/implementation, sharing/android/README.md; microg/GmsCore@master:play-services-nearby/core.

**F5. Local radios.** *Wi-Fi Aware:* API 26, `FEATURE_WIFI_AWARE`, `NEARBY_WIFI_DEVICES`, PSK-secured data path, ~255-byte discovery messages [PRIMARY] https://developer.android.com/develop/connectivity/wifi/wifi-aware . *Wi-Fi Direct:* needs `NEARBY_WIFI_DEVICES` and location mode on; concurrency with infrastructure Wi-Fi is undocumented [PRIMARY] https://developer.android.com/develop/connectivity/wifi/wifip2p . *BLE:* data is readable by all apps on the device, so it needs app-layer crypto [PRIMARY] https://developer.android.com/develop/connectivity/bluetooth/ble/ble-overview . *Android 17:* `ACCESS_LOCAL_NETWORK` is mandatory for LAN access when targeting API 37 [PRIMARY] https://developer.android.com/about/versions/17/behavior-changes-17 .

**F6. No PTT key in AOSP.** Android 17's `KeyEvent` has no PTT keycode (it has `KEYCODE_HEADSETHOOK`, `KEYCODE_VOICE_ASSIST`, `KEYCODE_STEM_PRIMARY`) [PRIMARY] GrapheneOS/platform_frameworks_base@17:core/java/android/view/KeyEvent.java. Rugged phones use vendor intents [MEMORY]; mainstream Snapdragon targets have no PTT key, so use an on-screen button.

**F7. Codec.** Android 10+ ships a `MediaCodec` Opus encoder; decoding works from 5.0 [PRIMARY] https://developer.android.com/media/platform/supported-formats . libwebrtc recommends 16 to 20 kbps for wideband speech and defaults to 20 ms frames [PRIMARY] webrtc-sdk/webrtc@m144_release:modules/audio_coding/codecs/opus/audio_encoder_opus.cc. LiveKit's Android SDK defaults to a 48 kbps "music" preset with DTX and RED on (`TELEPHONE` is 12 kbps, `SPEECH` 24 kbps) and has a `preconnect` buffer [PRIMARY] livekit/client-sdk-android@main:.../room/participant/LocalParticipant.kt.

**F8. SFU and relay components.** LiveKit server is Apache-2.0; defaults include TCP fallback on 7881, `auto_create: true`, empty-room timeout 300 s, and every codec (video included) enabled, though `EnabledCodecs` can be narrowed to Opus [PRIMARY] livekit/livekit@master:pkg/config/config.go. Janus is GPL-3.0, mediasoup ISC, Pion MIT [PRIMARY]. Mumble is BSD-3-Clause, Opus-based, with UDP and TCP tunnelling and a 558 kbps default per-client cap [PRIMARY] mumble-voip/mumble@master:LICENSE, docs/dev/network-protocol/voice_data.md, auxiliary_files/mumble-server.ini. Element Call is AGPL or commercial, built on LiveKit, advertises E2EE, and its README never mentions MLS [PRIMARY] element-hq/element-call README. LiveKit Cloud prices: Ship $50 with 150k participant-minutes then $0.0005; Scale $500 with 1.5M then $0.0004; $0.10 to $0.12 per GB [SECONDARY via report 13]. livekit.com and docs.livekit.io were blocked, so I have no verified SFU capacity figure and no verified child-directed terms for LiveKit, Agora, Twilio, Daily or Vonage.

**F9. Emergency calls.** When an emergency call is placed, Telecom disconnects all self-managed (VoIP-style) calls [PRIMARY] GrapheneOS/platform_packages_services_Telecomm@17:src/com/android/server/telecom/CallsManager.java.

**F10. Voice moderation is weak.** Roblox's v2 voice classifier has six classes (none is grooming); English precision is 63.9% and recall 58.2% at a 1% false-positive rate, on Roblox data [PRIMARY] Roblox/voice-safety-classifier@main:README.md. faster-whisper transcribes 13 minutes in 51 s (int8, batch 8, i7-12700K, 8 threads), about 15x realtime [PRIMARY] SYSTRAN/faster-whisper@master:README.md.

**F11. Law (all unverified here; counsel must confirm).**
- *COPPA:* a child's voice is personal information, so verifiable parental consent (VPC) comes first. Amended rule: effective 2025-06-23, comply by 2026-04-22; written security programme and retention policy; separate consent for non-integral third-party disclosure [SECONDARY via reports 12/13; MEMORY for the audio definition]. The audio-to-text exception covers immediately-deleted voice commands, not PTT relay or storage [MEMORY].
- *18 U.S.C. 2258A:* report to NCMEC on actual knowledge; one-year preservation since the REPORT Act; no duty to monitor [SECONDARY via 13; MEMORY for 2258A(f)].
- *Recording consent:* the federal Wiretap Act is one-party. The all-party core list is CA, DE, FL, IL, MD, MA, MT, NV, NH, PA, WA; some surveys count up to 15 [SECONDARY via 13].
- *FCC:* "interconnected VoIP" means two-way voice connected to and from the PSTN (47 CFR 9.3). Only such services carry E911 duties (9.11), with Kari's Law and RAY BAUM'S Act on top [MEMORY].

## 3. Options & trade-offs

**Transport**

| Option | Strengths | Weaknesses | Verdict |
|---|---|---|---|
| 1. WebRTC + SFU (LiveKit, Pion, mediasoup, Janus) | Mature jitter, loss and NAT handling; one SDK shared with video | Join latency unless pre-joined, and pre-joined rooms bill participant-minutes; child audio sits with a third party; needs UDP or TURN fallback; default tokens and codecs too permissive (F8) | **Plan B** |
| 2. Store-and-forward clips over HTTPS | Cheapest; works offline and in school mode; moderable before delivery | Not live; every clip is stored child voice | Stage 2, for "missed" only |
| **3. Opus over our WebSocket** | No setup on the warm socket; TCP retransmit means no clipped words; works on any 443-capable network; per-frame policy kill; no vendor processor | We write jitter buffer, floor control and relay (about 1.5 to 2k lines [INFERRED]); TCP head-of-line stutter on bad cellular | **Recommend** |
| 4. Mumble/Murmur | Proven PTT, BSD-3, Opus | Built for open servers, not a parent-approved graph [INFERRED]; no schedules or push; long-lived client connections; moderation needs a bot | Fallback if schedule slips |
| 5. Matrix / Element Call | E2EE, federation | Group-call shaped; AGPL or commercial licence; E2EE conflicts with parent review; heavy ops | Reject (as report 13) |

**Local modes** (all Stage 2): Nearby Connections is impossible (F4). **Wi-Fi Aware** has longer range and more throughput than Bluetooth per the docs, and a PSK path, but only where `FEATURE_WIFI_AWARE` is true. **BLE L2CAP + Opus** is the baseline: widest hardware, short range [MEMORY], 16 kbps fits easily [INFERRED], needs rotating IDs derived from a per-edge key. Skip Wi-Fi Direct (group negotiation, undocumented concurrency), Bluetooth classic (pairing UX) and same-LAN (AP client isolation). Offline enforcement works from the signed policy snapshot (report 13), but parents see nothing until reconnect.

**Parent visibility:** *None* is unsafe and leaves no abuse evidence. **Metadata (v1 default)** gives who, when, duration and outcome but weak evidence on a report. *Recorded for 72 h (30 d max)* gives playback plus ASR flags, at the cost of stored child voice, VPC, all-party consent and breach liability.

## 4. Recommended design for Zune

**Protocol (extends the report 13 WebSocket: JSON control, binary audio).**
1. `ptt.begin{cid, edge, codec}`. The sender streams frames at once, without waiting for the ack.
2. The server checks edge state, both grants, both schedules, recipient DND, rate limits and floor, then replies `ptt.ack{stream, ok | busy | unavailable}`. The code is neutral and never reveals a block.
3. The recipient gets `ptt.incoming{stream, from, play: auto | chime}` then `audio{stream, seq, ts, bundle}`. `ptt.end` or `ptt.abort` closes it. Server timers abort at the 30 s cap and at schedule boundaries.

**Audio.** `OPUS_APPLICATION_VOIP`, wideband, 16 kbps, in-band FEC on, DTX off (the button gates transmission), 20 ms frames bundled in threes, receiver jitter buffer 120 to 200 ms. Use libopus in the app; the platform encoder exposes fewer knobs [MEMORY]. Latency is about 300 to 480 ms mouth-to-ear in region, against about 185 to 335 ms for an SFU [INFERRED, unmeasured]; acceptable for half-duplex. Device audio latency varies, with no runtime API [PRIMARY] https://developer.android.com/ndk/guides/audio/audio-latency .

**Bandwidth [INFERRED arithmetic], per direction of continuous talk:** WebRTC at 20 ms packets 36 kbit/s (16.2 MB/h); at 60 ms packets 22.7 kbit/s (10.2 MB/h); WebSocket/TLS/TCP with 60 ms bundles 29.6 kbit/s (13.3 MB/h). At 8 talk-minutes per day that is about 53 MB per month per direction per kid.

**Device.**
- The Guardian/Comms system app already owns the socket (reports 05, 13). It holds `MODIFY_AUDIO_SETTINGS_PRIVILEGED`, `START_FOREGROUND_SERVICES_FROM_BACKGROUND` and an `allow-in-power-save` entry, plays incoming PTT under a partial wake lock, and gets a `ZuneWalkie` privapp-permissions entry (report 03).
- The visible Walkie activity records (F2) and hands frames to the socket owner. On-screen hold-to-talk only; headset-hook and volume-key PTT are Stage 2.
- Auto-play only when the edge allows it, outside school mode and DND, under the volume cap, with no call active; otherwise a "X tried to talk" chime with no audio.
- First test: `adb shell cmd audio set-enable-hardening enable`.

**Trust and safety.**
- Edges, dual-guardian approval, invite codes and revoke are report 13 section 4.1.
- PTT adds: one talker per edge, 30 s cap, at most 60 transmissions per hour per edge, a kid "mute contact" control, and "Tell a grown-up", which alerts guardians and flags the edge.
- **SOS:** hold 3 s sends a priority alert plus last location (if enabled) to all guardians by Web Push and optional SMS to a verified number. It bypasses schedules and offers a one-tap cellular call to a guardian and the native 911 dialer. Parent-side live voice is deferred (D8). The UI and terms say Walkie cannot call emergency services.

**Law, concretely.**
- *Required (as I understand it):* COPPA VPC before collecting a child's voice; both guardians' consent at link time; written retention and security policies; NCMEC reporting on actual knowledge; all-party consent for any recording.
- *Why metadata-only first:* a human who hears a flagged clip can create "actual knowledge", so the T&S and NCMEC runbook must precede review mode.
- *Moderation cost:* for opted-in clips, self-hosted faster-whisper plus text rules. 100% coverage at 10k kids needs about 3.6 eight-thread nodes, roughly $0.08 to $0.16 per kid per month at an assumed $0.30 per node-hour [INFERRED]. Commercial ASR is a COPPA third-party disclosure, so avoid it. Flags are assistive, never a gate (F10).

**Telephony.** v1 voice and SMS use the native carrier path (report 12). No VoIP-to-PSTN; bridging would make us an interconnected-VoIP provider with E911 duties [MEMORY]. A Wi-Fi-only device must say it has no emergency calling.

**Cost and hosting (10k kids, 8 transmit-minutes per kid per day, 1:1).**

| Item | Monthly | Basis |
|---|---|---|
| Relay egress, about 540 GB | $27 to $49 | [INFERRED]; $0.05 to $0.09/GB [MEMORY] |
| LiveKit Cloud, join-on-press, sessions at 3x talk time (14.4M participant-minutes) | $5.7k (Scale) or $7.2k (Ship) | [INFERRED] on secondary prices |
| Self-hosted LiveKit, 2 nodes plus bandwidth | $300 to $600 plus ops | [INFERRED] |
| Relay peak (3% concurrent, about 300 streams, about 10k msgs/s) | One 4-vCPU Go node | [INFERRED]; load-test |

One US region over two availability zones (A1); a second region only with a market.

**MVP cut.** 1:1 kid-to-kid between approved edges; hold-to-talk, 30 s cap, floor control with busy and unavailable tones; Opus relay on the existing socket; no ring-through, no stored audio; metadata log, rate limits, "Tell a grown-up", SOS alert; server-side schedules with abort at window edges. Ship gates: VPC, dual-guardian consent and a T&S owner before the first cross-family link. Review mode, voice messages, local mode and headset PTT are Stage 2.

## 5. Risks & unknowns

1. TCP head-of-line stutter on weak cellular. Test on target carriers. If more than a few percent of transmissions glitch, move to Plan B (LiveKit, Opus-only codecs, `SPEECH` preset, RED off, `canPublishData=false`).
2. Native Android 17 playback enforcement is unread. Confirm on a device or Cuttlefish.
3. Persistent-socket battery and NAT behaviour are unmeasured on the qualified Snapdragon devices (report 15).
4. Law and vendor terms are unverified here (sources blocked, search budget gone).
5. A hostile adult with a guardian account is the main residual threat; VPC and guardian verification are the control (report 13).
6. Voice moderation will miss grooming; do not market it. Review mode makes stored child voice the top breach target.

## 6. Decisions needed from the founder

1. **Transport:** own-WebSocket relay (default) or LiveKit PTT for one shared SDK.
2. **Offline use:** cloud-only v1 (default), or "works with no internet" required at launch.
3. **Visibility:** metadata-only v1 (default), with 72 h dual-guardian review mode after counsel.
4. **Incoming audio:** auto-play when allowed (default) or tap-to-hear always.
5. **Voice messages** for unavailable contacts in Stage 2: yes or no.
6. **SOS promise:** alert-and-call-parent only, never marketed as emergency calling (default).
7. **Wi-Fi-only devices:** allowed or excluded, given no emergency calling there.
8. **T&S headcount** before the first cross-family link (report 13).
9. **Limits:** 30 s per transmission and 60 per hour per edge (default).

## 7. Load-bearing claims

| # | Claim | Source | Basis |
|---|---|---|---|
| 1 | Background audio needs a visible activity or non-short FGS; target-37 needs WIU; privileged audio permissions are exempt in the Java path | https://developer.android.com/about/versions/17/changes/bg-audio ; GrapheneOS/platform_frameworks_base@17:services/core/java/com/android/server/audio/HardeningEnforcer.java | PRIMARY |
| 2 | A `microphone` FGS cannot start from the background | https://developer.android.com/develop/background-work/services/fgs/service-types | PRIMARY |
| 3 | Doze limits alarms to one per 9 minutes; an exemption keeps network and partial wake locks | https://developer.android.com/training/monitoring-device-state/doze-standby | PRIMARY |
| 4 | Nearby Connections is GMS-only; microG implements only Exposure Notification | google/nearby@main:internal/platform/implementation; microg/GmsCore@master:play-services-nearby/core | PRIMARY |
| 5 | Wi-Fi Aware needs `FEATURE_WIFI_AWARE` and `NEARBY_WIFI_DEVICES`, with a PSK data path | https://developer.android.com/develop/connectivity/wifi/wifi-aware | PRIMARY |
| 6 | Android 17 `KeyEvent` has no PTT keycode | GrapheneOS/platform_frameworks_base@17:core/java/android/view/KeyEvent.java | PRIMARY |
| 7 | Opus encode on Android 10+; 16 to 20 kbps suits wideband speech; LiveKit Android defaults to 48 kbps with RED and DTX | https://developer.android.com/media/platform/supported-formats ; webrtc-sdk/webrtc@m144_release audio_encoder_opus.cc ; livekit/client-sdk-android@main LocalParticipant.kt | PRIMARY |
| 8 | Telecom disconnects self-managed calls for an emergency call | GrapheneOS/platform_packages_services_Telecomm@17 CallsManager.java | PRIMARY |
| 9 | Voice classifier: 63.9% precision, 58.2% recall (English, 1% FPR); faster-whisper about 15x realtime | Roblox/voice-safety-classifier README; SYSTRAN/faster-whisper README | PRIMARY |
| 10 | LiveKit Cloud prices (Ship $50/150k/$0.0005; Scale $500/1.5M/$0.0004) | `docs/research/13-kid-messenger-and-video-calling.md` F5 (aggregators; livekit.com blocked) | SECONDARY |
| 11 | COPPA, 2258A, recording-consent and FCC interconnected-VoIP rules | `docs/research/13-kid-messenger-and-video-calling.md` F10; `docs/research/12-telephony-calls-sms-allowlists.md` 2.8; no primary text fetched | MEMORY |
