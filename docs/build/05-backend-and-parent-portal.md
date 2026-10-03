# Backend services, data model, device channel and the browser-based parent portal

## Purpose and scope

This section specifies the cloud side: service boundaries, stack and AWS India topology, the one device channel owned by ZuneGuardian, enrolment with Rule-10 verification, authentication, the data model, the 12-month retention vault, tamper-evident audit, the Stage-1 Zune Portal and the staff console.

**Stage 1** = every MUST, working end to end at Z4 exit (`01-prerequisites-and-phases.md`); message and AI review pages complete at Z5 when 06 and 07 land. **Stage 2** = Caregiver role, DigiLocker as default path, parent-side calling (D8), parent-key E2EE, billing, multi-device UI.

Not covered here:
- Guardian internals, enforcement, PIN, bypass tests: `03-lockdown-and-guardian.md`. Keys, OTA client, rings: `04-device-signing-ota-release.md`.
- Messenger and call rules, moderation, media, T&S operations: `06-communication.md`. Assistant behaviour: `07-ai-assistant.md`. Catalog, Tier 2, weather providers: `08-content-videos-weather-reader.md`.
- ZuneSetup screens, on-device crash reporting: `09-core-apps-and-design-system.md`. Station, intake, kill-level semantics, support: `10-delivery-operations-and-pilot.md`.
- Legal analysis, runbooks: `11-compliance-and-privacy-engineering.md`. Test execution: `12-testing-qa-and-acceptance.md`. AWS accounts, SCP: `01`.

`<zone>` is the neutral domain fixed in the Z0 ADR (name clearance pending, A5). 

## Decisions applied and reconciliations

**Reconciliations applied**

| Decision or report | Effect |
|---|---|
| D22, D24, R05 §4.5, R13 §6 | Guardian owns the single socket; `ZunePolicyService` becomes Policy Service plus Guardian; `ZuneComms` dropped; Comms Service only relays signalling. |
| D18, A11, R05 §4.6, R10 | us-east-2 and R2/B2 become ap-south-1 plus ap-south-2 DR, S3 plus CloudFront for OTA; Indian NTP. |
| D19, D28, R05 §4.4, R13 | No SMS vault, SMS SOS fallback, E.164 contacts or invite SMS; contacts are child-to-child edges. |
| D23, R19 §3 | Bands 7-9, 10-12, 13-14 (R05: 6-8); R19's excerpts-only visibility at 13+ rejected: D27 gives full parent read access. |
| D27, R19 Rule 8(3) | One retention policy per class (§4.6) replaces R05's 90 d and 30 d and R13's 180 d; erasure seals. |
| D31, R19 §4.1 | Location = parent-set places (opt-in) plus SOS fix; R19's "SOS only" yields. |
| R13 §3.2, §4.1 | Server-readable messages stay, one vault copy per family; E2EE stays Stage 2. |
| R19 (card is not Rule 10) | No card step; verification is staff-inspected ID or DigiLocker token. |
| D29 | AI Gateway provider interface (OpenAI default, Anthropic fallback). |
| 03 §4.4 | `policy-v1` stays canonical in 03; server types generated; additions in §4.5. |
| R05 §4.8, R10 | N devices per child in schema, one in the UI; Caregiver deferred; no FRP Activation Lock here. |
| 04 REL-14 | Seat = serial HMAC plus device certificate; attestation alone never grants one. |

## Requirements

**Platform and residency**
- **BE-01 MUST** Go services in `zune/backend/<svc>` (one module), PostgreSQL (`pgx`, `sqlc`), Redis for routing and rate limits only, S3, KMS, Terraform (`backend/infra`); portal in React and TypeScript at `zune/portal`.
- **BE-02 MUST** Each §4.1 deployable has its own IAM role, DB role and security group.
- **BE-03 MUST** Stores, compute, logs and backups stay in ap-south-1 or ap-south-2; no third-party script, analytics or advertising SDK in portal or backend.
- **BE-04 MUST** Default-deny egress: only `ai-gateway`, `weather`, `content` and the notification adapter reach the internet, via the allowlist proxy in `backend/infra/egress.yaml`; others use VPC endpoints.

