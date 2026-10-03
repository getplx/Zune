# Messenger, voice and video calls, walkie-talkie

## Purpose and scope

Specifies internet-only, WhatsApp-style communication (D19): 1:1 Messenger (text and emoji), 1:1 voice and video calls, and walkie-talkie, only between parent-approved contacts. Includes the Comms Service, moderation, Android 17 process rules, battery plan and trust-and-safety (T&S) operations with POCSO duties.

**Stage 1** = every MUST, done before the staff pilot unless a gate says otherwise. **Stage 2** = kid-initiated friend requests (still dual approval), parent-side calling (D8), mid-call video upgrade, voice-note review, nearby walkie, blocking classifiers, several devices per child, E2EE tier.

Not covered (in `docs/build/`): channel envelope, keepalive, identity, portal pages, KMS (`05-backend-and-parent-portal.md`); Guardian, policy, Emergency, SOS (`03-lockdown-and-guardian.md`); screens (`09-core-apps-and-design-system.md`); assistant moderation, crisis cards (`07-ai-assistant.md`); consent text, DPDP, contracts (`11-compliance-and-privacy-engineering.md`); kill-switch levels (`10-delivery-operations-and-pilot.md`); `INTERNET` list, 16 KB (`02-os-image-and-product.md`); test runs (`12-testing-qa-and-acceptance.md`).

`[default]` = value chosen here: configurable, unvalidated. Evidence is mostly GrapheneOS mirrors and secondary sources, not Google's tree [HANDOFF §2]; see VC-n.

## Decisions applied and reconciliations

| Decision or report | Effect |
|---|---|
| D19, D7, D8, D10, D28 | Internet only, 1:1, approved contacts; no PSTN bridge, groups or discovery. R13's PSTN edges and R08's SOS/911 flow dropped (SOS: 03 LOCK-35). |
| D23 | Bands 7-9, 10-12, 13-14 replace R13's 5-9/10-13 and R19's "excerpts at 13+". |
| D27 | Each guardian reads the full 1:1 thread in every band; child told; 12-month vault replaces R13's 180 days/13 months; calls and walkie unrecorded, metadata only. |
| D18, R19 | COPPA, NCMEC, TAKE IT DOWN, AB 1043, card consent, US hosting become DPDP s.9, Rule 10, POCSO ss.19-21, IT Rules clocks, ap-south-1. |
| D24, R05 §4.8 | `ZuneComms` dropped; ZuneGuardian owns the socket; apps use `IZuneLink` (03). N devices per child in schema; Stage 1 pairs one. |
| Media-in-visible-app convention vs R08 | R08's privileged background playback service becomes Guardian launching the Walkie or Calls activity. R13's self-managed Telecom call kept. |
| D18, D29, D20 | R13's LiveKit Cloud US and USD costs dropped: self-host in ap-south-1. No vendor moderation sees kid text unless LEG-7 closes. Charset Latin; rules English plus romanised Hinglish. |
| R13 SMS invite, quiet-hours check-ins, decision 9 | Dropped (SMS pumping; delayed guardian commands); "data plan required" becomes "Wi-Fi or mobile data". |

## Requirements

**Contact graph**
- **COM-01 MUST** Principals are guardian and kid with opaque UUIDs. Nothing resolves a name, number, username or e-mail to a principal; no search, suggestions or address-book upload.
- **COM-02 MUST** Cross-family edges form only from a parent-issued code: 10 characters, 32-symbol alphabet, single use, 48 h expiry, stored as HMAC; at most 3 open per kid and 10 per guardian per day; Rule-10-verified guardians only (05, 11). Invalid codes return identical responses; 5 failures per hour lock redemption for 1 h.
- **COM-03 MUST** An edge is `active` only after both guardians' consent-ledger entries (text version, time, kid, channels): A at code creation, B at redemption after seeing A's verified name and A's kid's display name. Text: both families read the conversation and see call metadata.
- **COM-04 MUST** Each guardian grants `msg`, `voice`, `video`, `ptt` for their kid (default `msg` only). `Allowed()` (§4.2) decides; the device re-checks via `PolicyClient` (03 LOCK-13) and fails closed.
- **COM-05 MUST** Revoke or block by either guardian acts within 3 s online: live call or PTT ended, thread removed from both devices (`contacts.rev`), sends refused `edge`, the other side sees "chat not available"; re-adding needs a new code.

