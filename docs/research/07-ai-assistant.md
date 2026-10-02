# Zune research 07: Kid-safe AI assistant (architecture, models, safety, policy)

2026-10-02. Tags: **[P]** read in a primary source this session, **[S]** secondary or search summary (page blocked/unread), **[I]** engineering judgement, **[M]** memory, unchecked. The search budget ran out and egress blocked openai.com, ai.google.dev, ftc.gov, law-firm sites and arXiv, so OpenAI, Google, Mistral and most regulatory items are **[S]** and need counsel or a re-read before they bind a decision.

## 1. Summary & recommendation

1. **Stage 1 is a cloud assistant behind a Zune AI Gateway** (Go, same backend as report 05). Main model **Claude Sonnet 5.5**, guards on **Claude Haiku 4.5**, under a **zero-data-retention (ZDR)** arrangement, US-pinned. Anthropic allows API products for minors with age gating, moderation, monitoring, AI disclosure and COPPA compliance [P], but does not spell out under-13 products, so **written confirmation from Anthropic is the first go/no-go gate**.
2. **Gemini API is out** (terms bar API clients "directed towards or likely to be accessed by" under-18s) [S]. OpenAI is a viable backup but needs ZDR before any under-13 personal data [S]. Self-hosted Apache-2.0 open weights (Qwen3, gpt-oss) are the Stage 2-3 path, guard classifiers first.
3. **Voice runs on-device from day one** (push-to-talk, STT via sherpa-onnx/Moonshine/Whisper, TTS via sherpa-onnx Kokoro/Matcha). AOSP ships no usable speech stack, and cloud TTS would cost more than the LLM [I].
4. **On-device LLM is a Stage 2 offline fallback only**, on 8 GB+ devices, answering from local curated packs, not open chat. Gemini Nano/AICore is unavailable without Google components [S].
5. **Product shape: a tutor, not a companion.** Four modes (Ask Why, Homework Helper, Story Maker, Look at This), three age bands, hard time budgets, no memory of personal facts, no persona that says "friend", no web, no image generation, no side-effect tools.
6. **Safety is layered and eval-gated**: scripted responses for self-harm/abuse/grooming, tiered parent alerts, a kid red-team suite that blocks releases, a kill switch, a human Trust & Safety queue.
7. **COGS** about **$1.4 per typical child per month** (240 turns), $0.6 light, $3.6 heavy [I from P prices]. Price AI into the subscription; cap turns per day.

## 2. Findings

**F1. Anthropic terms [P].** Guidelines (updated 2026-03-16): products letting minors interact directly with the API "should implement" age verification, moderation/filtering, monitoring and reporting, safe-use education; "must disclose" the user is talking to an AI; state COPPA compliance on the website; Anthropic "may provide a child-safety system prompt", "will periodically audit" and may suspend after a high violation rate. https://support.claude.com/en/articles/9307344-responsible-use-of-anthropic-s-models-guidelines-for-organizations-serving-minors . Usage Policy (eff. 2025-09-15): minor = under 18; grooming/sexualization barred even in fiction https://www.anthropic.com/legal/aup . Child-safety guidance (2026-06-26): detect uploads; US platforms with actual knowledge of apparent CSAM must report to NCMEC https://support.claude.com/en/articles/15591275-child-safety-guidance-for-developers . Commercial Terms (page dated 2025-06-17): no explicit minors clause; no training on Customer Content https://www.anthropic.com/legal/commercial-terms .

**F2. ZDR [P].** Available on request via sales, per organization. Eligible: Messages API, prompt caching, citations, search results, data-residency, structured outputs (qualified). Not eligible: Files API, Batch, code execution, Managed Agents. Fable/Mythos models need 30-day retention. **Flagged content may be kept up to 2 years even under ZDR**, which our privacy notice must disclose. https://platform.claude.com/docs/en/manage-claude/api-and-data-retention

**F3. Other vendors [S].**

| Vendor | What we found | Verdict |
|---|---|---|
| OpenAI | Under-18 guidance: disclosures, content filters, monitoring/escalation; no personal data of under-13s without ZDR first (needs OpenAI approval) https://developers.openai.com/api/docs/guides/safety-checks/under-18-api-guidance | Allowed with safeguards; backup |
| Google Gemini API | Must be 18+; no use in an API Client "directed towards or likely to be accessed by individuals under the age of 18" https://ai.google.dev/gemini-api/terms ; Vertex AI coverage unverified | **No-go** without a written exception |
| Mistral | Consumer terms 13+, no under-13 personal data, API business-only from 2026-08-05 https://help.mistral.ai/en/articles/347631-can-children-use-mistral-products-and-services | Unverified |
| Self-hosted | Qwen3 Apache 2.0 [P] https://raw.githubusercontent.com/QwenLM/Qwen3/main/README.md ; gpt-oss-safeguard Apache 2.0 [P] https://raw.githubusercontent.com/openai/gpt-oss-safeguard/main/README.md ; Llama Guard under Llama licences [P]; Gemma 4 licence unread | Stage 2-3 |

