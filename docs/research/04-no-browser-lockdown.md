# 04 - Making "no browser" real: threat model and enforcement

Status date: 2026-10-02. Basis tags: **[P]** read in a primary source or real source file this session; **[S]** reputable secondary (often only the search summary was readable); **[I]** engineering inference; **[M]** memory, unchecked. Source keys (S1...) are listed at the end. `source.android.com` and `android.googlesource.com` were blocked, so AOSP 17 code was read from GrapheneOS's `17` branches (`android-17.0.0_r1` plus their patches). I treat those files as AOSP-equivalent unless marked GrapheneOS-specific.

## Summary & recommendation

Deleting a browser APK does not deliver "no browser". Browsing needs (1) an engine that renders web content (WebView), (2) a way to reach an arbitrary URL (an `ACTION_VIEW http(s)` handler or URL box), and (3) a path to the open internet. Zune must break at least two, in code the child cannot change. Realistic attacks by a 10-14-year-old: link taps, hidden system WebViews, Wi-Fi/carrier sign-in pages, sideloading, developer options, recovery or reflash.

Recommendation:
1. **The image is the root of trust; policy is only the dial.** Everything that defines "no browser" is compiled into the verified, locked image. Parent preferences are delivered as policy.
2. **Keep WebView, but make it a controlled substance.** Ship one Chromium-based provider; add a small system_server patch so only two Zune packages can instantiate a WebView; give the EPUB reader a WebView with **no INTERNET permission**; confine the Videos WebView with a proxy and allowlist.
3. **Close the intent plane:** no http(s) handler anywhere in the image (CI-enforced) plus a baked Intent Firewall rule.
4. **Close the network plane in two stages.** Stage 1: INTERNET only for about 8 packages, strict Private DNS to a Zune resolver, our own captive-portal URLs and no portal UI. Stage 2: always-on lockdown VPN with domain/SNI allowlist.
5. **Close the boot chain:** `user` build, locked bootloader with Zune AVB key, OEM-unlock bit forced off, no Developer options, no multi-user.
6. **Sell pre-flashed devices.** Image-only sales cannot honestly carry the claim. Say "no browser, Zune-approved content only", never "no internet" or "unbypassable".

## Findings

**F1. AOSP 17 is not browser-free and hides WebViews.** The AOSP manifest still contains `packages/apps/Browser2` and `QuickSearchBox` [P: S23]. `handheld_system.mk` installs `CaptivePortalLogin`, `DocumentsUI`, `PrintSpooler`, `CertInstaller`, `BookmarkProvider`, `PrivateSpace`, `VpnDialogs`; `media_system.mk` installs `HTMLViewer`; `telephony_system.mk` installs `CarrierDefaultApp` [P: S2]. Three are escape hatches:
- `CarrierDefaultApp` has a **disabled alias `URLHandlerActivity` claiming `VIEW` + `http`/`https` + host `*`**; carrier signals enable it and it hosts a JS-enabled WebView [P: S1].
- `OsuLogin` (Passpoint sign-up) sits inside the Wi-Fi Mainline module with INTERNET and a JS-enabled WebView [P: S4].
- `HTMLViewer` blocks network and JS, but turns link clicks into `ACTION_VIEW`+BROWSABLE intents, so any http(s) handler becomes a browser [P: S7].

**F2. WebView supply.** Neither downstream manifest has `external/chromium-webview`, and LineageOS says building WebView inside AOSP "is no longer supported", so AOSP 17 gives us no implementation [P: S10, S23; absence inferred]. GrapheneOS whitelists one provider, `app.vanadium.webview` [P: S1]: Chromium plus a GPL-2.0-only patch set with CFI, on Chromium's cadence, at 154.0.8037.x like LineageOS's prebuilt [P: S9, S10]. Provider updates are ordinary APK updates checked for signature and minimum version [P: S1].