**Messenger**
- **COM-06 MUST** Text and emoji only, at most 500 code points after NFC; no attachments, links, stickers, GIFs, voice notes, groups, typing indicators, read receipts or presence. Allowed: Basic Latin, Latin-1, Latin Extended-A, common punctuation, 5 newlines, and the pair's lower-band emoji.
- **COM-07 MUST** States: sending, sent (server accepted), delivered (persisted on the recipient device), failed. Idempotent on `(conv, cid)`; per-conversation `seq`; device outbox 50 messages for 24 h; cursor replay; a closed recipient schedule holds the message.
- **COM-08 MUST** Emoji allowlists come from `emoji_gen.py` over Unicode `emoji-test.txt`: nested per band, T&S-reviewed, denylist (sexual, weapons, drugs, alcohol, tobacco, rude gestures), no free ZWJ sequences, RGI flags only, keycaps mapped to digits; bundle the pinned Noto Color Emoji.
- **COM-09 MUST** `app.zune.messenger` has no `INTERNET`, receives via Guardian (§4.7), shows only the contact name in notifications, uses `FLAG_SECURE`, disables keyboard suggestions. Local store: 500 messages and 90 days per conversation [default].

**Moderation and visibility**
- **COM-10 MUST** Send-path hard blocks (p99 under 20 ms [default]; kid-friendly notice; attempt visible to the sender's guardian): URLs including spaced or spelled domains, phone numbers (digits, words, keycaps), e-mails, addresses, `@handles`, contact-exchange phrases, severe profanity and slurs per band. The renderer is plain text, never linkified, with no `ACTION_VIEW` (03 LOCK-29).
- **COM-11 MUST** Soft rules assign S1-S4 (§4.4): S1, S2 deliver and flag; S3 sexual or threat items are held for T&S; S2 and above notify guardians within 60 s.
- **COM-12 MUST** The async classifier is self-hosted in ap-south-1 and flag-only; vendor classifiers stay off for kid text until LEG-7 covers them (D29); no content is used for training or analytics.
- **COM-13 MUST** Both guardians, and nobody else, see in the portal the full thread, flags, held, blocked and suppressed items, and call and walkie logs (who, when, duration, outcome); every read is logged. Guardians can dismiss, mark safe, block or report to T&S.
- **COM-14 MUST** Child notice: full-screen first run, again per new contact, and a persistent "Parents can see this chat" header; calls and walkie say parents see who and when. Button "Got it", not "I agree" [R19 §4.1].
- **COM-15 MUST** One copy per family under that family's KMS data key; 12-month retention; one family's erasure removes only its copy; legal hold blocks deletion.

**Calls**
- **COM-16 MUST** Voice and video share one stack: LiveKit room `call_<ulid>`, `max_participants=2`; voice tokens carry the microphone source only; a callee may accept video as audio-only.
- **COM-17 MUST** Self-host LiveKit (Apache-2.0 SFU) in ap-south-1, DR ap-south-2: two nodes on EC2 with host networking behind an NLB (not Fargate: it needs a UDP port range, 05 §4.1), TURN/TLS; no egress, ingress, hidden participant or recording; AWS is the only processor (DPA: 11); Cloud only after VC-5 and a signed DPA. The portal shows metadata and can end calls.
- **COM-18 MUST** Tokens: TTL 120 s, identity kid UUID, `canPublishData=false`, `canUpdateOwnMetadata=false`, `canPublishSources` within {microphone, camera}, `hidden=false`, `recorder=false`, no admin, create, list or record grant; server `auto_create=false`.
- **COM-19 MUST** The callee token is minted only after `call.accept`; ring timeout 45 s; no invite to a busy kid; at most 10 invites per hour per edge.
- **COM-20 MUST** Server timers call `RemoveParticipant` or `DeleteRoom` at either family's schedule boundary, on revoke, block, suspension, kill, portal "End call" and at `call.max_min` (30 [default]); the device ends locally too.
- **COM-21 MUST** Video at most 360p and 24 fps, VP8 default; no simulcast, screen share or virtual-background module; hardware H.264 only after CT-08. Camera mutes after 5 s out of view; `FLAG_SECURE` on call windows.
- **COM-22 MUST** `app.zune.calls` registers a self-managed Telecom call (`MANAGE_OWN_CALLS`) and starts a `phoneCall` foreground service (FGS) from the visible activity; Bluetooth headsets route (D31); a 112 call from Guardian ends Zune calls within 2 s.

**Walkie-talkie**
- **COM-23 MUST** Opus frames travel as binary frames on the Guardian channel to a Go relay (§4.6); cloud-only in Stage 1. Plan B is LiveKit audio-only behind a `PttTransport` interface, triggered by CT-12.
- **COM-24 MUST** Half-duplex per edge, server floor control; 30 s per transmission; 60 per rolling hour per edge (both directions); 300 ms gap; replies `ok`, `busy`, `unavailable` never reveal a block. Audio is never stored; metadata only is logged.
- **COM-25 MUST** Capture and playback only in the visible Walkie activity; frames reach Guardian by Binder; `app.zune.walkie` has no `INTERNET`; tiles offer "mute contact".
- **COM-26 MUST** Auto-play only if the screen is on and unlocked, no call is active, and schedule, DND, volume cap and `walkie.auto_open` allow; Guardian launches the Walkie activity. Else chime and notification, no audio.

**Device**
- **COM-27 MUST** One socket, in Guardian; only `app.zune.calls` opens its own (to the SFU). Comms apps target SDK 37 and pass CT-13 with audio hardening on. Run §4.8 before the staff pilot (`zune/docs/lab/comms-battery.md`); keepalives go to 05.
- **COM-28 MUST** No GMS, Firebase, ML Kit or analytics (CI scan); `libopus` 16 KB-clean (02 OS-33); Guardian pre-grants `RECORD_AUDIO` (Walkie, Calls), `CAMERA` (Calls), `POST_NOTIFICATIONS` (Messenger); the other apps' grants (Assistant and Recorder `RECORD_AUDIO`, Photos `CAMERA`) are in 09 APP-16, and no grant is ever shown to the child.

**Trust and safety operations**
- **COM-29 MUST** Before any cross-family link: named T&S lead, 2 or more trained 24x7 responders, resident grievance officer, drilled incident plan.
- **COM-30 MUST** `comms.cross_family_external=false` by default: only staff-cohort families may link until two approvers set it true citing LEG-6 and EXT-3 in `gates.md`; refusal `gate`.
- **COM-31 MUST** Abuse reporting: kid "Block" (hides at once, alerts guardians), "Tell a grown-up" (alerts guardians) and "Report" (also sends the last 20 messages to T&S); portal "Report to Zune"; `safety@` mailbox.
- **COM-32 MUST** Legal hold freezes both families' copies and call logs, stops sweeps, exports JSON with a signed SHA-256 manifest on two-person approval.
- **COM-33 MUST** POCSO runbook with a reporting officer, a deputy and counsel on call [R19 §4.1]: reports to the SJPU (Special Juvenile Police Unit), local police or cyber-crime portal [R19 §2.4], logs receipts, never auto-reports a child sender.
- **COM-34 MUST** The T&S console is a separate SSO and MFA app: default view is flagged excerpts plus 20 messages; a full-thread read needs a case and second approver; views are logged and shown to guardians.
- **COM-35 MUST** S4 guardian notification is a T&S decision within 1 h (a guardian may be the risk). Account actions (warn, pause edge, suspend kid or family, reinstate) need a reason and audit; family suspension needs the T&S lead.
- **COM-36 MUST** Per-channel and per-family kill switches reach devices within 10 s (policy `kill`, 03 LOCK-09).
- **COM-37 SHOULD** Siblings in one family link with one approval, no code.

## Design and build instructions

### 4.1 Components and paths

```
zune/backend/comms/  cmd/comms-api  internal/{graph,invite,msg,moderation,call,ptt,flags,ts,vault}  deploy/livekit/
zune/apps/{messenger,calls,walkie}  zune/libs/{net,audio-opus}  zune/libs/core/emoji/ (allowlists, emoji_gen.py, rules/*.yml)
zune/portal/src/comms/  zune/portal/ts/ (T&S console)
```
Decision: a custom Go service over Guardian's channel, not Matrix or XMPP, because authorization is a parent-approved graph, not room membership [R13 §3.1]. Zune Gateway routes `msg.*`, `call.*`, `ptt.*` and binary audio to Comms Service; the envelope and RPC are 05's, and if it differs the payloads below still apply. Postgres (Multi-AZ, DR replica ap-south-2) is the source of truth; `internal/msg` sits behind a `MessageStore` interface so the XMPP fallback swaps one package.

### 4.2 Contact graph

```sql
-- contact_edge is 05 §4.4's table (columns child_a < child_b, state proposed|active|revoked|blocked, grants_a|b, sched_a|b, consent_a|b); family ids and the effective band (the lower of the two) are derived at read time
message(id, conv, seq, cid, st, sev, UNIQUE(conv,cid))  message_copy(message_id, family_id, body_ct, enc_key_id)  device_event(device_id, cursor, type, ref)
```
Other tables: invite, conversation, call, ptt_log, flag, ts_case, audit. The signed policy's `contacts.entries[]` carries `{cid, name, av, ch: [msg|voice|video|ptt], win}` (03 extends the schema). `Allowed(edge, channel, now)` returns the first failing code: `edge` (not active), `grant` (either side), `kill`, `suspended`, `schedule` (sender's window closed), recipient window closed (`defer` for `msg`, refusal for calls and PTT), `gate` (COM-30).

