# Zune research 12: Cellular calls and SMS with parent-controlled allowlists

Date: 2026-10-02. Tags: [P] read in a primary source or real source file this session (repo@ref:path or URL); [S] reputable secondary source or search summary; [I] my engineering judgement; [M] training memory, unchecked. android.googlesource.com is still blocked (tested once, HTTP 403, not retried), so code was read from GrapheneOS `17` branches (android-17.0.0_r1 plus later patches). grapheneos.org, gigs.com, telnyx.com and t-mobile.com were egress-blocked (GrapheneOS text was read from its GitHub repo). Only reports 01 and 02 existed when this was written.

## 1. Summary and recommendation

Voice and SMS are buildable on Android 17 without Google apps, but not from AOSP parts alone. AOSP 17 ships the plumbing (Telecom, TeleService, TelephonyProvider, Mms service, CellBroadcast, carrier config) but no usable messaging app and no eSIM manager. On Pixels, IMS (VoLTE), the eSIM manager and carrier data come from Google's stock images. We must write: a Dialer/InCall app, an SMS "vault" app, a guardian/policy agent, and a patch set in Telecom and Telephony.

**Enforce the allowlist in the framework, not in apps.** Role-based hooks fail the "determined child" bar for three reasons found in the code: call screening cannot block outgoing calls, it fails open after 5 seconds, and `DISALLOW_OUTGOING_CALLS` is all-or-nothing and checked only at the intent entry point. Add a system-process policy service (signed policy, deny by default) consulted in-process by Telecom's incoming filter graph, by `TelephonyConnectionService` for outgoing and incoming PSTN/IMS connections, and by the MMI/USSD path. Emergency calls and parent numbers bypass it. The cost is a permanent fork of two modules, rebased every AOSP drop; a June 2026 Telecom CVE fix shows this surface is actively attacked.

SMS: hold the default SMS role with no UI. Persist each message to an encrypted queue, upload to the portal, wipe locally, never write the SMS provider, and grant READ_SMS, RECEIVE_SMS and SEND_SMS to no other app. Stage 1 does not capture MMS bodies and does not record call audio (wiretap exposure). Carrier path: US only, VoLTE only, Wi-Fi calling off, bring-your-own SIM in beta, then one host network (T-Mobile via an MVNE) at general availability.

## 2. Findings

### 2.1 What AOSP 17 ships

| Component | Android 17 status | Basis |
|---|---|---|
| Telecom | Two repos in the manifest: `packages/services/Telecomm` (the code GrapheneOS patches) and new `packages/modules/Telecom`; Telecomm's build has a `release_telecom_mainline_module` switch. modules/Telecom was unreadable, so which one our build compiles is unconfirmed | [P] GrapheneOS/platform_manifest@17:default.xml; platform_packages_services_Telecomm@17:Android.bp |
| TeleService, frameworks/opt/telephony, modules/Telephony, TelephonyProvider, Mms service, BlockedNumber/CallLog/Contacts providers | Present | [P] manifest |
| CellBroadcastReceiver + modules/CellBroadcastService | Present; keep for WEA | [P] manifest |
| ImsServiceEntitlement, modules/ImsStack, ImsMedia, Stk, CarrierConfig, BasicSmsReceiver, EmergencyInfo | Present (BasicSmsReceiver purpose unverified; check as SMS-role template) | [P] manifest |
| Dialer | In the 17 manifest but unsupported since the 2023 deprecation | [P] manifest; [S] https://www.androidauthority.com/google-kill-android-aosp-dialer-messages-app-3334980/ |
| Messaging | In android16-release, absent from 17. GrapheneOS ships `external/Messaging` as a prebuilt APK (v16, 2026-09-30). AOSP (not GrapheneOS) removing it is inferred | [P] manifest diff vs aosp-mirror/platform_manifest@android16-release; platform_external_Messaging@17; [I] |
| eSIM manager (LPA) | None in AOSP. GrapheneOS backports Google's `EuiccGoogle`, `EuiccSupportPixel*` and euicc APEX from stock images, off by default | [P] GrapheneOS/adevtool@17:config/device/common/backport.yml; grapheneos.org usage |
| IMS on Pixel | `ShannonIms.apk`, `ShannonRcs.apk`, `libsitril-ims.so` come from the stock image | [P] adevtool backport.yml |
| Carrier config, APNs, MMS config | GrapheneOS converts Google's CarrierSettings database via `CarrierConfig2` | [P] platform_packages_apps_CarrierConfig2@17:README.md |
| RCS | Only Google Messages with sandboxed Play; no RCS client without GMS | [P] grapheneos.org usage |