**F3. A WebView gate exists and is small.** Every WebView first calls `WebViewUpdateService.waitForAndGetProvider()` in system_server, which already reads `Binder.getCallingUid()` [P: S1]. A caller allowlist there (about 20 lines) makes WebView fail for every other package, including hidden ones like OsuLogin [I]. It is the best single choke point.

**F4. Origin allowlists: what holds.**

| Mechanism | Layer | Holds? |
|---|---|---|
| Network Security Config | app | **No allowlist**: cleartext/pins/CAs only [P: S14]; WebView honors cleartext for apps targeting O+ [P: S8] |
| `shouldOverrideUrlLoading`, `onCreateWindow` | app | Good for navigation, not subresources |
| `shouldInterceptRequest` | app | **Leaky by design**: only the initial URL (not redirects), not blob:/javascript:/asset URLs [P: S1] |
| `ProxyController` to a local filtering proxy | app | Sees all requests incl. redirects; fails closed only if no `DIRECT` fallback is configured and implicit bypass rules are removed [S: S21; I] |
| No INTERNET permission | OS (eBPF) | Hard: socket creation denied [P: S3] |
| Strict Private DNS to Zune resolver | OS | Fails closed, no clear-text fallback [S: S17]; WebView sets DoH off and can use platform DNS [P: S8]; IP literals bypass |
| Chromium-level allowlist patch | provider | Strongest for web content; rebase cost [I] |

**F5. Intent plane.** AOSP's Intent Firewall evaluates XML rules (`scheme`, `host`, `action`, `sender-package`) in `ActivityStarter` for every activity start, including intent-redirect checks [P: S1]. It reads only `/data/system/ifw`, so a tiny patch to also read a verified `/system_ext/etc/ifw` makes it tamper-proof [I]. `cmd package query-activities` and `resolve-activity` support a CI gate [P: S1].

**F6. Network plane.** INTERNET is enforced in-kernel by eBPF per app ID [P: S3]. `ConnectivityManager` offers per-UID firewall chains (`OEM_DENY_1..3`; module-library API gated by `NETWORK_SETTINGS`), per-UID not per-destination [P: S3]. Always-on VPN lockdown (`setAlwaysOnVpnPackageForUser`, `CONTROL_ALWAYS_ON_VPN`) is the only built-in per-destination path, but it leaks: a code comment admits one, and GrapheneOS fixed DNS-race, multicast and `SO_BINDTODEVICE` leaks yet still calls it incomplete [P: S1, S3, S11]. Apps targeting API 37 use ECH when supported, which blinds SNI inspection (`<domainEncryption>` in NSC tunes it) [P: S13]. WebView supports QUIC, so a TCP-only filter is blind [P: S8]. GrapheneOS's Network permission adds a second layer that also blocks indirect use through OS APIs, so bare INTERNET is not airtight [P: S11].

**F7. Policy plane.** `UserManager` offers every restriction we need: install apps and unknown sources, debugging, factory reset, private DNS, VPN, credentials, tethering, add user/guest/private profile, safe boot, USB file transfer, physical media, Bluetooth sharing, NFC [P: S1]. Caveats: `UserManager.setUserRestriction` is deprecated in favor of DPM; `config_user_types.xml` defaults apply only at user creation; `fw.max_users` can be baked [P: S1]. **`DISALLOW_FACTORY_RESET` also clears the OEM-unlock bit and makes `setOemUnlockAllowedByUser` throw** [P: S1]. Android 17's supervision framework adds flag-gated per-package block/time-limit policies; the only user restriction it sets itself is `DISALLOW_FACTORY_RESET`; it enforces no web or network rule [P: S1]. Lock task mode is a launchable-package allowlist, better suited to kiosks than phones [P: S16]. AOSP 17's Advanced Protection hooks (unknown-sources ban, USB data off when locked, 2G off, MTE) could be enabled by a system app [P: S1; use I].

