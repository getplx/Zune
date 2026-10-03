#!/usr/bin/env bash
# Zune pre-check (01 PRE-01, PRE-02, PRE-08). Exit non-zero on any hard failure.
# Usage: os/tools/pre-check.sh [--host]   (--host also enforces build-host sizing)
set -u
fail=0; host=0; [ "${1:-}" = "--host" ] && host=1
ok(){ printf 'PASS  %s\n' "$1"; }; bad(){ printf 'FAIL  %s\n' "$1"; fail=1; }

# PRE-01: AOSP reachability
n=$(git ls-remote https://android.googlesource.com/platform/manifest 2>/dev/null | head -3 | wc -l)
[ "$n" -ge 3 ] && ok "android.googlesource.com manifest ($n refs)" || bad "android.googlesource.com manifest"
for u in https://source.android.com https://dl.google.com https://developers.google.com; do
  curl -sSfIL --max-time 20 "$u" >/dev/null 2>&1 && ok "$u" || bad "$u"
done

# PRE-02: build host sizing (only meaningful on the build host)
if [ "$host" = 1 ]; then
  cpu=$(nproc 2>/dev/null || sysctl -n hw.ncpu); mem=$(awk '/MemTotal/{print int($2/1048576)}' /proc/meminfo 2>/dev/null)
  [ "${cpu:-0}" -ge 32 ] && ok "vCPU $cpu" || bad "vCPU ${cpu:-?} (<32)"
  [ "${mem:-0}" -ge 128 ] && ok "RAM ${mem} GB" || bad "RAM ${mem:-?} GB (<128)"
  [ -r /dev/kvm ] && [ -w /dev/kvm ] && ok "/dev/kvm rw" || bad "/dev/kvm not rw"
  free=$(df -k --output=avail . | tail -1); [ "$free" -ge 900000000 ] && ok "disk >= ~1 TB free" || bad "disk < 1 TB free"
else
  printf 'SKIP  PRE-02 host sizing (run with --host on the build host)\n'
fi

# PRE-08: secret scan (private keys / API-key patterns in tracked files)
root=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
if git -C "$root" grep -InE -e '-----BEGIN [A-Z ]*PRIVATE KEY-----' -e 'sk-[A-Za-z0-9]{32,}' -e 'AKIA[0-9A-Z]{16}' -- . ':!os/tools/pre-check.sh' >/dev/null 2>&1; then
  bad "secret scan found key-like material"; else ok "secret scan clean"; fi
exit $fail
