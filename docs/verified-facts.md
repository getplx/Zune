# Verified facts (01 Verify-first rows; add rows from sections 02-12)

| # | Claim | Command | Output | Date | Outcome |
|---|---|---|---|---|---|
| PRE-01 | AOSP hosts reachable | `os/tools/pre-check.sh` | 3 refs; 3 hosts 2xx/3xx | 2026-10-03 | PASS (founder's Mac; repeat on build host) |
| 1 | `android-17.0.0_r1` is CP2A.260605.016, SPL 2026-06-05 | | | | open |
| 2 | `android17-security-release` / `android-security-17.*` branches exist | | | | open |
| 3 | Google Pixel image/driver licence allows company flashing and OTA redistribution | | | | open (needs reading + counsel) |
| 4 | Supervision framework and `config_systemSupervision` are in AOSP itself | | | | open |
| 5 | Ubuntu 24.04 builds Android 17; `aosp_cf_x86_64_only_phone-aosp_current-userdebug` valid; /dev/kvm | | | | open (needs build host) |
| 6 | Monorepo at `<aosp>/zune` with linkfiles and `.find-ignore` works with Soong | | | | open (M1 spike) |
| 7 | Vanadium prebuilt obtainable, redistributable, accepted as WebView provider | | | | open |
| 8-16 | See 01 Verify-first | | | | open |