**Device channel**
- **BE-05 MUST** One endpoint `wss://device.<zone>/v1/channel`: TLS 1.3, mutual TLS with a device certificate, subprotocol `zune.channel.v1`; devices not `claimed` are refused; a second connection supersedes the first.
- **BE-06 MUST** `policy.update`, `command`, `approval.grant`, `time.sync` persist in `device_outbox`, replay after the device `cursor`, and are idempotent by frame `id`.
- **BE-07 MUST** `heartbeat` (echoed) defaults to 180 s (`ready.hb_s`, range 60-600), idle timeout 2.5 times that, client backoff 1 s doubling to 5 min with jitter.
- **BE-08 MUST** For a connected device, portal-save-to-ack p95 is at most 10 s (p99 30 s); `lock` p95 at most 5 s.
- **BE-09 MUST** Frames at most 64 KiB, validated against `zune/libs/core/schema/channel-v1.schema.json`, 20 per second per device; unknown types dropped and counted. `msg.*`, `call.*`, `ptt.*` route to `comms`, the rest to `policy`. The same certificate authenticates `/v1/device/*`.
- **BE-10 MUST** `ready` and `time.sync` carry a server-time JWS (BE-13 signer), pushed at least hourly (03 LOCK-11).

**Policy and commands**
- **BE-11 MUST** Resolve band template, child sections, device override; for safety keys (`caps`, `time.bedtime`, `sos`, `kill`, `net`) the most restrictive wins; validate against `policy-v1.schema.json`; `rev` rises atomically per device; edits within 500 ms coalesce.
- **BE-12 MUST** `not_after` = `iat` + 30 days, reissued daily; `epoch` rises only on re-claim; `rev` is never reused or lowered.
- **BE-13 MUST** Bundles and commands are ES256 JWS from KMS key `policy-signer`, chain in `x5c` to the offline root (03 LOCK-07); signer cert at most 90 days, renewed at day 60, alert at 21 days left; Go and Kotlin share test vectors.
- **BE-14 MUST** Commands (03 LOCK-10) carry `cmd_id`, `nonce`, `exp` (§4.5); expired ones are never sent; results stored.
- **BE-15 MUST** Kill state (`global|cohort|family|device`, level 0-4, semantics in 10) reaches affected bundles within 10 s; level 2 or higher and any global scope need two staff approvals.
- **BE-16 MUST** Child approval requests (`time|app|topic|video`) expire in 24 h, at most 5 open per kind; a grant is a signed `approval.grant` with TTL; decisions audited.
- **BE-17 MUST** Ingest `posture` (03 LOCK-06) and `ev.health` (04); flag drift when acked `rev` trails 5 min while connected or the posture hash changes.

