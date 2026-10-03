#!/usr/bin/env bash
# Zune M1 baseline on the build host (01 §4.1, PRE-02, PRE-10). Ubuntu 24.04 x86_64 ONLY.
# Usage: bootstrap-build-host.sh [workdir]   default workdir: $HOME/aosp
# Records wall time, disk use and ro.build.id in $WORK/m1-baseline.log for the M1 re-baseline (PRE-16).
set -euo pipefail
TAG="${AOSP_TAG:-android-17.0.0_r1}"   # pinned, never a floating branch (PRE-10)
WORK="${1:-$HOME/aosp}"
LUNCH="aosp_cf_x86_64_only_phone-aosp_current-userdebug"

[ "$(uname -s)-$(uname -m)" = "Linux-x86_64" ] || { echo "Linux x86_64 required"; exit 1; }
. /etc/os-release; [ "$VERSION_ID" = "24.04" ] || echo "WARN: not Ubuntu 24.04 (Verify-first 5)"
"$(dirname "$0")/pre-check.sh" --host

sudo apt-get update
sudo apt-get install -y git-core gnupg flex bison build-essential zip curl zlib1g-dev \
  libc6-dev-i386 x11proto-core-dev libx11-dev lib32z1-dev libgl1-mesa-dev libxml2-utils \
  xsltproc unzip fontconfig python3 rsync libncurses-dev bc ccache
mkdir -p "$HOME/.bin"; curl -sSf https://storage.googleapis.com/git-repo-downloads/repo -o "$HOME/.bin/repo"
chmod +x "$HOME/.bin/repo"; export PATH="$HOME/.bin:$PATH"

mkdir -p "$WORK"; cd "$WORK"; t0=$(date +%s)
repo init -u https://android.googlesource.com/platform/manifest -b "refs/tags/$TAG" \
  --partial-clone --clone-filter=blob:limit=10M --no-clone-bundle
repo sync -c -j8 --no-tags
t1=$(date +%s)
set +u; source build/envsetup.sh; set -u
lunch "$LUNCH"; m -j"$(nproc)"
t2=$(date +%s)
{ echo "tag=$TAG"; echo "sync_s=$((t1-t0))"; echo "build_s=$((t2-t1))"; du -sh "$WORK" | sed 's/^/disk=/'
  grep -r RELEASE_PLATFORM_SECURITY_PATCH build/release/flag_values 2>/dev/null | head -3
  repo manifest -r | grep -m1 'name="platform/manifest"' || true; } | tee "$WORK/m1-baseline.log"
echo "Next: launch_cvd, then 'adb shell getprop ro.build.id' (expect CP2A.260605.016 [verify]); record in docs/verified-facts.md rows 1, 5."