**F8. Boot chain.** On locked, non-debuggable builds `adbd` requires authorization; on unlocked or debuggable builds it follows `ro.adb.secure`, which defaults to false, so set it explicitly [P: S6]. AOSP 17 `adbd` also has a **trade-in mode** (`persist.adb.tradeinmode`, flag-gated) that disables auth in its evaluation state; keep the flag off and the property unset [P: S6]. GrapheneOS: production is `user` builds, its setup wizard disables OEM unlocking at the end of setup, and its Auditor does hardware attestation [P: S9, S11]. On Pixel, a locked bootloader with a custom AVB key rejects stock firmware (docs 02). Public BROM tools read/write flash on many MediaTek SoCs regardless of lock state [P: S20], so SoC choice bounds this layer.

**F9. Field evidence.** Real kid-control bypasses are "hidden browser" bugs: a Family Link bypass via a hidden browser in Play Services reached through a contact's website field, and links in always-allowed apps [S: S19]. Kiosk-breakout practice adds help/legal links, embedded browser elements, NFC tags launching Settings, Bluetooth/USB keyboards, USB Ethernet dongles, safe mode and fastboot [P: S15]. Treat every first-party link, WebView and exported activity as hostile.

## Threat model: bypass-vector table

Likelihood: chance a determined 10-14-year-old tries it and it works against unhardened AOSP. Where: **I** image, **P** policy, **N** network, **S** server.