**Minimum set for voice + SMS + emergency + WEA:** Telecom, TeleService, frameworks/opt/telephony, Telephony module, TelephonyProvider, Mms service, CallLog/Contacts/BlockedNumber providers, CellBroadcastReceiver/Service, CarrierConfig2 plus extracted Google carrier data, vendor IMS/radio, EmergencyInfo, ImsServiceEntitlement if a carrier needs it. Exclude AOSP Dialer, Messaging, Stk and the Contacts UI. **We write:** ZunePhone, ZuneSmsVault, ZuneGuardian, the policy service and Telecom/Telephony patches, overlays.

### 2.2 Why role-based enforcement is not tamper-proof

- For outgoing calls Telecom binds the screening app only for caller-ID lookup and ignores the answer (`CallsManager.bindForOutgoingCallerId`, ~line 3300) [P].
- The incoming filter graph starts from `DEFAULT_RESULT` with `shouldAllowCall(true)`; on the default 5000 ms timeout it completes with that result (`IncomingCallFilterGraph`, `Timeouts.getCallScreeningTimeoutMillis`) [P]. A killed or slow app lets the call ring.
- `DISALLOW_OUTGOING_CALLS` is boolean, spares emergency numbers only, is checked in `UserCallIntentProcessor` and conference creation, and skips self-managed (VoIP) calls [P] Telecomm@17: UserUtil.java, components/UserCallIntentProcessor.java.
- Google's 2026-06-17 fix says unprivileged apps could bypass `NewOutgoingCallIntentBroadcaster` checks via the `UserCallActivity` trampoline and "silently execute dangerous MMI/USSD codes (e.g. call forwarding) or auto-dial emergency numbers" [P] Telecomm@17 commit 21585d3.
- `BlockedNumberContract` is a blocklist; an allowlist would mean importing the whole number space. The call-redirection role cannot stop emergency calls [P] NewOutgoingCallIntentBroadcaster.java header.

### 2.3 Hooks already in the code

- `setUpCallFilterGraph` (CallsManager.java ~1100) is where a mandatory `ZuneAllowlistFilter` sits beside `BlockCheckerFilter` [P].
- `onSuccessfulIncomingCall` skips filtering for emergency-callback mode, network-identified emergency calls and emergency SMS mode; `Timeouts` defaults the callback window to 5 minutes [P].
- `TelephonyConnectionService.onCreateOutgoingConnection` (~line 1125) is the single PSTN/IMS choke point and already blocks call-forwarding prefixes per number while roaming [P] platform_packages_services_Telephony@17.
- `MmiUtils` already treats call-forwarding and vertical service codes (`*72`, `*67`...) as dangerous [P].
- `ACTION_DIAL_EMERGENCY` resolves to `config_emergency_dialer_package`, so our dialer can own emergency UI [P] TelecomServiceImpl.java ~2721.
- "Secret codes" are broadcast by the Dialer app and merely consumed by Telecom's `DialerCodeReceiver` [P]; with no AOSP Dialer that surface disappears. TeleService test activities (RadioInfo, `*#*#4636#*#*`, which GrapheneOS uses for eSIM bring-up) must be stripped on `user` builds [P]/[I].

### 2.4 Caller-ID spoofing (STIR/SHAKEN)

`Call.Details.getCallerNumberVerificationStatus()` exists since API 30; on 4G+ only the verdict is shared [P] https://developer.android.com/develop/connectivity/telecom/dialer-app/prevent-spoofing. Telecom's `Call` carries it, so a system filter reads it directly [P]. Telephony sets it only from IMS call profiles (`ImsPhoneConnection.java:224`) and otherwise leaves "not verified" [P] frameworks_opt_telephony@17. So it exists on Android 17 but only on VoLTE/Wi-Fi calls where the carrier supplies it; whether the Pixel IMS stack populates it per US carrier is unverified [I].

### 2.5 SMS plumbing

