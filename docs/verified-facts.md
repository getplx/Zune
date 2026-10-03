# Verified facts (01 Verify-first rows; add rows from sections 02-12)

| # | Claim | Command | Output | Date | Outcome |
|---|---|---|---|---|---|
| PRE-01 | AOSP hosts reachable | `os/tools/pre-check.sh` | 3 refs; 3 hosts 2xx/3xx | 2026-10-03 | PASS (founder's Mac; repeat on build host) |
| 1 | `android-17.0.0_r1` is CP2A.260605.016, SPL 2026-06-05 | grep `BUILD_ID` in build/make/core/build_id.mk; `build/release/flag_values/cp2a/RELEASE_PLATFORM_SECURITY_PATCH.textproto` | BUILD_ID=CP2A.260605.016; string_value "2026-06-05" | 2026-10-03 | PASS (source). Runtime `ro.build.id` still to confirm on Cuttlefish |
| 2 | `android17-security-release` / `android-security-17.*` branches exist | | | | open |
| 3 | Google Pixel image/driver licence allows company flashing and OTA redistribution | | | | open (needs reading + counsel) |
| 4 | Supervision framework and `config_systemSupervision` are in AOSP itself; stock makefiles list Browser2, CaptivePortalLogin, HTMLViewer | grep frameworks/base and build/make/target/product/*.mk | `services/supervision/.../SupervisionService.java` exists; `config_systemSupervision` in core/res/res/values/config.xml; Browser2 in handheld_product.mk:25, CaptivePortalLogin in handheld_system.mk:46, HTMLViewer in media_system.mk:32 | 2026-10-03 | PASS (source). Overlay behaviour and `cmd role` still to test on Cuttlefish |
| 5 | Ubuntu 24.04 builds Android 17; `aosp_cf_x86_64_only_phone-aosp_current-userdebug` valid; /dev/kvm | `ls device/google/cuttlefish/AndroidProducts.mk`; lunch + m | target `aosp_cf_x86_64_only_phone` listed in AndroidProducts.mk; sync of 1,084 projects = 139 GB on Ubuntu 24.04 m6a.4xlarge | 2026-10-03 | PARTIAL: target exists; `aosp_current` lunch, build and KVM still open |
| 6 | Monorepo at `<aosp>/zune` with linkfiles and `.find-ignore` works with Soong | | | | open (Z1 spike) |
| 7 | Vanadium prebuilt obtainable, redistributable, accepted as WebView provider | | | | open |
| 8-16 | See 01 Verify-first | | | | open |