Invite: guardian A picks a kid, consents, gets a code, link and QR, and shares them out of band. Guardian B enters it, sees A's verified name and A's kid's display name, picks a kid, ticks "I know this family", consents and sets grants. One transaction writes the edge `active` and bumps `contacts.rev` for both kids; Policy Service pushes the signed bundle. Display names are guardian-chosen (20 characters, hard-block rules apply); no SMS.

### 4.3 Messenger protocol

Frames (D = device, S = server):
- `msg.send` D `{cid, conv, body}`; `msg.ack` S `{cid, id, seq, st: accepted|blocked, code}`, codes `url phone email address handle profanity chars emoji length edge rate schedule`; `msg.new` S `{id, conv, seq, from, body, ts}`; `msg.delivered` D `{id}`; `msg.state` S `{id, st}`.
- `call.invite` D `{kind, to}`; `call.accept|decline|cancel|end` D `{call}`; `call.ringing`, `call.token` S `{call, url, token}`; `call.incoming` S `{call, from, kind}`; `call.ended` S `{call, reason}`.
- `ptt.begin` D `{cid, edge}`; `ptt.ack` S `{stream, ok|busy|unavailable}`; `ptt.incoming` S `{stream, from, play: auto|chime}`; `ptt.end`, `ptt.abort`.

