# Starter prompt for conversation 2

Paste everything inside the box as your first message in the new chat. Before you do, create the new
session on an environment whose Network access allows `android.googlesource.com`,
`source.android.com`, `dl.google.com` and `developers.google.com`, and attach the repo `getplx/Zune`.

````
I'm continuing the "Zune" project: a custom, kids-only, browser-less AOSP (Android 17) OS image
plus a browser-based parent portal. A previous conversation did the research phase in a container
that could NOT reach AOSP; this container should be able to.

1. Repo: getplx/Zune, branch research/android-kids-foundation. Read docs/HANDOFF.md first, then
   docs/REQUIREMENTS.md (my authoritative decisions, D1-D18), then the reports in docs/research/.
2. Before anything else, check AOSP access:
   git ls-remote https://android.googlesource.com/platform/manifest | head -3
   If it is blocked, stop and tell me exactly which host is denied.
3. Then follow "Next steps" in docs/HANDOFF.md. The reusable research script is
   docs/handoff/research-workflow.js. I explicitly opt in to multi-agent workflows ("use a
   workflow") for running it, in modes research / verify / reconcile / critic.
4. First priority: re-verify the AOSP-dependent claims (HANDOFF section 6) against the real
   android-17.0.0_r1 tree and finish any research topics that are missing or unverified.
5. Ask me ONE question at a time. Commit and push to a branch is fine; do not open a pull request
   unless I ask. No model names in commits; use the trailer
   "Co-Authored-By: Claude <noreply@anthropic.com>".
````