**F4. Prices [P]** https://platform.claude.com/docs/en/about-claude/pricing : Sonnet 5.5 $2 in / $10 out per MTok, cache read $0.20; Haiku 4.5 $1 / $5, cache read $0.10; `inference_geo:"us"` costs 1.1x and exists only on Claude 4.6+ (Haiku 4.5 cannot be geo-pinned on the first-party API); Bedrock regional endpoints +10%.

**F5. On-device LLM [P unless noted].**
- LiteRT-LM (Apache 2.0): stable Kotlin Android API on Google Maven, GPU via OpenCL, NPU via bundled libs, no Play Services dependency; Gallery APK offered "for users without Google Play". https://raw.githubusercontent.com/google-ai-edge/LiteRT-LM/main/README.md ; https://raw.githubusercontent.com/google-ai-edge/gallery/main/README.md
- Google's allowlist (google-ai-edge/gallery@main:model_allowlists/1_0_19.json, 2026-10-01): Gemma-4-E2B 2.6 GB, **min device RAM 8 GB**; E4B 3.7 GB, **12 GB**; Gemma3-1B 0.6 GB, 6 GB.
- Speed: E2B about 52 tok/s on a Galaxy S26 Ultra GPU, 2-5 tok/s on mid-range CPU [S] https://dev.to/samdude/gemma-4-on-android-tricks-for-faster-on-device-inference-3kj5 ; Llama-3.2-3B 10-28 tok/s on 8 Elite [S, report 15]. Battery and thermals: not found.
- Gemini Nano/ML Kit GenAI goes through Google Play services [S]; treat as unavailable [I]. ExecuTorch, MLC, llama.cpp also run on Android [P]; LiteRT-LM is the best fit [I].

**F6. Voice [P unless noted].**
- sherpa-onnx (Apache 2.0): Android arm64 ASR, VAD, keyword spotting, TTS (Kokoro, Piper, Matcha) https://raw.githubusercontent.com/k2-fsa/sherpa-onnx/master/README.md . Moonshine: MIT, streaming, Android; non-English legacy models non-commercial https://raw.githubusercontent.com/usefulsensors/moonshine/main/README.md . whisper.cpp: MIT.
- **No AOSP-derived Android 17 tree we can read lists a speech engine**: neither the GrapheneOS `17` nor LineageOS `lineage-24.0` manifest (1,057 and 1,067 projects) has a Pico/svox, espeak or recognizer project; GrapheneOS adds its own MIT on-device TTS (Matcha-TTS fork, Kotlin Misaki phonemizer) https://github.com/GrapheneOS/SpeechServices . So AOSP gives us no maintained TTS or recognizer service [I].
- Piper is now **GPL-3.0** and embeds GPL espeak-ng https://github.com/OHF-Voice/piper1-gpl ; avoid.
- Child speech has materially higher WER than adult speech [M]; Common Sense saw activation and recognition problems in AI toys [S]. Measure on our own consented kid-speech set.

**F7. Child-AI guidance [S].** Common Sense Media: AI toys "Unacceptable", 27% of outputs inappropriate, avoid at 5 and under, caution 6-12 https://www.commonsensemedia.org/press-releases/common-sense-media-warns-against-ai-toy-companions-after-research-reveals-safety-risks . UNICEF Guidance on AI and Children 3.0 (Dec 2025), ten requirements https://www.unicef.org/innocenti/media/11991/file/UNICEF-Innocenti-Guidance-on-AI-and-Children-3-2025.pdf . ICO Children's Code, 15 standards (private by default, minimisation, no nudges, tell the child when parents monitor) https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/childrens-information/childrens-code-guidance-and-resources/introduction-to-the-childrens-code/ . NIST AI RMF [M].

**F8. What binds us (US launch, A1) [S; counsel to confirm].**