```
1 authN device -> kid; Allowed(msg) else ack blocked(code); rate limits
2 n = normalise(body): NFC; NFKC copy; strip zero-width and bidi; de-leet; keycap->digit; fold homoglyphs
3 charset, length, emoji(band_eff) else blocked; hard rules(n) else blocked + log attempt
4 sev = soft(n, last 10 msgs); S3 sexual or threat => st=held, queue T&S
5 one tx: message + 2 family copies + device_event rows; ack accepted
6 async classifier -> flag; deliver msg.new unless held or suppressed
```
A message to a kid who blocked the sender is stored `suppressed` (sender sees "sent") and shown to the blocker's guardian. Delivered means Guardian's inbox-provider insert returned OK.

Per band 7-9 / 10-12 / 13-14 [default]: edge cap 10 / 20 / 25; messages per minute 10 / 20 / 20, 1,000 per day per kid; profanity any blocked / strong blocked, mild S1 / slurs and severe blocked, mild S1; romance cues S2 / S2 / S1; emoji sets widen by band (COM-08). The band comes from signed policy `band` (03).

### 4.4 Moderation and severity

Rules live in `rules/*.yml` with a labelled corpus; the T&S lead sources the English and romanised-Hinglish lexicons (none is supplied here). Evaluate classifiers on a synthetic, expert-reviewed set (PRE-07); if none passes, ship rules plus human review.