| # | Vector | Likelihood | Mitigation | Residual | Where |
|---|---|---|---|---|---|
| 1 | `ACTION_VIEW`/`WEB_SEARCH` on http(s)/ftp from any link | High | No handler (CI gate), baked IFW block, no `Linkify`, no link previews | Low (an update adds a filter; CI catches) | I |
| 2 | Custom Tabs / TWA providers | Low | No `CustomTabsService`; drop `android-browser-helper` | Very low | I |
| 3 | System WebView hosts: CaptivePortalLogin, OsuLogin, HTMLViewer, CarrierDefaultApp | Medium | Remove from product; WebView caller allowlist; `captive_portal_mode=0` | Low | I |
| 4 | Captive-portal Wi-Fi (hotel, school) | Medium | Detection off, probe URLs to Zune; portals unsupported in v1 | Usability loss | I, N |
| 5 | Help/legal/licence links (Settings, Dialer, SetupWizard) | Medium | Minimal Zune Settings; plain-text licences; IFW | Low | I |
| 6 | Links in SMS/MMS/CB/messenger | High | SMS unreadable (D6); plain-text rendering, no auto-link | Low | I |
| 7 | Videos WebView (YouTube logo, title, end cards, "watch on YouTube") | High | Own page + one iframe, `rel=0`, `fs=0`, custom controls, touch shield, no new windows or navigation, proxy/allowlist; Chromium patch Stage 2 | **Medium**: YouTube UI is third-party code | I, N |
| 8 | EPUB external links, embedded JS, remote resources | Medium | No INTERNET (GrapheneOS PdfViewer declares none [P: S12]), JS off, links dropped | Very low | I |
| 9 | AI assistant as web gateway | High | No browse tools, strip URLs, server filters | **Web-derived content still reaches the child** | S |
| 10 | Camera QR to URL; text-selection "web search" | Low | No barcode feature; drop `PROCESS_TEXT` web handlers | Low | I |
| 11 | Sideload via installer UI, unknown sources, `adb install` | Medium | `INSTALL_APPS` + `..._UNKNOWN_SOURCES_GLOBALLY`; no `REQUEST_INSTALL_PACKAGES` holders; only Zune Updater installs | Low | I, P |
| 12 | USB OTG storage, MTP, USB keyboard or Ethernet dongle | Medium | `USB_FILE_TRANSFER`, `MOUNT_PHYSICAL_MEDIA`, omit USB-host feature | Low | I, P |
| 13 | Bluetooth OPP/keyboard force-pair, NFC tag AAR/URL | Low-Med | `BLUETOOTH_SHARING`; NFC omitted or restricted; monthly BT patches | Low | I, P |
| 14 | ADB, Developer options, trade-in mode | High | `user` build, `ro.adb.secure=1`, Developer options stripped, trade-in flag off | Low | I |
| 15 | OEM unlock, fastboot flash, stock reflash | High | OEM-unlock bit forced off; locked bootloader + Zune AVB key | Low on Pixel; **higher on BROM-exploitable SoCs** | I |
| 16 | Recovery factory reset (buttons) | High | Cannot block. Device inert until re-paired; backend alert | Parent policy lost until re-pair; **no browser gained** | I, S |
| 17 | Safe mode | Medium | `SAFE_BOOT`; Zune apps are system apps | Low | I, P |
| 18 | DNS/DoH/Private DNS change | Low-Med | Strict Private DNS pinned; `CONFIG_PRIVATE_DNS`; WebView DoH off | IP literals (gated by #7 controls) | P, N |
| 19 | VPN apps, user CA install | Low | `CONFIG_VPN`, `CONFIG_CREDENTIALS`, no CertInstaller | Low | I, P |
| 20 | Hotspot/tether, alternate SIM or Wi-Fi | Medium | `CONFIG_TETHERING`; policy is per-app, so network source is irrelevant | Low | I, P |
| 21 | Other users, guest, Private Space, clone/work profile | Medium | `fw.max_users=1`, disable user types, `ADD_*` restrictions | Low | I |
| 22 | Remote-control/VNC apps, share sheet, Cast | Low | Not installable; no web targets; remote-display module omitted | Very low | I |
| 23 | Reflashed or rooted device, parent-assisted unlock | Low-Med | Server attestation of verified-boot key; sell locked devices | **Beyond image control** | S |

## Options & trade-offs

**WebView strategy**

| Option | Pro | Con | Verdict |
|---|---|---|---|
| A. No WebView | Zero engine surface | Breaks Readium-style EPUB and YouTube IFrame (the native Player SDK is deprecated [S: S18]) and any system app touching WebView | Only if Videos goes native/licensed |
| B. Provider + app-level limits only | Cheapest | `shouldInterceptRequest` leaks (F4) | Reject as sole control |
| **C. Provider + system_server gate + no-INTERNET EPUB + proxied Videos** | Small patches; closes hidden WebViews | Still ships Chromium; patch burden | **Stage 1** |
| D. C plus Chromium allowlist fork | Native-code origin gate | Patches on Chromium's cadence | Stage 2 if needed |

Provider source: Vanadium prebuilt (GPL-2.0 obligations, hardened) or own Chromium build (LineageOS publishes its GN args [P: S10]). Either way we own a Chromium update pipeline.

**Network strategy**

| Option | Pro | Con | Verdict |
|---|---|---|---|
| DNS allowlist only | Easy | IP literals, ECH/HTTPS-RR, broad `googlevideo.com` | Layer, not control |
| Per-UID INTERNET + firewall chains | Kernel-enforced | Per-app only | **Stage 1 base** |
| Always-on lockdown VPN ("Zune Guard") | Domain/SNI/QUIC control | Battery, perf, AOSP leaks | **Stage 2** |
| Server gateway (WireGuard to Zune) | Central enforcement | Holds only if device is forced onto it | Pair with Guard |

Embedded YouTube needs `youtube.com`, `youtube-nocookie.com`, `google.com`, `ytimg.com`, `googlevideo.com`, `gstatic.com` and more [S: S22], so a network allowlist is a coarse perimeter. The fine gate is the WebView page: one iframe, no URL entry.

## Recommended design for Zune

**Compile into the image (tamper-proof, survives reset):**
1. Product composed from `base_*`; exclude `Browser2`, `QuickSearchBox`, `CaptivePortalLogin`, `CarrierDefaultApp`, `HTMLViewer`, `BookmarkProvider`, `PrintSpooler`, `CertInstaller`, `PrivateSpace`, `Traceur`, and AOSP Settings as child UI; keep `PackageInstaller` only if restrictions neutralise it. `config_defaultBrowser` empty; Zune holds the assistant role.
2. Patches (target under 5): WebView caller allowlist; IFW verified directory; system-asserted restriction set that reset or API drift cannot lift; Settings without Developer options.
3. Config: `user` variant, `ro.adb.secure=1`, `fw.max_users=1`, `fw.show_multiuserui=0`, profile user types disabled, `captive_portal_mode=0`, `config_captive_portal_*_url` set to Zune endpoints [P: S5], strict Private DNS default, per-package INTERNET allowlist via privapp-permissions, WebView provider whitelist, NSC with ECH off for Zune apps.
4. SELinux: dedicated domains for the WebView hosts and `neverallow` assertions that only INTERNET-allowlisted domains create inet sockets [I].
5. Verified boot with Zune AVB key; OEM unlock off at setup; Zune setup wizard demands a parent pairing code (activation lock).
6. **CI gates every build:** (a) on Cuttlefish, `cmd package query-activities` for `VIEW` with http, https, ftp, `intent:`, `WEB_SEARCH`, `text/html` returns nothing; (b) scan all partitions and apexes for `android.webkit.WebView` references and INTERNET holders, which must equal the allowlists; (c) exported-activity diff against the previous build.

**Deliver as policy (mutable per child):** Zune Guard (platform-signed, started every boot) applies and re-asserts restrictions, watches `adb_enabled`, `development_settings_enabled`, `private_dns_*`, `captive_portal_mode`; delivers signed allowlists (video IDs, domains) verified with a key baked into the image; enforces time limits via supervision `PackageUsagePolicy`; reports key attestation. Prefer Device Owner provisioning from our setup wizard to the deprecated `UserManager` call [I]; validate on Cuttlefish.

**Stage 1 (ship):** the above, INTERNET allowlist, strict Private DNS, Videos proxy. **Stage 2:** Guard lockdown VPN, Chromium allowlist patch, a logging "sink" activity so parents see attempted links, Advanced Protection hardening.

## What we can and cannot claim

Physical access bounds everything: parent-assisted unlock, retail-unlocked devices, SoC-level flashing and recovery wipes cannot be fully stopped. A wipe yields an inert device, not a browser. Safe: "no browser app, no way to open or type a web address, the device talks only to Zune-approved services", backed by attestation and pre-flashed locked devices. Unsafe: "no internet", "no web access" (AI and YouTube content are web-derived), "cannot be bypassed", or any claim for image-only installs.

## Risks & unknowns

- Chromium/WebView is the largest attack surface and cadence burden; GPL-2.0 patch obligations need legal review.
- YouTube's embedded UI (links we cannot remove) caps Videos containment at medium.
- ECH, QUIC and HTTPS-RR erode DNS/SNI enforcement; AOSP VPN lockdown leaks.
- Unverified here: `DISALLOW_INSTALL_APPS` effect on our own Updater; CaptivePortalLogin source (googlesource blocked, search summary only [S]); supervision profile-owner behavior; Pixel recovery wipe under a custom AVB key; WebView use in Pixel vendor/product blobs (CI scan covers it).
- Removing apps from Mainline modules (OsuLogin in Wi-Fi) needs build patches; the WebView gate is the fallback.
- Non-Pixel ODM hardware weakens the boot chain. Retest emergency calling and carrier flows after removing CarrierDefaultApp.

## Decisions needed from the founder

1. **Sales model:** pre-flashed relocked devices only (recommended) or also image-only (weaker claim).
2. **Videos architecture:** accept a network-limited YouTube WebView in Stage 1; explore licensed/native video to remove it later.
3. **WebView supply:** Vanadium prebuilt vs own Chromium; commit to an update SLA at Chromium cadence.
4. **Captive-portal Wi-Fi (hotel, school) unsupported in v1:** accept?
5. **Marketing wording** per "What we can and cannot claim".
6. **Reset behavior:** accept that a recovery wipe leaves an inert device until a parent re-pairs.
7. **Hardware gate:** proof of SoC-level flash lock before approving any non-Pixel device.

## Load-bearing claims

| # | Claim | Evidence | Basis |
|---|---|---|---|
| 1 | CarrierDefaultApp ships a disabled `VIEW http/https host=*` alias that carrier signals enable, hosting a JS WebView | S1 `packages/CarrierDefaultApp/AndroidManifest.xml`, `CarrierActionUtils.java` | P |
| 2 | WebView requests pass through `WebViewUpdateService.waitForAndGetProvider()` in system_server with the caller UID, so a caller allowlist is feasible | S1 `WebViewFactory.java:447-458`, `WebViewUpdateService.java:205-225` | P (feasibility I) |
| 3 | `shouldInterceptRequest` skips redirects, blob:, javascript:, assets; NSC has no allowlist | S1 `WebViewClient.java:212-218`; S14 | P |
| 4 | INTERNET is denied at socket creation by eBPF `cgroupsock/inet_create` | S3 `bpf/progs/netd.c:1180-1226` | P |
| 5 | `IntentFirewall` filters scheme/host/sender in `ActivityStarter` but reads only `/data/system/ifw` | S1 `IntentFirewall.java`, `ActivityStarter.java:1337` | P |
| 6 | `DISALLOW_FACTORY_RESET` clears the OEM-unlock bit and blocks `setOemUnlockAllowedByUser` | S1 `OemLockService.java` | P |
| 7 | AOSP 17 offers no WebView implementation; Vanadium and LineageOS use Chromium 154.0.8037.x | S9, S10, S23 | P (absence I) |
| 8 | Always-on lockdown VPN is permission-gated and has known leaks | S1 `VpnManager.java:595`; S3 `netd.c:1530`; S11 | P |

## Sources

S1 GrapheneOS/platform_frameworks_base `17` (WebViewFactory, WebViewUpdateService, WebViewClient, IntentFirewall, ActivityStarter, OemLockService, UserManager, config_user_types.xml, config_webview_packages.xml, SupervisionService, VpnManager, advancedprotection, packages/CarrierDefaultApp). S2 GrapheneOS/platform_build `17` `target/product/*.mk`. S3 GrapheneOS/platform_packages_modules_Connectivity `17` (`bpf/progs/netd.c`, `ConnectivityManager.java`); S4 GrapheneOS/platform_packages_modules_Wifi `17` `OsuLogin/`. S5 ..._NetworkStack `17` `res/values/config.xml`. S6 ..._adb `17` `daemon/main.cpp`, `tradeinmode.cpp`. S7 aosp-mirror/platform_packages_apps_htmlviewer. S8 chromium/chromium `android_webview/browser/aw_content_browser_client.cc`, `aw_browser_context.cc`. S9 GrapheneOS/Vanadium (README, LICENSE, args.gn) and grapheneos.org `static/build.html`. S10 LineageOS/android_external_chromium-webview_patches README. S11 grapheneos.org `static/features.html`. S12 GrapheneOS/PdfViewer manifest. S13 developer.android.com/about/versions/17/behavior-changes-17. S14 developer.android.com/privacy-and-security/security-config. S15 github.com/ikarus23/kiosk-mode-breakout. S16 developer.android.com/work/dpc/dedicated-devices/lock-task-mode. S17 android-developers.googleblog.com/2018/04/dns-over-tls-support-in-android-p.html. S18 developers.google.com/youtube/android. S19 androidpolice.com/exploit-bypass-android-parental-controls-web-browsing (search summary only). S20 github.com/bkerler/mtkclient. S21 developer.android.com/reference/androidx/webkit/ProxyController. S22 YouTube domain lists via SonicWall/Meraki KBs (search summary). S23 AOSP project list via LineageOS/android `lineage-24.0` and GrapheneOS/platform_manifest `17` `default.xml`. Internal: `docs/REQUIREMENTS.md`, `docs/research/01`, `02`.