| Rule | Status and effect |
|---|---|
| COPPA amended rule | Compliance date 2026-04-22; separate parental consent for non-integral third-party disclosure incl. AI training https://www.dataprotectionreport.com/2025/06/ftcs-coppa-rule-changes-include-ai-training-consent-requirement/ . **Binds us**: consent at portal enrolment, vendors no-train, voice audio is personal information (report 05). Audio-file exception [M, unverified] |
| FTC 6(b) | Orders 2025-09-11 to seven firms on testing, monitoring, age limits, parental controls, COPPA https://www.ftc.gov/news-events/news/press-releases/2025/09/ftc-launches-inquiry-ai-chatbots-acting-companions . Not binding; a preview of FTC questions |
| California SB 243 | In force 2026-01-01. "Companion chatbot" = human-like, "capable of meeting a user's social needs", sustains relationships. Known-minor duties: AI disclosure, 3-hour break reminders, no sexual content, suicide protocol, reporting from 2027-07-01; $1,000 per violation https://www.troutmanprivacy.com/2026/01/analyzing-the-new-ai-companion-chatbot-laws/ . Likely out of scope for a tutor; build the duties anyway |
| WA HB 2225, OR SB 1546 (eff. 2027-01-01), about a dozen state laws | Disclosure, crisis protocols, minor protections https://www.bakerlaw.com/insights/washingtons-new-ai-companion-chatbot-law-childrens-safety-private-right-of-action/ . Same design satisfies |
| GUARD Act (federal) | Senate Judiciary approved 2026-04-30; would ban minors from "AI companions", mandate age verification; later status unknown https://www.globalpolicywatch.com/2026/05/senate-judiciary-committee-advances-guard-act-regulating-minor-use-of-ai/ |
| CA AB 1043 (2027-01-01) | OS providers expose an age bracket; we are the OS vendor (report 05) |
| EU AI Act | Art. 5 age-vulnerability ban (2025-02-02); Art. 50 chatbot disclosure (2026-08-02); high-risk delayed to 2027-12-02 https://www.morganlewis.com/blogs/sourcingatmorganlewis/2026/08/eu-ai-acts-transparency-rules-what-went-into-effect-on-2-august . Only if we sell in the EU |
| UK | Chatbots moving into Online Safety Act duties via the Crime and Policing Bill https://www.lewissilkin.com/insights/2026/02/23/online-safety-reforms-to-be-fast-tracked-amid-rising-ai-risks-102mk2r . Only if we sell in the UK |

## 3. Options & trade-offs

- **Cloud via gateway (Stage 1):** best quality, central moderation and parent logs; costs per use and child data leaves the device.
- **On-device only:** offline, no third-party disclosure, zero marginal cost; but 8-12 GB RAM floor, slow on mid-range, weaker safety and quality, no central logs. Not viable alone.
- **Hybrid (Stage 2):** offline answers only from local curated packs, so no second open-chat safety stack to certify.
- **Self-host open weights:** control, cost at scale; we own GPU ops and all safety, and kid-nuance is weaker. Guards first.

On-device per tier [I, from F5; devices from report 15]:

| Tier | Devices | Stage 1 | Stage 2 |
|---|---|---|---|
| A: 12 GB+, 8-class | Nothing Phone (3), Signature 27 | STT, TTS, small classifier | Gemma 4 E4B or E2B, offline pack Q&A |
| B: 8-12 GB, 7-class | Fairphone Gen 6+, Nothing 4a Pro | STT, TTS | E2B or 1B, templated answers, load on demand |

Under 8 GB is excluded by report 15.

## 4. Recommended design for Zune