| Sev | Examples | Pipeline | Guardian | T&S [default] |
|---|---|---|---|---|
| S1 | mild insult | deliver | digest | none |
| S2 | bullying, "don't tell your parents", age or location probe, meet-up ask | deliver, flag | under 60 s | review 24 h |
| S3 | sexual solicitation, "send a pic", threats, self-harm cue | sexual or threat: hold; self-harm: deliver plus crisis card (07) | under 60 s | ack 15 min 24x7, decide 4 h |
| S4 | suspected child sexual exploitation, imminent harm | hold, legal hold | T&S decides, 1 h | ack 15 min, counsel 2 h |

### 4.5 Calls

```yaml
# confirm key names at the pinned release (VC-4)
rtc:  {tcp_port: 7881, port_range_start: 50000, port_range_end: 50999, use_external_ip: true}
turn: {enabled: true, tls_port: 5349, udp_port: 3478}
room: {auto_create: false, max_participants: 2, empty_timeout: 20}
```
Keys: Secrets Manager (PRE-08). Pin the newest stable server and Android SDK at Z5 start (`verified-facts.md`). A signed webhook fills the call log.

Sequence: `call.invite` -> `Allowed(voice or video)` -> create room, mint caller token -> `call.ringing` to caller, `call.incoming` to callee -> Guardian launches `app.zune.calls/.IncomingCallActivity` (show-when-locked, turn-screen-on) -> `call.accept` -> callee token -> both join. Audio: Opus 24 kbps speech preset, DTX on, RED off [R08 F7]. Voice reuses the video stack (design confirmed): one SDK, minter and enforcement path outweigh the SFU hop. Persist deadlines across restarts.

### 4.6 Walkie relay

Binary header, 12 bytes, big-endian: `0x5A41 | ver u8=1 | kind u8=1 | stream u32 | seq u16 | ts_ms u16`, then one packet of three 20 ms Opus frames (VOIP, wideband, 16 kbps, in-band FEC, DTX off) [R08 §4]. Hold button -> Walkie encodes, hands frames to Guardian (`IZuneLink`) -> `ptt.begin` plus frames at once -> server checks `Allowed(ptt)`, floor, limits, DND -> `ptt.ack`, `ptt.incoming` to the peer, buffering up to 2 s [default] in RAM until the peer's Walkie attaches -> 120-200 ms jitter buffer. The server aborts at 30 s and on schedule, revoke or kill. Plan B trigger: over 3% of 500+ transmissions glitch (underrun above 200 ms) or p95 mouth-to-ear above 900 ms [default].

### 4.7 Android 17 process map

| Function | Process | Why |
|---|---|---|
| Socket, keepalive, policy, routing, waking apps | ZuneGuardian (persistent, platform-signed) | one channel [R05 §4.5] |
| Inbox, notifications, store | `app.zune.messenger`, cold-started via a signature-protected inbox `ContentProvider` | no `INTERNET` |
| Camera, microphone, WebRTC | `app.zune.calls`: visible activity, then `phoneCall` FGS started while visible | camera and mic FGS cannot start from the background [R08 F2] |
| PTT capture, playback | `app.zune.walkie` visible activity | background audio needs a visible activity or while-in-use FGS [R08 F1] |

Guardian needs `START_ACTIVITIES_FROM_BACKGROUND` (03). 03 LOCK-29 lets only the incoming-call activity show over the keyguard (Accept and Decline only); Walkie never shows over it (COM-26: screen on and unlocked, else a chime).

### 4.8 Battery, keepalive and quality measurement