- `SMS_DELIVER` goes only to the default SMS app; with none, to all receivers. Other RECEIVE_SMS holders get `SMS_RECEIVED` [P] InboundSmsHandler.java ~1915-1950, ~2199. We must hold the role.
- Role requires: SMS_DELIVER receiver, WAP_PUSH_DELIVER receiver, RESPOND_VIA_MESSAGE service, `smsto` SENDTO activity; `config_defaultSms` presets the holder [P] Permission@17:PermissionController/res/xml/roles.xml. Our SENDTO and respond-via stubs do nothing.
- Inbound PDUs sit in the provider `raw` table until the broadcast completes, so the vault must persist before returning [P]/[I]. SMS over IMS uses the same handler [P].
- Android 17 withholds OTP SMS from non-default apps for 3 hours; the default SMS app is exempt [P] https://developer.android.com/about/versions/17/behavior-changes-all.
- No framework check blocks sending beyond permissions and app-ops (`DISALLOW_SMS` only affects broadcast routing and Telecom's reply-with-SMS) [P]. A2 is enforced by granting SEND_SMS to nobody.

### 2.6 Carrier, SIM and modem realities

- Pixel 10, Pro and Pro XL US models have no SIM tray; the Pro Fold keeps one [S] https://www.androidauthority.com/google-pixel-10-no-physical-sim-3586171/. For the 10a, search summaries conflict: **unverified**, which matters because report 02 picks the 10a.
- GrapheneOS reports VoLTE, SMS, MMS and calling work on carriers Google supports on stock, and that carriers restrict VoLTE on imported Pixels by whitelisting IMEI ranges of locally sold SKUs [P] grapheneos.org usage. That suggests VoLTE is gated by hardware IMEI, not OS, favoring US-SKU Pixels [I].
- US 3G is off (2022), so VoLTE is mandatory [S] https://www.phonearena.com/news/t-mobile-verizon-att-sprint-2g-3g-4g-lte-network-shut-down-date_id134159.
- Verizon Open Development has a "Device Maintenance and Regression Process" for modified approved devices [S] https://opendevelopment.verizonwireless.com/content/dam/opendevelopment/pdf/OD_Device_Certification_Process.pdf (summary only). FCC Class II change applies only if software alters RF results [S] https://markready.io/learn/fcc-permissive-changes. Keeping modem firmware, IMS apks and carrier data byte-identical to Google's (what adevtool does) is the best argument nothing certified changed [I].
- Google's Emergency Location Service needs Play services [S] https://www.android.com/safety/emergency-help/emergency-location-service/; non-GMS E911 performance is unverified.

### 2.7 Incumbents and suppliers [S unless noted]

- Gabb: Verizon MVNO; Bark: T-Mobile MVNO (https://www.fierce-network.com/wireless/bark-technologies-strikes-mvno-deal-t-mobile-child-safety-phone); Troomi: AT&T, locked to its plan; Pinwheel: carrier-agnostic, parent approves every contact and sees texts. Retail $20-25 (Gabb), $27-50 (Troomi), $39-89 (Bark) per month.
- T-Mobile "Your Name, Our Wireless": white-label MVNO, under 3 months to launch (https://www.t-mobile.com/news/network/t-mobile-launches-your-name-our-wireless). Gigs ("MVNO in a box": voice, SMS, data, eSIM, porting, API) and Telnyx Mobile Voice (VoLTE SIM/eSIM with real numbers, from $5/SIM/month, marketing; https://telnyx.com/products/mobile-voice) are candidates, unvalidated.
- Twilio Super SIM, Soracom and 1NCE are IoT-only: no consumer voice or no phone-to-device SMS (vendor docs via search).
- No primary wholesale price found; planning figure $6-12 per line per month for voice, SMS and modest data [I, unverified].

### 2.8 Law and regulation (all need counsel)

- 911: carriers must deliver all wireless 911 calls regardless of validation, including non-initialized handsets [S] https://www.law.cornell.edu/cfr/text/47/9.10. WEA devices must keep alerts in a consumer-accessible place for 24 hours [S] https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-10.
- Wiretap Act is one-party consent; parental "vicarious consent" is accepted by some courts, rejected by others; all-party states complicate it; access after receipt is generally outside "interception", but forwarding from the device is a gray area [S] https://www.congress.gov/crs-product/R41733, https://privacyresearchgroup.law.nyu.edu/2016/04/parental-eavesdropping-an-exception-for-best-interests/.
- COPPA amendments: effective 2025-06-23, compliance by 2026-04-22; separate consent for third-party disclosure; written retention policy [S] https://www.dglaw.com/the-ftc-finalizes-amendments-to-the-coppa-rule/.
- Third-party senders and callers cannot be notified; GDPR/ePrivacy only if EU launch [M].

## 3. Options and trade-offs

| Decision | Options | Pick |
|---|---|---|
| Enforcement | A: roles. B: fork Telecom/Telephony with a system policy service. C: B plus network-side filtering | **B now, C in Stage 2.** A fails open and cannot gate outgoing calls |
| Policy delivery | Screening-service IPC vs in-process snapshot | In-process snapshot; no IPC on the call path |
| SMS | Default role + vault; no default app; hidden Messaging fork | Vault. No default app broadcasts to everyone; a Messaging fork keeps a readable database |
| MMS | Disable; capture; metadata only | Metadata only (sender, size, expiry from WAP push); capture in Stage 2 |
| Network | BYO SIM; one MVNE line; IoT SIM | BYO SIM for beta, T-Mobile MVNE line at GA; IoT SIMs cannot do voice |
| Wi-Fi calling | On/off | Off in Stage 1 (E911 address handling, carrier apps GrapheneOS lacks) |
| Call recording | Ship it / none | None |

## 4. Recommended Stage-1 design

**Components**
1. `ZunePhone` (DIALER role): contacts-only call list, large emergency button, `ACTION_DIAL`, `ACTION_DIAL_EMERGENCY`, `InCallService`; no free keypad (an "ask a parent to add a number" box feeds the portal); no voicemail, add-call or secret codes.
2. `ZuneSmsVault` (SMS role, no launcher, no notifications): SMS_DELIVER and WAP_PUSH_DELIVER receivers plus the two stubs. `onReceive` writes to an encrypted queue (Keystore AES-GCM); WorkManager uploads over TLS 1.3 with device-signed requests; on ack it deletes and checkpoints. Queue cap: 14 days or 5,000 messages, then drop oldest with a gap marker. Never writes `content://sms`.
3. `ZuneGuardian` (privileged): pairing, policy sync, event upload, own push channel (no FCM; reconcile with report 05).
4. `ZunePolicyService` (system service, `/data/system/zune/policy.bin`): verifies an ECDSA P-256 portal signature with pinned key, monotonic version and expiry; exposes `check(direction, e164, presentation, verstat, now)` to Telecom and Telephony; deny-by-default if file missing or invalid.

**Decision function**
1. Emergency: `TelephonyManager.isEmergencyNumber` plus explicit 911, 112, 988 (988 is an ordinary routed number [I]) always allowed.
2. Inbound in emergency-callback state or window: allow everything, including withheld numbers, using AOSP's skip path, extended to 30 minutes after any emergency call [I; confirm with carrier and counsel].
3. Guardian numbers: allowed both ways, immune to schedules; inbound rejected only if verstat is FAILED.
4. Everyone else: exact E.164 match (libphonenumber, region from SIM, post-dial digits stripped), matching direction and schedule window. Withheld, alphanumeric, SIP and short-code numbers are never allowed unless added. Any dial string with `*`, `#` or letters is rejected, which blocks all MMI/USSD. No suffix matching.
5. Policy missing or unsynced beyond 14 days: guardians and emergency only. Never fail open.
6. Time: last signed server time plus `elapsedRealtime`; `DISALLOW_CONFIG_DATE_TIME`.

**Hook points (about 1-2k lines [I])**: `UserCallIntentProcessor` (friendly "ask your parent" dialog), `TelephonyConnectionService.onCreateOutgoingConnection` (authoritative), `CallsManager.startOutgoingCall`, mandatory `ZuneAllowlistFilter` in `setUpCallFilterGraph` (reject always wins), MMI/USSD in `handleMmiCode` and the phone layer, ignore `EXTRA_SKIP_CALL_FILTERING` on the PSTN account. Blocked inbound calls are rejected, logged and raised as "pending approval".

**Bypass matrix**

| Vector | Control |
|---|---|
| `tel:`/ACTION_CALL from other apps | No third-party apps; enforcement below the intent layer |
| MMI/USSD, `*21*`, `*67`, `*#06#`, hidden codes | Dial-string rule; no Dialer; strip TeleService test activities; no Stk, so SIM "set up call" has no handler [I] |
| Add call, merge, conference | Each leg is a new outgoing call, checked; remote-initiated network merges are uncontrollable |
| Voicemail | No voicemail number in overlay; MVNE voicemail off; MWI notifications suppressed |
| Settings forwarding/barring | No Settings entry; `DISALLOW_CONFIG_MOBILE_NETWORKS` |
| SIP/VoIP | No UI to add accounts; non-`tel:` rejected; our self-managed apps apply the messenger/video allowlist themselves |
| Wi-Fi calling | Off via carrier-config override |
| Spoofed or withheld ID | Reject FAILED verstat, block withheld; VERIFIED-only mode in Stage 2 |
| Second SIM, SIM swap | Policy is SIM-independent; SIM lock is Stage 2 |
| Timeout or app crash | Synchronous in-process check |
| Debug, reset | `user` build, `DISALLOW_DEBUGGING_FEATURES`, factory reset and safe boot disallowed (reports 04, 10) |

**SMS hygiene.** Nothing but the vault touches SMS text: no notifications, no Settings entry, no READ_SMS/RECEIVE_SMS for the Assistant (report 07) or anything else (privapp allowlist), `allowBackup=false` with empty extraction rules, no content logging, adb off. Consequences of A2: no text-to-911, no "STOP" replies, no quick-reply texts; any carrier flow needing a mobile-originated SMS must be tested with the host carrier. Short codes and OTPs are captured and flagged; parent push notifications never carry bodies.

**Carrier setup.** US only; VoLTE on; VoWi-Fi, VVM, RCS and voicemail off via CarrierConfig2 overrides [I]. CellBroadcastReceiver stays visible with alert history (24-hour rule). eSIM profiles are downloaded by a privileged Zune Setup app through `EuiccManager` and the stock LPA [I], which inherits report 02's Pixel-binary licensing question.

**Parent portal (Stage 1)**

| Feature | Detail |
|---|---|
| Contacts and rules | Contact (name, E.164, relationship, guardian flag); per-direction toggles for call-in, call-out, messenger, video, walkie; device-wide quiet hours plus per-contact windows |
| Call log | Direction, E.164, start, duration, result (connected, missed, blocked: not allowlisted, schedule, spoof, withheld; emergency), network type, verstat |
| Pending approvals | Blocked inbound numbers and child "please add" requests; approval creates a rule |
| SMS inbox | Read-only threads, sender flags (unknown, short code, alphanumeric), MMS placeholder, search, delete, export; retention default 90 days (30/90/365) |
| Alerts | Emergency call placed, possible spoof, repeated unknown caller, policy unsynced for N days |
| Audit | Immutable log of policy changes and portal SMS reads (actor, time, before/after) |

Schema sketch: `family`, `guardian`, `device(msisdn, iccid, policy_ver, last_sync)`, `contact(e164, label, is_guardian)`, `allow_rule(contact_id, device_id, channel, direction, windows_json)`, `policy_bundle(device_id, version, body, sig, expires_at)`, `call_event(direction, e164, started_at, duration_s, result, reason, verstat, net_type)`, `pending_request(e164, kind, state)`, `sms_msg(sender_raw, sender_e164, body_enc, received_at, flags, mms_meta)`, `audit(actor, action, target, before, after, ts)`. TLS 1.3 in transit; per-family KMS data key at rest.

**Pre-beta tests**: carrier matrix (VoLTE, hidden number, verstat, emergency callback), MMI/USSD and intent fuzzing, E911 and WEA tests with the host carrier, offline and expired-policy behavior.

## 5. Stage-2 improvements

Network-side allowlist and SIM/IMEI lock via MVNE API; Wi-Fi calling with parent-entered E911 address; MMS capture (images to portal only); parent-composed replies, optional auto-reply and a "text 911/988" button limited to those destinations; VERIFIED-only mode and spam intelligence; AI risk flags on SMS (bullying, grooming); optional end-to-end encryption to a parent-held key; opt-in call recording where legal; calendar-style schedules and time budgets; multi-guardian roles; remote eSIM provisioning from the portal; parent-side calling.

## 6. Conflicts with earlier reports (01-11)

- **02:** "no voice/SMS in v1", its decision 3 and risk 4 are superseded by D4-D6. Its Pixel 10a may be eSIM-only in the US (unverified), changing the SIM plan. The Google-binary licensing risk (F5) now also covers IMS and eSIM components.
- **01:** "review Messaging, Dialer": Messaging is absent from the 17 manifest; Dialer is present but replaced by ZunePhone. Add the Telecom and Telephony forks to the rebase list and note the `modules/Telecom` vs `services/Telecomm` split. The 3-hour OTP delay item is consistent (default SMS app exempt).
- **08:** per the brief, its "v1 position on telephony" (no cellular) is superseded. It was not present; messenger and video should reuse this policy service, because self-managed VoIP calls bypass `DISALLOW_OUTGOING_CALLS`.
- **04, 05, 09, 10, 11 (not present):** expected changes. 04: carrier entitlement and E911 screens use WebView, and MMS/WAP links must open nothing. 05: allowlist lives in the framework, not the guardian app. 09: no Contacts UI; contacts come from the portal. 10: OTA must carry the Telecom/Telephony patches and keep vendor radio/IMS identical to Google's. 11: add wiretap, COPPA, 47 CFR 9.10, WEA, HAC and CPNI.

## 7. Risks and unknowns

1. Google licence for shipping stock radio, IMS and eSIM components commercially (high; report 02 F5).
2. Host carrier or MVNE may require certification of an OS they have not tested (high; no primary evidence either way).
3. E911 quality without Google's Emergency Location Service (high; unverified).
4. Fork maintenance, and which Telecom repo the 17 build compiles (medium-high).
5. Wiretap, all-party-consent states, COPPA, retention and legal-process handling (high until counsel signs off).
6. Pixel 10a SIM tray; eSIM provisioning without GMS (medium).
7. Verstat availability and false positives on FAILED (medium).
8. Carrier provisioning that needs mobile-originated SMS while A2 forbids sending (medium).
9. Ported iPhone numbers must be deregistered from iMessage or texts vanish [P] grapheneos.org usage.
10. Hearing-aid compatibility and a reseller's FCC responsible-party status [M]; wholesale pricing unverified.

## 8. Decisions needed from the founder

1. **Network model.** Default: BYO SIM in beta, one T-Mobile MVNE line at GA.
2. **Enforcement.** Default: fork Telecom/Telephony with a system policy service, accept rebase cost.
3. **Child sends SMS (A2).** Default: no in Stage 1; parent replies and emergency text in Stage 2.
4. **MMS.** Default: metadata only.
5. **Call audio recording.** Default: none.
6. **Unknown, withheld, spoofed callers.** Default: block, surface in portal, reject verstat FAILED.
7. **SMS retention and encryption.** Default: 90 days, server-side encryption.
8. **Child-facing disclosure.** Default: persistent in-device notice that parents see calls and texts.
9. **Wi-Fi calling.** Default: off in Stage 1.
10. **Legal and hardware checks.** Default: counsel review (wiretap, COPPA, FCC 911/WEA/HAC, CPNI) before beta; verify the 10a/9a SIM tray before ordering devices.

## 9. Load-bearing claims

1. Call screening cannot gate outgoing calls and fails open after 5 s. [P] Telecomm@17: CallsManager.java `bindForOutgoingCallerId`; callfiltering/IncomingCallFilterGraph.java; Timeouts.java.
2. `DISALLOW_OUTGOING_CALLS` is intent-entry-only, boolean, and skips self-managed calls. [P] Telecomm@17: UserUtil.java, components/UserCallIntentProcessor.java.
3. Intent-layer checks leaked MMI/USSD and emergency auto-dial as recently as June 2026. [P] Telecomm@17 commit 21585d3.
4. `TelephonyConnectionService.onCreateOutgoingConnection` is the PSTN/IMS choke point, and Telecom already exempts emergency-callback calls from filtering. [P] platform_packages_services_Telephony@17; Telecomm@17 CallsManager.java `onSuccessfulIncomingCall`.
5. SMS_DELIVER goes only to the default SMS app (all receivers if none); the role needs four stub components. [P] frameworks_opt_telephony@17 InboundSmsHandler.java; Permission@17 roles.xml.
6. AOSP 17 has no Messaging app (present in 16) and no eSIM LPA; Pixel IMS, eSIM and carrier data come from stock images. [P] manifest diff; adevtool@17 backport.yml; CarrierConfig2 README.
7. STIR/SHAKEN verdict is exposed (API 30) but populated only from IMS call profiles. [P] developer.android.com prevent-spoofing; frameworks_opt_telephony@17 imsphone/ImsPhoneConnection.java:224.
8. GrapheneOS gets VoLTE/SMS/MMS on Google-supported carriers, carriers gate VoLTE by IMEI range, and eSIM management needs a proprietary Google component. [P] GrapheneOS/grapheneos.org@main:static/usage.html.
9. IoT SIM vendors do not offer consumer voice/SMS; kids' phone incumbents each use one host network. [S] vendor docs via search; Fierce Network.
10. Pixel 10, Pro and Pro XL US models are eSIM-only; the 10a is unverified. [S] androidauthority.com Pixel 10 SIM article; conflicting search summaries.