**Architecture.** Child app -> (device attestation + signed policy, report 05) -> Zune AI Gateway -> Anthropic API. The device has INTERNET only to Zune; output is plain text (no links, no WebView, report 04). The gateway does:
1. Resolve child, age band, parent policy, time and turn budget; hard per-device token cap and circuit breaker.
2. Input layer: PII scrub (phones, addresses, emails; also on-device), rules plus a Haiku structured-output screen (self-harm, abuse, grooming, sexual, violence, jailbreak, PII) [P pattern: https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks].
3. Main call: Sonnet 5.5, child-safety system prompt (request Anthropic's), age-band persona, curated-pack snippets as `search_results` with citations, low effort (thinking cannot be disabled on 5.5); handle `stop_reason:"refusal"` with a kind redirect [S: Anthropic API reference bundled in this session].
4. Output layer: hold back one sentence, screen it (Haiku now, Qwen3Guard-Stream or gpt-oss-safeguard self-hosted later) before display/TTS.
5. Log to the family's encrypted store, emit alerts, enforce retention.

**Age bands** (set by parent at enrolment; report 05 templates):

| Band | Modes | Style and limits |
|---|---|---|
| 5-7 | Ask Why, Story Maker, voice-first; **no free chat, no photos by default** | 1-3 sentences, about grade 2, topic allowlist, 10 turns/day |
| 8-10 | + Homework Helper (Socratic hints, never just the answer), Look at This | 2-5 sentences, grade 3-5, 25 turns/day |
| 11-13 | + deeper explainers, writing feedback | grade 6-8, 30 turns/day; sensitive topics get curated answer plus trusted-adult redirect |

**Tutor-not-companion rules.** No human name, no claimed feelings or memory, no "best friend", no streaks, rewards or proactive notifications; 20-minute session cap then a break prompt; AI disclosure at every session start (Anthropic, SB 243, EU Art. 50); context reset per session; neutral non-human voice.

**Grounding.** Authored packs (weather, report 14; book metadata; video topics, report 06) feed retrieval; safety-critical topics (first aid, lightning, chemicals, medicine) answer only from authored cards. Permit "I'm not sure, ask a grown-up"; cite as "From the Weather lesson", never URLs [P technique: https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations ; grounding reduces but does not remove errors].

**Disclosure handling** (scripted, not improvised; counsel and a child-safety expert must write the scripts):

| Tier | Trigger | Response |
|---|---|---|
| T0 | self-harm, abuse, grooming, sexual contact, CSAM | Safety mode: warm scripted reply, "tell a trusted grown-up", crisis line (988; Childhelp 1-800-422-4453 [M, verify]); lock session; human T&S review within SLA; guardian notice per policy; NCMEC report where required [P] |
| T1 | bullying, sadness, death, puberty, drugs | Age-appropriate curated answer, adult redirect, daily digest to parent |
| T2 | jailbreaks, profanity, sexual curiosity | Refuse and redirect; count; escalate repeat attempts |

**Image input (D11).** Highest-risk feature. v1: in-app camera and Photos only, **objects, drawings and worksheets**, on-device people/NSFW gate, EXIF stripped, ephemeral by default, server vision screen, text-in-image treated as untrusted data (JSON-encoded, screened) [P pattern: mitigate-jailbreaks page]; upload detection per Anthropic child-safety guidance [P]. Never generate images.

**Parent transparency.** The child always sees "grown-ups can see our chats". Portal: weekly topic summary, immediate T0 alerts, transcripts one tap away with an access log. Summaries-only for 11-13 is decision 3 below.

**Privacy.** No child accounts or names; pseudonymous device ID; vendor ZDR and no training; we never train on child data (COPPA separate consent [S]); per-family KMS (report 05); 30-day default transcript retention, T0 incident records longer in a restricted vault [I]; US-only inference.

**Evaluation harness** (blocks release). About 600 benign kid questions per band (over-refusal); 800 adversarial (roleplay, "my teacher said", opposite-day, leetspeak, secrets, photo requests, friendship/dependency bait, multi-turn crescendo); grounded QA (citation faithfulness); image set; T0 recall set. Metrics: critical unsafe outputs (target 0 observed), over-refusal, reading grade per band, T0 recall and routing, injection success. Run on every prompt, model or classifier change; LLM judge plus expert human review; public seeds (XSTest, HarmBench, ToxicChat) [M, verify]; thresholds set with the child-safety expert.

**Incident response [I].** Server-side kill switch per band, feature or global (fallback: curated-only answers). P0 (harmful output reached a child): disable in minutes, preserve logs, notify parents, counsel, vendor, regulators, NCMEC as applicable; postmortem and new eval cases within 72 hours; on-call for T0 from launch.

**Voice.** Push-to-talk only in v1 (no always-on mic: privacy, battery, misfires). On-device STT (Moonshine or Whisper-tiny via sherpa-onnx); show the transcript with tap-to-retry; gate launch on measured kid-speech WER. TTS: sherpa-onnx with Kokoro-82M (code Apache 2.0 [P], weights licence [M]) or Matcha (MIT [P]); Stage 2 expose it as a system TextToSpeechService (or adopt GrapheneOS Speech Services, MIT) for the EPUB reader and Weather. English first; Spanish Stage 2 (Qwen3Guard covers 119 languages [P]).

**Cost per active child per month** [I; P prices; assumptions: 2,000 cached prompt tokens, 1,160 uncached input, 160 output, two Haiku screens per turn, 8% image turns; Sonnet 5.5; cache writes amortised over six turns]:

| Usage | Turns | Sonnet 5.5 + guards | With 25% FAQ-cache hits | Haiku 4.5 main |
|---|---|---|---|---|
| Light | 100 | $0.59 | $0.46 | $0.32 |
| Typical | 240 | $1.42 | $1.10 | $0.78 |
| Heavy (daily cap) | 600 | $3.55 | $2.75 | $1.95 |

US-pinned adds 1.1x. Cloud TTS would add about $2-4 per child per month and cloud STT $0.1-0.2 [M prices], hence on-device voice. Fixed cost, not per child: Trust & Safety staffing.

**v1 scope.** Four modes above, three bands, voice and text, limited images, parent alerts and transcripts, eval harness, kill switch. **Will NOT build:** open-ended companion or friend chat, roleplay personas, cross-session personal memory, web search or any link/browser path (D1, D2), image or video generation, tools with side effects (calls, messages, purchases), voice cloning, always-on listening, ads, engagement streaks, sharing child data for AI training, group chat with the assistant, and an under-7 free-chat mode.

## 5. Risks & unknowns

- Anthropic may decline, add conditions, audit or suspend; single-vendor dependency (mitigate: provider abstraction, OpenAI/self-host fallback).
- Child jailbreak creativity and multi-turn drift; self-harm false negatives are the worst case; false positives frustrate families.
- Abuse disclosure where the parent is the risk: guardian notification can harm the child.
- Child-voice STT accuracy, battery, thermals, on-device latency are **unmeasured**.
- Image input: PII, self-generated sexual imagery, CSAM reporting duty.
- Regulatory churn: GUARD Act status after May 2026 unknown; parent attestation may not count as "reasonable age verification"; COPPA audio exception and SB 243 scope unverified.
- Transcripts are a breach honeypot; Anthropic keeps flagged data up to 2 years even under ZDR [P].
- Gemma 4 and Kokoro weight licences unread; Moonshine non-English licences differ.
- Cost spikes from loops or abuse (mitigate: per-device budgets).

## 6. Decisions needed from the founder

1. Approve outreach to Anthropic for written under-13 confirmation, ZDR, DPA and the child-safety prompt; direct API (recommended) vs Bedrock; OpenAI as named fallback.
2. Minimum age for the assistant, and whether 5-7 gets only the constrained mode (recommended).
3. Parent visibility for 11-13: full transcripts (D11 default) vs summaries plus alerts.
4. Abuse-disclosure policy (who is told when a parent may be involved) and T&S staffing (24x7?); needs a child-safety expert and counsel.
5. Image input in v1: objects/homework only (recommended) vs any photo.
6. Push-to-talk only (recommended) vs wake word; launch languages (English only?).
7. AI included in subscription, daily turn cap default (30), COGS ceiling.
8. AI transcript retention default (30 days proposed) vs 180 days in report 13.
9. Accept the no-persona, no-friend positioning (needed to stay outside SB 243 "companion").

## 7. Load-bearing claims

1. Anthropic permits API products for minors given age gating, moderation, monitoring, AI disclosure, COPPA statement, with audits [P]: https://support.claude.com/en/articles/9307344-responsible-use-of-anthropic-s-models-guidelines-for-organizations-serving-minors
2. ZDR is obtainable for Messages/caching/citations; flagged data may be kept 2 years [P]: https://platform.claude.com/docs/en/manage-claude/api-and-data-retention
3. Gemini API terms bar API clients directed at or likely accessed by under-18s [S]: https://ai.google.dev/gemini-api/terms
4. OpenAI requires ZDR before processing under-13 personal data [S]: https://developers.openai.com/api/docs/guides/safety-checks/under-18-api-guidance
5. Sonnet 5.5 $2/$10, Haiku 4.5 $1/$5, US geo 1.1x [P]: https://platform.claude.com/docs/en/about-claude/pricing
6. Gemma 4 on-device needs 8 GB (E2B) or 12 GB (E4B); LiteRT-LM is Apache 2.0 and needs no Play Services [P]: google-ai-edge/gallery@main:model_allowlists/1_0_19.json; https://raw.githubusercontent.com/google-ai-edge/LiteRT-LM/main/README.md
7. No speech engine in the GrapheneOS 17 or LineageOS 24 manifests; GrapheneOS ships its own MIT TTS; Piper is GPL-3 [P]: GrapheneOS/platform_manifest@17:default.xml; LineageOS/android@lineage-24.0:default.xml; https://github.com/GrapheneOS/SpeechServices
8. COPPA amended rule: compliance 2026-04-22, AI-training disclosure needs separate consent [S]: https://www.dataprotectionreport.com/2025/06/ftcs-coppa-rule-changes-include-ai-training-consent-requirement/
9. SB 243 in force 2026-01-01; its companion-chatbot definition is avoidable by a tutor [S]: https://www.troutmanprivacy.com/2026/01/analyzing-the-new-ai-companion-chatbot-laws/
10. Common Sense rates AI toys "Unacceptable", avoid at 5 and under [S]: https://www.commonsensemedia.org/press-releases/common-sense-media-warns-against-ai-toy-companions-after-research-reveals-safety-risks