One Pixel 10a and one 9a on `userdebug`. Matrix: network {home Wi-Fi, Wi-Fi with short NAT timeout, 4G on Jio, Airtel, Vi if a data nano-SIM exists [R20]} x keepalive {60, 120, 180, 240 s, adaptive} x traffic {idle, 1 message per minute, 1 PTT per 10 min}; unplugged, screen off, 8 h, Doze IDLE confirmed. Record battery per 24 h (`batterystats`), MB per day, drops per hour, reconnect and delivery latency. Pass [default]: incremental drain at most 3% per 24 h on Wi-Fi, 5% mobile; latency p95 at most 5 s Wi-Fi, 10 s mobile in deep Doze; at most 1 drop per hour; reconnect p95 at most 10 s. Adaptive probe per network type [R13 F3: short pings drain battery]: start at the server's `hb_s` (05 BE-07 default 180 s), step down 30 s per drop to a 60 s floor, up 30 s after 6 h stable to a 240 s ceiling; the matrix result may change 05's default through an ADR.

### 4.9 Trust and safety operations

- **Runbook:** detect (rule, classifier, report) -> triage within SLA -> legal hold -> counsel for S4 -> designated officer reports to the SJPU, local police or cyber-crime portal -> log receipt -> support. A child who sends sexual text is a victim first; counsel decides any report [R19 §2.4].
- **Clocks** [R19 §2.4, secondary]: 3 h takedown on orders; 2 h for intimate-image and CSAM complaints; POCSO ss.19-21, with personal liability for the person in charge (s.21(2)). Breach clocks: 11.
- **Escalation:** responder, T&S lead, founder and counsel; each step logged in `ts_case`. Sweeps skip `hold`; counsel may narrow 12 months (D27).

## Acceptance criteria and tests

`CT-nn`; 12 runs them.

- **CT-01** Two synthetic families: edge `active` only after both consents; both guardians read the thread, a third family cannot; the kid sees all notices; a staff read shows in the access log.
- **CT-02** Invalid codes give identical bodies within 20 ms; the sixth wrong try in an hour is locked out; an OpenAPI scan finds no endpoint resolving a principal outside an active edge.
- **CT-03** Airplane-mode cycles, duplicate `cid`, 2 h offline with 50 messages: one copy each, in order; 500 code points pass, 501 fail.
- **CT-04** Hard-block corpus: all 200 positives blocked, at most 1% of 1,000 benign kid sentences [default]; a stored URL is untappable (LT-09). Allowlists nest, exclude the denylist, render in the bundled font; the lower band applies.
- **CT-05** Seeded S1-S4 corpus: S3 items held and queued; portal flag within 10 s p95, classifier flag within 30 s p95, guardians told within 60 s.
- **CT-06** A message to a closed-window kid arrives at the boundary; calls and PTT are refused; an open call ends within 5 s.
- **CT-07** Revoke: live call ends within 3 s, thread leaves both devices within 10 s, a send returns `edge`. Block: sender sees "sent" only; message `suppressed`.
- **CT-08** Voice call to a locked, screen-off Pixel connects within 5 s p95 on Wi-Fi; audio-only accept works; video camera mutes 5 s after leaving the foreground; codec bench on both models (CPU, heat, battery, VP8 vs H.264).
- **CT-09** Token decode shows every COM-18 grant; a data publish, expired token, third identity and room-create all fail.
- **CT-10** Portal "End call" ends both sides within 3 s; IaC has no egress or ingress; no `recorder` token; dialing 112 mid-call ends the Zune call within 2 s.
- **CT-11** With `comms.cross_family_external=false` a staff-to-external edge is refused `gate`; a 12-month-old message is swept unless held; family erasure crypto-shreds only its copies.
- **CT-12** PTT: abort at 30 s plus or minus 0.5 s; transmission 61 in an hour `unavailable`; simultaneous press `busy`; no audio in storage or logs; 500-transmission statistics decide Plan B.
- **CT-13** With hardening on: foreground Walkie plays; screen on and unlocked with Walkie backgrounded launches and plays; screen off chimes only; nothing drops silently.
- **CT-14** §4.8 matrix complete; a per-channel kill switch disables a feature within 10 s.
- **CT-15** T&S tabletop with a simulated S4 meets the SLAs; the evidence export hash verifies.

## Verify first

