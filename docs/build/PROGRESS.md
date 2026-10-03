# Zune build progress (append-only)

## 2026-10-03: Z0 start
- PRE-01 PASS from the founder's Mac: `git ls-remote` on android.googlesource.com/platform/manifest returns refs; source.android.com, dl.google.com, developers.google.com reachable. Re-run on the build host.
- Branch `build/m0-foundation` created off `research/android-kids-foundation`; 01 §4.3 skeleton created; `os/tools/pre-check.sh` added (PRE-01, PRE-08; PRE-02 with `--host`).
- `docs/gates.md` and `docs/verified-facts.md` created from 01's register and Verify-first table.
- Not done (needs founder or a build host): build host (PRE-02), Pixel dev units (PRE-04), cloud/GitHub accounts (§4.2), spend approval (B-1).
- Note: `ZUNE_BUILD_SPEC_FULL.md` contains `99-consistency-log.md` twice; the section file has one copy.

## 2026-10-03: AOSP download requested
- Founder asked to download AOSP and start building. The founder's Mac (macOS arm64, 16 GB RAM, ~13 GB free) cannot hold or build AOSP; no sync was started. Blocked on B-1: a Linux x86_64 build host (PRE-02).
- Added `os/tools/bootstrap-build-host.sh` (pins `android-17.0.0_r1`, partial-clone sync, baseline `aosp_cf_x86_64_only_phone-aosp_current-userdebug`, writes timings to `m1-baseline.log`). Syntax-checked only; not run.

## 2026-10-03: build order (founder)
- Founder: build the phone product first (OS image, then on-device apps), then the management portal. Backend/portal skeletons are deferred behind the phone track, except what the device channel needs.
- Toolchain installed on the founder's Mac: Go 1.27.1, Node 26.10.0, `repo` 2.65 (~/.bin). Mac has ~12 GB free, so it is for editing and Gradle app work only; AOSP sync/build waits for the Linux build host (B-1).

## 2026-10-03: AWS account guardrails
- AWS account 193793988127 (new, no free tier), CLI logged in as root via `aws login`, default region ap-south-1. Move to an IAM admin user/role and lock root with MFA before anything real runs (01 PRE-06).
- Budget `zune-monthly-50usd` created (us-east-1 API): USD 50/month, credits excluded so it tracks gross usage; email alerts to abhishek@getplex.in at 25/50/80/100% actual and 100% forecast. Definition in `backend/infra/aws/`. A budget alerts; it does not hard-stop spend. Stop/deny budget action still to add once an instance exists.
- EC2 Standard on-demand vCPU quota in ap-south-1 is 5; increase to 32 requested (build host needs 32 vCPU / 128 GB, PRE-02).
- Cost note: a permanent 1-2 TB EBS disk exceeds USD 50/month alone; plan is start-on-demand instance plus source kept as a snapshot.

## 2026-10-03: on-demand AWS build host
- Decision (founder): Mumbai (ap-south-1), on-demand `m6a.8xlarge`, started only for build/test sessions; est. USD 33/month at 20 h, 52 at 40 h incl. ~USD 15 fixed (150 GB persistent source volume + S3 ccache). m8i.8xlarge only for a KVM/Cuttlefish trial.
- Added `os/tools/aws-build-session.sh` (init, init-volume, up, ssh, status, down). Terminate-on-shutdown, 4 h hard max runtime, 15 min idle shutdown. `init` run (SSH key pair `zune-build`, SG `zune-build-ssh`; both free; key at ~/.ssh, not in repo). Dry-run launch passed. Source volume NOT created yet (billing starts then). S3 ccache not wired (needs an instance profile).
- EC2 Standard vCPU quota is now 16; the increase to 32 is under AWS review (case opened). `m6a.8xlarge` needs 32 vCPU, so the full-size host cannot launch yet; `m6a.4xlarge` (16 vCPU, 64 GB) would fit.

## 2026-10-03: milestone naming (founder)
- Milestones renamed Z0-Z8 (was M0-M8; `Mn` -> `Zn`) across docs/build, gates, verified-facts and tooling. `docs/research/*` and `docs/investor/*` are unchanged and still use M<n> (R21's M<n> means months, kept as such in 01). Git branch `build/m0-foundation` keeps its name.

## 2026-10-03: AOSP synced on AWS build host
- `android-17.0.0_r1` synced (partial clone, depth 1): 1,084 projects, 139 GB on disk (105 GB files + 34 GB .repo). First attempt filled the 150 GB volume; grew to 250, then replaced with a 200 GB volume (rsync copy verified identical, old volume deleted). Source volume `zune-aosp-src` is 200 GB (about USD 18/month); `aws-build-session.sh` default SRC_GB is now 200.
- Build host for now: m6a.4xlarge (16 vCPU / 64 GB) because the vCPU quota is 16 until the 32 request (case open) is approved.
- Verify-first rows 1 and 4 pass at source level; row 5 partial (see docs/verified-facts.md). Browser2, CaptivePortalLogin, HTMLViewer confirmed in stock product makefiles.