**Enrolment and verification**
- **BE-18 MUST** Claim code: 8 characters from a 31-character alphabet, stored as HMAC, 10 min, single use, 5 attempts per code, 10 failures per IP per hour; QR payload `ZUNE1:<code>` only for pairing (03 LOCK-30; the station's `ZUNE1S:<token>` is a separate factory-QA payload, 10 §4.5).
- **BE-19 MUST** The station (role `station`) registers each flashed phone `unclaimed` with model, build, `serial_hmac`, attestation; a claim must match one through the attested serial (fallback V4).
- **BE-20 MUST** Claim codes go only to guardians with `verified_state=verified` (Rule 10: `staff_id` with inspector, document type, document-number HMAC, no ID image; or `digilocker`) after the §4.6 consents.
- **BE-21 MUST** The device certificate (P-256, 365 days, KMS `device-ca`) needs `attest` to pass the chain. Mismatch (unlocked, other key hash, SPL below `min_spl`) sets `integrity=fail`, turns cloud caps off, warns the parent; an unreachable verifier retries 72 h on station identity (04 REL-14).
- **BE-22 MUST** After a wipe, re-claim accepts only a code from a guardian of the bound family and the same serial; `epoch` increments; the portal shows "device was reset" within 60 s (03 LOCK-18).
- **BE-23 MUST** `unenroll` needs step-up. `service_unlock` needs step-up, staff co-approval and a `zune-service-ca` KMS signature (03 LOCK-20). Both notify every guardian.

**Authentication and roles**
- **BE-24 MUST** Passkeys (`go-webauthn`, discoverable, user verification required, attestation `none`); the RP ID is the neutral domain from the Z0 ADR and never changes.
- **BE-25 MUST** Server-side sessions, `__Host-` cookie, HttpOnly, Secure, SameSite=Lax, idle 2 h, absolute 12 h. Step-up (passkey assertion under 5 min old) is required to add or remove a guardian, release, service-unlock, PIN-reset, withdraw, erase, export, and to read vault content after 30 min without one.
- **BE-26 MUST** Email OTP (6 digits, hashed, 10 min, 5 attempts) only registers a passkey from an invite or starts recovery, which waits 48 h with notice to all guardians unless staff re-inspect the ID. SMS OTP only after DLT registration.
- **BE-27 MUST** Roles `owner`, `guardian`; `caregiver` in the enum without UI. At most 4 guardians; unverified guardians have no data powers; Stage 1 co-guardians need a staff-inspected ID; support may set a family `frozen`.
- **BE-28 MUST** Staff use SSO with hardware keys (IdP: AWS IAM Identity Center or an equivalent India-region IdP, chosen in the Z0 ADR, V11), roles `support|tns|verifier|station|release|sec|content|content_lead` (the last two per 08 CNT-22), no standing vault access; break-glass needs two approvers, lasts at most 4 h, is written to `staff_audit` and notified to the family unless counsel directs otherwise. Staff laptops are company-managed (disk encryption, screen lock, patching); offboarding revokes SSO, hardware keys, station access and break-glass eligibility within 1 h.

**Data, vault, audit**
- **BE-29 MUST** Row-level security on every table with `family_id`, set only from the session.
- **BE-30 MUST** Consent ledger (append-only, hash-chained) per purpose `account|visibility|ai|contact_pair|location|diagnostics|third_party_video` with notice version and language; a purpose without a `granted` row disables its feature server-side.
- **BE-31 MUST** Multi-Region KMS key; AES-256-GCM DEK per (family, child, month), AAD = family|child|class|item; DEK cached at most 5 min; only `vault` holds `kms:Decrypt`. One vault item per family per message; message text, AI text and images exist nowhere else (logs, caches, search, analytics).
- **BE-32 MUST** `retain_until` set at write per §4.6; a daily sweeper deletes expired non-held items, a monthly job destroys expired DEKs; overdue 48 h alerts.
- **BE-33 MUST** Parents read only through `vault`; each thread or session open writes a `vault.read` audit row every guardian sees; bundles carry `vis.notice_v` so the child is told (D27).
- **BE-34 MUST** Withdrawal and erasure follow §4.6; `erasure_mode` defaults to `seal`, `delete_now` destroys DEKs at once; legal holds block deletion and need the `tns` lead plus a second approver. Export (step-up) is the family's own data as JSON in a ZIP, presigned URL 7 days, ready within 24 h [INFERRED].
- **BE-35 MUST** Per-family audit hash chain (`SHA-256(prev || canonical entry)`), UPDATE and DELETE revoked; hourly KMS-signed Merkle root in an S3 Object Lock (compliance) bucket replicated to ap-south-2; daily verifier; failure is Sev-1.
- **BE-36 MUST** Logs via a field-allowlist logger (no bodies, names, free text, tokens), kept 12 months with 180 days searchable, in India; servers sync via `chrony` to Indian NTP (hostnames per V8, also 02's `config_ntpServers`); incidents carry 6 h (CERT-In) and 72 h (DPDP Rule 7) clocks.
- **BE-37 MUST** RDS backups at most 35 days with PITR plus cross-region replicas; the Z4 drill records RPO and RTO (targets 15 min, 4 h [INFERRED]); a restored row with a destroyed DEK is unreadable.

**Portal, notification, edge**
- **BE-38 MUST** Portal pages of §4.7 with OpenAPI at `backend/gateway/openapi.yaml`, `If-Match` concurrency, audited writes, 360 px mobile-first, keyboard operable.
- **BE-39 MUST** CSP `default-src 'self'`, `frame-ancestors 'none'`, Origin check plus CSRF token, WAF on the ALB; `gateway` serves the SPA (no CDN carries personal data).
- **BE-40 MUST** Web Push (VAPID) and email; SMS after DLT; payloads carry no child text or names. SOS cannot be disabled, reaches every guardian in 10 s p95 and pages `tns` if unacknowledged for 5 min [INFERRED].
- **BE-41 MUST** `dns`: DoT on 853 at `dns.<zone>` via an NLB TLS listener to Unbound; answers only `dns/allowlist.yaml` (service registry plus 08's Tier-2 hosts); logs counts and refused names, never allowed names per device.
- **BE-42 MUST** `connectivity.<zone>/generate_204` answers 204 on HTTP and HTTPS (D30).
- **BE-43 MUST** `admin` publishes OTA metadata (04 REL-16) signed by `channel` after two approvals; artifacts in S3 ap-south-1 replicated to ap-south-2 behind CloudFront `dl.<zone>`; payload URLs need a 6 h token from `policy` via Guardian (REL-20).
- **BE-44 MUST** `entitlement(plan='free_pilot')` and a billing stub; no payment data before PAY-1.
- **BE-45 MUST** Alerts: BE-08 latency, channel availability under 99.5% monthly [INFERRED], drift, device quiet 24 h, sweeper, audit verifier, signer expiry, certificate expiry (BE-48), KMS errors, budget.

**Operations: endpoints, secrets, domain, paging, migration**
- **BE-46 MUST** Every endpoint other sections call is declared in `backend/gateway/openapi.yaml` with owner, auth mode (session, mTLS, token-plus-attestation, station SSO), rate limit and body limit, and the gateway refuses an undeclared route. Cross-section routes owed here: `POST /v1/station/jobs` (issues the `factory_qa` token, 10 §4.5), `POST /v1/device/factory/qa` (authenticated by that token and the attested key, usable only before a claim), `POST /v1/device/shares` (09 §4.5, vault class `share`), `POST /v1/device/diag` (09 §4.8, 20 a day per device), `/v1/device/ai/*` (07 §4.2), `GET /v1/content/tier2/state` and content manifests (08), `/v1/weather/*` (08 §4.8), the Guardian-minted short-lived device token for Tier B REST calls (08 §4.10), and the portal routes `/children/{c}/home` and `/children/{c}/shared` (09).
- **BE-47 MUST** All secrets (vendor API keys, LiveKit keys, VAPID keys, database credentials, HMAC keys for claim codes, `serial_hmac`, `doc_hmac` and `safety_identifier`) live in Secrets Manager or KMS (01 PRE-08), are named in `backend/infra/secrets.yaml` with an owner and rotation period (90 days, or at once on staff departure or suspected leak) and are rotated in a drill before C0. HMAC keys are versioned (`kid` stored beside each value) so rotation re-computes in the background and verifies against old and new; `serial_hmac` and `doc_hmac` uniqueness constraints are rebuilt per `kid`, never dropped. No secret appears in Terraform state, container images, logs or the repository (CI secret scan, PRE-08).
- **BE-48 MUST** One registrar-locked domain `<zone>` (Z0 ADR; devices bake hostnames into overlays and ZuneUpdater, so a rename after devices ship is an OTA event). `backend/infra/hostnames.yaml` lists every hostname (`device.`, `dns.`, `connectivity.`, `player.`, `dl.`, `weather.`, the portal host, SFU and TURN hosts from 06, `status.`) with its certificate source (ACM for ALB, NLB and CloudFront, a public CA for the Unbound DoT and TURN/TLS endpoints where ACM cannot be exported), automatic renewal and an alert 21 days before expiry. CAA records, DNSSEC and HSTS on the portal; the device CA and its chain follow BE-21. Outbound e-mail (OTP, notices) uses the same domain from an India-region sender (SES ap-south-1 [INFERRED, V11]) with SPF, DKIM and an enforced DMARC policy; role mailboxes (security, privacy, grievance, legal, safety) are monitored.
- **BE-49 MUST** BE-45 alerts page a named engineering on-call (rota in `zune/docs/ops/oncall.md`; two people from Z6) through a paging service whose payloads carry no personal data; severities follow 11 §4.3; a Sev-1 or Sev-2 outage lasting over 30 minutes shows a portal banner and a notice e-mail to guardians; each alert has a runbook in `zune/docs/ops/runbooks/`.
- **BE-50 MUST** Versioning and migration: PostgreSQL schema changes are versioned SQL migrations (`golang-migrate` or equivalent, `sqlc` regenerated in CI), expand-then-contract across two releases, each rehearsed in staging on a restored copy of the latest snapshot with timing recorded; vault re-encryption and DEK rotation are background jobs, not migrations. The server keeps accepting a device client (channel `zune.channel.v1`, `/v1/device/*`, `policy-v1`) until no device on that build has reported in 30 days and the next ring has reached 100%; a breaking change ships as a new subprotocol or `/v2` beside the old one, and policy-schema changes are additive until Guardian understands both. The portal's OpenAPI changes are backward compatible within a release train.

## Design and build instructions

### 4.1 Topology and stack

`gateway` (Zune Gateway) runs as `gateway-web` (ALB: Portal SPA, REST, SSE, auth) and `gateway-device` (NLB passthrough: channel, device API), with packages `notify`, `ratelimit`. `policy` is the Policy Service. `vault` alone holds the vault KMS key and owns `zune-vault`. `comms`, `ai-gateway`, `content`, `weather` (06, 07, 08) write content only through `vault`. `admin`: staff console API, OTA publisher, billing stub, incidents. `attest`: Kotlin sidecar on Google's `android/keyattestation` [R05 F8]. `dns`: Unbound. `livekit` (06 COM-17) is the one component that does not run on Fargate: it needs host networking and a UDP port range, so it runs on two EC2 instances behind an NLB (UDP and TCP) with its own security group, IAM role and patching, and TURN/TLS on 443 or 5349 (06 VC-5).

Why: Go gives socket density and one codebase with Comms [R05 §4.6]; Postgres is the source of truth with row-level security; Redis only routes; S3 and KMS give residency, Object Lock, crypto-shredding.

ECS Fargate over two AZs; RDS PostgreSQL Multi-AZ `zune-main` (schemas core, graph, policy, ledger, ops) and `zune-vault`; ElastiCache; Secrets Manager; jobs are Postgres rows claimed with `FOR UPDATE SKIP LOCKED`. DR is pilot-light in ap-south-2: replicas, S3 replication, KMS replica key, Route 53 failover at 60 s TTL. CloudFront serves only non-personal OTA artifacts.

### 4.2 Device channel

Frame (JSON text): `{"v":1,"t":"<type>","id":"<uuidv7>","ts":<ms>,"seq":<n>,"b":{...}}`.

| Direction | Types (`b`) |
|---|---|
| D to S | `hello{cursor,boot_id,build,rev}`, `heartbeat{bat}`, `ack{id}`, `command.result{cmd_id,status,reason}`, `approval.request{kind,subject}`, `ev{kind:usage\|sos\|drift\|posture\|health\|presence}` |
| S to D | `ready{cursor,hb_s,rev_latest,time}`, `heartbeat`, `policy.update{rev,epoch,sha256}`, `command{jws}`, `approval.grant{jws}`, `time.sync{jws}` |
| Both | `msg.*`, `call.*`, `ptt.*` (bodies in 06; media never rides this socket) |

Sequence: connect with client certificate; `hello`; server sends `ready` and replays `device_outbox` after `cursor`; device acks. `policy.update` is a doorbell: the device fetches `GET /v1/device/policy?rev=N` (JWS, ETag = sha256). Redis holds `conn:{device_id}` and pub/sub `node:{id}` so any node reaches the socket; Redis loss only forces reconnects.

### 4.3 Enrolment

```
Portal   POST /v1/families/{f}/children/{c}/claim-codes          -> {code, expires_at}
Setup    scan ZUNE1:<code>; Guardian makes attested EC key K (StrongBox if present)
Guardian GET  /v1/device/enroll/challenge                         -> {challenge_id, challenge}
Guardian POST /v1/device/enroll/begin {code, csr(K), chain[], challenge_id}     (no client cert)
Server   claim_code by HMAC -> family, child; attest.verify(chain, challenge) -> {key_hash, locked, state, spl, serial}
         match serial_hmac to an unclaimed device; one tx: bind, issue cert, ledger + audit rows
         <- {device_id, leaf_cert, ca_chain, signer_chain, bundle_jws, epoch}
Guardian verifies bundle (03 LOCK-07); Setup sets Device Owner, PIN, claim blob (03 §4.2)
Guardian POST /v1/device/enroll/complete {claim_blob_hash} (mTLS)  -> state=claimed; open channel
```

Visit order: `verifier` inspects the ID and records `guardian_verification`; the station registers the phone (04 §4.6); the parent registers a passkey and grants consents; then Add device. DigiLocker is a `VerificationProvider` behind a flag.

### 4.4 Data model (every table also carries `family_id`; sketch, not DDL)

```sql
-- core
family(id, state[active|frozen|closing|closed])
guardian(id, family_id, role[owner|guardian|caregiver], email_enc, email_hmac UNIQUE, mobile_enc, verified_state)
guardian_verification(id, guardian_id, method[staff_id|digilocker], provider_ref, doc_type, doc_hmac, verifier_id, verified_at, notice_v)
passkey(id, guardian_id, cred_id UNIQUE, pubkey, sign_count)
child(id, family_id, display_name_enc, birth_ym, state)         -- band from birth_ym, Asia/Kolkata
device(id, family_id, child_id, model, serial_hmac UNIQUE, pubkey, cert_serial, cohort[lab|staff|external],
       state[unclaimed|claimed|suspended|released|revoked], integrity[unknown|ok|fail], build, spl, epoch, last_seen_at)
claim_code(code_hmac PK, child_id, created_by, expires_at, used_at, attempts)
-- graph (rules: 06)
contact_edge(id, child_a, child_b, CHECK(child_a < child_b), state[proposed|active|revoked|blocked],
             grants_a, grants_b, sched_a, sched_b, consent_a, consent_b)   contact_invite(code_hmac PK, from_child, expires_at, state)
-- policy
policy_section(child_id, section, rev, body jsonb, updated_by)   policy_override(device_id, section, body)
policy_bundle(device_id, rev, epoch, jws, sha256, not_after, acked_at)   device_outbox(device_id, seq, type, body, expires_at, acked_at)
approval(id, child_id, kind, subject, state, decided_by)   command(id, device_id, type, args, nonce, exp, state, result)
kill_state(scope, scope_id, level, features, set_by, approved_by)   place(id, child_id, name_enc, lat_enc, lon_enc, radius_m, presence_on)
-- append-only chains
consent_ledger(.., purpose, action, notice_v, lang, prev_hash, hash)
audit_log(family_id, seq, at, actor, action, target, meta, prev_hash, hash)   staff_audit(same shape)   audit_anchor(at, root, kms_sig, s3_key)
-- database zune-vault
dek(id, family_id, child_id, month, wrapped, state)   hold(id, scope, reason_ref, opened_by, approved_by, released_at)
item(id, group_id, child_id, class, dek_id, nonce, ct, meta, created_at, retain_until, state[live|sealed|deleted], hold_id)
erasure(id, family_id, child_id, mode, state[requested|applied|sealed|shredded|done])
-- RLS: CREATE POLICY fam ON t USING (family_id = current_setting('app.family_id')::uuid);
```

Effective permission (06 enforces): `edge.state='active' AND grants_a[ch] AND grants_b[ch] AND open(sched_a,ch,now) AND open(sched_b,ch,now)` and both children active.

### 4.5 Policy resolution and signing

```go
func Resolve(c Child, d Device, now time.Time) Signed {
  b := Template(c.Band(now))            // backend/policy/templates/band-{7-9,10-12,13-14}.yaml
  b = Clamp(Merge(b, Sections(c), Overrides(d)), SafetyKeys)
  b.Contacts, b.Kill, b.Rev = Effective(c, now), KillFor(d), NextRev(d)
  MustValidate(b, "policy-v1.schema.json"); return KMSSign("policy-signer", b)   // ES256 JWS, x5c
}
```

Template values (`templates/*.yaml`) are product-owned, reviewed with 09 [INFERRED]. Command TTLs: `lock` 24 h, `ring` 10 min, `pin_reset` 15 min, `service_unlock` 30 min, `factory_qa` 30 min, `kill` and `unenroll` 72 h, `policy_refresh` 1 h; `lock` takes `{state:on|off, until?}`. Requested `policy-v1` additions (owner 03; the full list is the 03 §4.4 table): `assistant{on,images,mode}`, `content{allow,deny}`, `vis{notice_v}`, `places`, `cohort`, per-channel schedules in `contacts.entries`. The `policy-signer` certificate is renewed every 60 days by a two-custodian ceremony with the offline root; if missed, devices run until `not_after`, then enter MINIMAL mode (03 LOCK-09).

### 4.6 Retention, withdrawal, erasure

| Class | Retention |
|---|---|
| Message content, AI turns, image references (vault `item`) | 12 months |
| Call and walkie metadata, approvals, commands, usage aggregates | 12 months (portal shows 90 days) |
| Presence events | 30 days [INFERRED] |
| SOS events | 12 months |
| Shares from Photos, Journal and Notebook (vault class `share`, 09 §4.5) | 12 months |
| Crash reports (`ops.crash`, only with `diagnostics`, 09 §4.8) | 30 days [INFERRED] |
| Station job records (no personal fields, 10 §4.4) | 12 months |
| Redeemed, expired or revoked claim codes and contact invites | purged after 30 days [INFERRED] |
| Audit chain, consent ledger, verification records | account life + 12 months [INFERRED; counsel] |
| Security and infrastructure logs | 12 months |

Consent purposes: `account` (necessary), `visibility` (parent reads messages and AI chats; withdrawing it disables Messenger and Assistant [INFERRED; counsel]), `ai` (vendor processors), `contact_pair` (both families, naming what each parent sees), `location`, `diagnostics`, `third_party_video` (YouTube Tier 2 disclosure, 08 CNT-10; only needed once Tier 2 is switched on).

Erasure: `requested` (step-up), `applied` (views removed, processing stopped, device unenrolled for family scope), then by `erasure_mode` `sealed` (unreadable to portal and services, held to `retain_until`, opened only by break-glass on legal process) or `shredded` (DEKs destroyed), then `done`. Family A's erasure never touches Family B's copy; a hold keeps items in both modes.

### 4.7 Portal pages (Stage 1)

| Route | Main APIs | Acceptance |
|---|---|---|
| `/setup` | `consents`, verification status | No claim code before verification and consents |
| `/` | SSE `events` | Per child: online, last seen, battery, build, minutes today, approvals, integrity, drift; events appear in 5 s |
| `/children/{c}/devices` | `claim-codes`, `devices/{d}/commands` | QR with countdown; lock applies in 5 s; ring; release with step-up |
| `/children/{c}/time` | `PUT policy/time` | Budgets, bedtime per day; ack within BE-08; stale `If-Match` returns 412 |
| `/approvals` | `GET approvals`, `:decide` | Time, app, topic, video requests and contact invites; a decision issues a TTL grant; expires 24 h |
| `/children/{c}/contacts` | invites, edges | Code, link or QR only; per-side grants and schedules; revoke in 10 s; shows what the other family reads |
| `/children/{c}/messages` | `threads`, `messages` | Via vault; flagged first; other-family label; each open audited; sealed content absent |
| `/children/{c}/assistant` | `ai/sessions`, `PUT policy/assistant` | Transcripts, flags; on/off, images, mode within 10 s |
| `/children/{c}/content` | `PUT policy/content`, `caps` | Tier 2 default off; topics; Reader approvals; toggles from `capabilities.json` |
| `/children/{c}/places` | `places` | Weather place, home, school; presence opt-in with child-visible indicator; SOS history |
| `/account` | guardians, `privacy/*`, `grievances`, audit, notifications | Invite guardian (staff verification), ledger, withdraw, export, erase, audit log, grievance contact |

### 4.8 Staff console, observability, cost

Console: family lookup (no content), device lifecycle, verification, kill switches, break-glass requests, T&S flag queue, incidents, OTA publish, entitlements. Observability: OpenTelemetry with PII scrubbing to CloudWatch. Cost [INFERRED, about 2x either way, no quote]: Stage 1 fixed infrastructure with DR about USD 700-1,400 per month, USD 2-5 per device at about 300 devices (R05: USD 250-500 for 1,000 devices, no DR); vendors, SMS, staff excluded. Record actuals at Z4 exit.

## Acceptance criteria and tests

- **BT-01** No certificate or a `released` device is refused; a second connection supersedes the first; updates queued during 10 offline minutes arrive once, in order.
- **BT-02** 300 simulated devices, 50 edits per minute: ack p95 at most 10 s; `lock` p95 at most 5 s.
- **BT-03** Go-signed bundles verify in Kotlin; lowered `rev`, wrong device, expired signer, expired or replayed commands rejected; each safety key clamps; kill level 2 needs two approvals and lands in 10 s.
- **BT-04** Enrolment on Cuttlefish and a Pixel: expired or reused code, brute force, unverified guardian, wrong serial, integrity mismatch, wipe and re-claim follow BE-18 to BE-22; `service_unlock` with one signature is refused.
- **BT-05** Passkey without user verification refused; step-up expiry; OTP lockout; recovery hold; break-glass needs two approvers.
- **BT-06** A generated test over every table with `family_id`: Family A's session reads nothing of Family B; a purpose without consent disables its feature.
- **BT-07** A `zune-vault` dump holds no plaintext; `policy` cannot decrypt; each message has two copies; reads appear in the audit view.
- **BT-08** Staging clock plus 12 months: sweeper deletes, DEKs destroyed, a restored backup row is unreadable; `seal`, `delete_now`, hold cases pass.
- **BT-09** Editing an audit row in staging is caught by the verifier (Sev-1); seeded names and message strings appear in no log, metric or trace.
- **BT-10** Export holds only the requesting family's data. A headless browser sees strict CSP and zero third-party requests.
- **BT-11** SOS reaches every guardian in 10 s; unacknowledged for 5 min pages `tns`.
- **BT-12** A non-allowlisted name is refused over DoT, allowed names are not logged; `generate_204` returns 204 on both schemes.
- **BT-13** OTA metadata needs two approvals; ZuneUpdater refuses a bad signature (04 G3).
- **BT-14** DR drill: promote ap-south-2, devices reconnect; RPO and RTO recorded in `milestones/Z4.md`.
- **BT-15** From the prod account an us-east-1 call is denied; a `policy` task cannot reach the internet; `ai-gateway` reaches only allowlisted hosts.
- **BT-16** Playwright at 360 px passes each §4.7 acceptance cell.
- **BT-17** A route absent from `openapi.yaml` is refused; every §BE-46 route exists with its auth mode; a pre-claim `factory/qa` call with a replayed token fails.
- **BT-18** A secret rotation drill in staging rotates one HMAC key (`serial_hmac`) with both `kid`s verifying and no outage; a repository, image and state scan finds no secret.
- **BT-19** `hostnames.yaml` matches the live certificates; an expiring test certificate alerts 21 days out; the mail domain passes SPF, DKIM, DMARC; a forced alert pages the on-call within 5 minutes with no personal data in the payload.
- **BT-20** A migration rehearsal on a restored snapshot completes with timing recorded; the previous device client still connects after an expand step; a `/v2` route does not break `/v1`.

## Verify first

Nothing here was run on AWS; log results in `zune/docs/verified-facts.md`.

| ID | Claim | Why uncertain | How to verify | If false |
|---|---|---|---|---|
| V1 | Both Indian regions offer Fargate, cross-region RDS replicas with multi-Region KMS, ElastiCache, NLB TLS, S3 Object Lock replication; RDS backups cap at 35 days [01 V12, MEMORY] | Unchecked | `terraform plan` in both | ECS on EC2 or reduced DR; founder re-approves spend |
| V2 | KMS signs ES256 and Ed25519 (`channel`, 04 REL-12) in ap-south-1 [MEMORY] | Ed25519 unclear | Create keys; sign and verify in Go and Kotlin | `channel` becomes ECDSA P-256 (edit 04 REL-12, REL-16) |
| V3 | DoT via NLB TLS with an ACM certificate satisfies strict Private DNS [03 VG-8] | Untested | Pixel with `setGlobalPrivateDnsModeSpecifiedHost` | Unbound terminates TLS with a public-CA certificate |
| V4 | Privileged Guardian gets the serial in key attestation on 10a and 9a; `android/keyattestation` accepts Android 17 and P-384 chains [R05 F8, R10 F12] | RKP without GMS unverified | Z2 attestation test | Parent confirms the last 4 serial characters ZuneSetup shows |
| V5 | One WebSocket survives Doze and carrier NAT at 180 s with acceptable battery [R13 F3, R05 §4.5] | Unmeasured; short pings hurt (R13) | Pixels, four carriers, Wi-Fi, 72 h | Longer keepalive, `JobScheduler` poll, tell 06 |
| V6 | Staff-inspected ID plus OTP plus stored record meets Rule 10 without DigiLocker [R19 Q2] | Mirrors; corrigendum unread | Counsel (LEG-1, LEG-3) | DigiLocker mandatory; external families wait |
| V7 | Rule 8(3) covers message content, and sealing satisfies s.6(4) and s.8(7) [R19 Q4; s.8(7) content MEMORY] | Scope ambiguous | Counsel | `erasure_mode=delete_now`; shorter content retention |
| V8 | CERT-In: 180-day in-India logs, NIC or NPL time; DPDP Rule 7 72-hour breach report (11 VL-1, VL-5); no hostnames verified [R19, secondary] | Direction unread | Read the 28 Apr 2022 direction; set `config_ntpServers` (02) only from NIC or NPL pages | Own `chrony`; devices use signed server time |
| V9 | Passkeys, DLT SMS, email and Web Push (iOS needs Home Screen install) work for Indian parents [R05 P, R19 MEMORY, R05 S] | Untested | Six phone and browser pairs; register DLT; send tests | Email OTP plus TOTP; email plus Web Push; `tns` phones for SOS |
| V10 | Cost ranges (§4.8): USD 700-1,400 a month fixed with DR, about INR 340-670 per child-month at 200 children | No quotes; 01 Verify 12 and 10 §4.12 once quoted other figures | AWS calculator at Z4 | Re-approve budget; PAY-1 re-prices |
| V11 | Staff IdP (AWS IAM Identity Center or equivalent in an India region), SES in ap-south-1 with DKIM and DMARC, Secrets Manager rotation, ACM export limits for DoT and TURN [MEMORY] | Unchecked | Create each in staging; send test mail; rotate a test secret | Self-hosted IdP; another India-region mail sender; public-CA certificates on the endpoints |

## Risks, open gates and out of scope

Risks:
1. The vault holds children's messages and AI chats; a breach is existential (BE-29 to BE-35; pen test before any external family).
2. Parent reading is the central DPDP s.9(3) exposure [R19]; both-family consent and read audit reduce it; counsel decides.
3. Passkeys bind to the RP ID; a rename after name clearance (A5) breaks them (BE-24).
4. The 60-day signer ceremony is a human dependency (§4.5).
5. Fixed cost dominates at about 200 families; the INR 199 founding price is below per-child cloud cost [R20].
6. Channel battery, NAT and Doze behaviour are unmeasured (V5); SOS staffing is a dependency (EXT-3).

Gates (IDs per 01):
- **[GATE: before build]** V1, V2 recorded; neutral domain and RP-ID ADR; B-1 AWS spend approved.
- **[GATE: before staff pilot]** SP-1 to SP-3 evidence; BT-08, BT-14, BT-17 to BT-20 passed; named on-call rota (BE-49); signer-renewal rehearsal; independent test of portal and device API with no open P1.
- **[GATE: before external family]** LEG-1 (including parent reading and erasure against Rule 8(3)), LEG-3, LEG-4, LEG-5, LEG-7, EXT-3, EXT-7.
- **[GATE: before charging]** PAY-1.

Out of scope: Caregiver UI; parent-side calling (D8); parent-key E2EE; SMS reader, call allowlists (D19); payments; analytics; active-active multi-region; Indic UI (D20).