| ID | Claim | Why uncertain | How to verify | If false |
|---|---|---|---|---|
| VC-1 | Audio hardening lets a visible activity play and capture, suppresses boot-started service audio, enforces native playback [R08 F1; R13 F3] | Java path only, GrapheneOS | Read `HardeningEnforcer`, audioserver; `cmd audio set-enable-hardening enable` on both Pixels | Give Walkie `MODIFY_AUDIO_SETTINGS_PRIVILEGED` (R08's design) |
| VC-2 | Guardian can start a Tier B activity from the background (show-when-locked, turn-screen-on) and cold-start a provider [R13 F3] | Activity-start rules unread | Read `BackgroundActivityStartController`; locked-screen test | Full-screen-intent notification; Walkie chime only |
| VC-3 | Camera and mic FGS cannot start from the background; a `phoneCall` FGS started while visible survives Home; Telecom ends self-managed calls on emergency calls [R08 F2, F9] | Docs only; Telecom read in GrapheneOS | Home mid-call; read the tag; CT-10 | Mute on stop; Guardian ends calls on call-state change |
| VC-4 | LiveKit grants, `auto_create`, `max_participants`, TURN keys, RoomService exist as used; the Android SDK has no GMS [R13 F4, F5; R08 F8] | Vendor docs blocked | Read config, `auth/grants.go` at the pinned release; `gradle dependencies` | Adapt config; fork or reject the SDK |
| VC-5 | Self-hosted LiveKit on EC2 host networking behind an NLB works from Indian carriers and ISPs (UDP range, TURN/TLS 443; TURN share unknown); Cloud option: India pinning, DPA [R13 F5, F6] | Unmeasured; aggregators only | `tc netem` loss runs; Jio, Airtel, Vi, 3 ISPs; vendor answer in writing | More TURN capacity; self-host only |
| VC-6 | Socket meets §4.8 thresholds; own Opus relay gives 300-480 ms and few glitches [R13 F3; R08 §4] | Unmeasured | CT-14, CT-12 | Longer keepalive, Wi-Fi-only live features, Plan B |
| VC-7 | `libopus` BSD-3 and 16 KB build; hardware encoders on `stallion`, `tegu` work [R13 F4] | Memory; Tensor claim unverified | Read licence; `check_elf_alignment.sh`; CT-08 | `MediaCodec` Opus (API 29 [R08 F7]); software VP8 |
| VC-8 | Android 17 lacks Emoji 17 glyphs; AOSP `LatinIME` has no GIF, sticker, cloud suggestion [R13 F7] | Secondary, memory | Render test; inspect `LatinIME` | Restrict to renderable emoji; IME patch |
| VC-9 | POCSO ss.19-21, Rule 11, takedown clocks, who must report [R19 §2.4] | Secondary; Indian hosts blocked | Counsel reads originals | Update runbook and SLAs |

## Risks, open gates and out of scope

Risks:
1. **Classification.** An IT Rules under-18 change or Karnataka's under-16 announcement could capture the messenger as a social media intermediary [R19, R20]. Stay closed and family-managed: no discovery, handles, feeds or groups.
2. **Moderation gaps.** Rules miss coded grooming; live voice, video and PTT are unmoderated. Do not market detection.
3. **Vault and disclosure.** Server-readable children's chats are a high-value target (05, 11); a guardian reading another family's child rests on dual consent and counsel (s.9(3), interception law).
4. **Hostile guardian.** The main threat; in v1 every guardian is verified at the company flash visit (D16, Rule 10).
5. **Unmeasured:** relay stutter, battery, SFU operations. If CT-01 to CT-07 are not green by Z5 week 8 [default], record an ADR to swap `MessageStore` for Prosody.

Gates:
- **[GATE: before build]** VC-1 and VC-2 recorded in `verified-facts.md` before building the Walkie and Calls wake paths; if either fails, redesign with 03.
- **[GATE: before staff pilot]** SP-3 drill, named T&S lead, CT-12 and CT-14 results with the Plan B decision, kill switches (SP-5), vendor register (SP-1) covering AWS and the classifier.
- **[GATE: before external family]** LEG-1, LEG-6, EXT-3, EXT-7; then set `comms.cross_family_external=true`.
- **[GATE: before charging]** 8 weeks of external operation within T&S SLAs [default].

Out of scope: guardian-side calling and messaging (D8), groups, media messages, discovery, PSTN bridge, recording, E2EE, other languages, other devices, SOS (03).
