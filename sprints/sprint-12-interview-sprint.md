# Sprint 12 — Interview sprint, mock interviews last (Days 89–96)

**Goal:** turn everything you built into fluent interview answers. Days 89–93 rehearse; Days 94–96 are full mock interviews.

Use [QUESTION-BANK.md](../QUESTION-BANK.md), which collects every interview question from Days 1–88 in one place.

[← Back to tracker](../TRACKER.md)

---

<a id="day-89"></a>
### Day 89 · Interview prep · Cloud scenario rehearsal

**Time:** ~3 h

**Why it matters:** cloud architecture rounds reward structure and specifics from real builds.

**Do**
- [ ] Answer every Cloud question from the question bank out loud, 3–5 minutes each; record yourself
- [ ] For each answer, name one thing you *built* that proves it
- [ ] Mark weak answers 🔴 / OK 🟡 / strong 🟢 in `interview/self-review.md`; redo every 🔴

**Interview questions**
1. **Design the network and identity for a regulated workload on Azure.** — Hub-spoke, private endpoints, Entra + PIM, policy guardrails, logging.
2. **An app can't reach a PaaS service after a private endpoint was added. Troubleshoot it.** — DNS → zone link → forwarders → NSG/UDR → public access → RBAC.
3. **Design DR for a banking app with a 15-minute RPO.** — Your DR doc.

**Gotchas**
- Answers that only name services. Always say *why* and *what you gave up*.

**Done when:** no 🔴 left in the Cloud section.

---

<a id="day-90"></a>
### Day 90 · Interview prep · AI engineering scenario rehearsal

**Time:** ~3 h

**Do**
- [ ] Answer every AI and LLMOps question from the question bank out loud; record yourself
- [ ] Prepare a 2-minute whiteboard of your RAG + agent architecture
- [ ] Prepare to live-code a minimal RAG endpoint in 30 minutes (practise once, timed)

**Interview questions**
1. **Design an enterprise RAG assistant for 10,000 employees with document-level permissions.** — Ingestion, chunking, hybrid search, ACL filtering, gateway, guardrails, evaluation, monitoring.
2. **Your RAG is wrong 20% of the time. Fix it.** — Separate retrieval vs generation, measure, fix the biggest bucket.
3. **How do you secure an agent that can take actions?** — Least-privilege tools, user identity, approvals, injection defences, audit.

**Gotchas**
- Over-indexing on framework names. Interviewers want reasoning and evaluation.

**Done when:** you can draw your AI architecture from memory in 2 minutes.

---

<a id="day-91"></a>
### Day 91 · Interview prep · DevOps and platform rehearsal + live troubleshooting

**Time:** ~3 h

**Do**
- [ ] Answer every DevOps question from the question bank out loud
- [ ] Live troubleshooting drill: a friend breaks your kind/AKS cluster in 3 ways while you narrate your debugging out loud
- [ ] Prepare a 2-minute walkthrough of your pipeline (commit → prod)

**Interview questions**
1. **Design CI/CD for 30 microservices owned by 6 teams.** — Templates, build once, scan/sign, GitOps, approvals, DORA.
2. **A pod is in CrashLoopBackOff in production. Go.** — The commands, in order, narrated.
3. **How do you structure Terraform for many teams and environments?** — Modules, state separation, PR plans, policy.

**Gotchas**
- Going silent while debugging. Narrate your hypotheses.

**Done when:** you fix all 3 induced failures while explaining each step.

---

<a id="day-92"></a>
### Day 92 · Interview prep · System design rounds (timed)

**Time:** ~3 h

**Do**
- [ ] Two timed 45-minute rounds from this list: chat/messaging system, ride-sharing, distributed job scheduler, e-commerce checkout
- [ ] Use the Day 7 framework; record yourself or do it with a peer
- [ ] Self-score each with the rubric below

**Rubric (score 1–4 each):** requirements clarified · estimates made · API + data model · high-level design · deep dive on the hardest part · trade-offs stated · failure modes covered · communication.

**Interview questions**
1. **Design a WhatsApp-like messaging system.** — Connections (WebSockets), message store, fan-out, delivery receipts, offline delivery, ordering per chat, scale numbers.
2. **Design an Uber-like ride-matching system.** — Location updates, geo-indexing, matching service, surge, consistency of trip state.
3. **Design a distributed job scheduler.** — Job store, leader election/locking, at-least-once execution, idempotent jobs, retries, monitoring.

**Gotchas**
- Spending 20 minutes on requirements, or zero. Aim for about 5.

**Done when:** both rounds score at least 3 on every rubric line.

---

<a id="day-93"></a>
### Day 93 · Interview prep · STAR stories, CV and profiles

**Time:** ~3 h

**Do**
- [ ] Write and rehearse 8 STAR stories (2 minutes each): a production incident you led · a design decision where you changed minds · a migration/modernisation · cutting cloud cost · a security issue · an AI feature you shipped and measured · speed vs quality conflict · leading a team through a new technology
- [ ] Rewrite the CV headline: *Senior .NET / Cloud / AI Solution Architect with hands-on Python, LLM and platform engineering*
- [ ] Each CV bullet = action + technology + measurable result
- [ ] Update LinkedIn and the GitHub profile to point at the capstone

**Interview questions**
1. **Tell me about yourself.** — 90 seconds: background → what you've built recently → what you want next.
2. **Why are you moving towards cloud/AI/platform work?** — A genuine reason backed by what you built.
3. **Tell me about a time you failed.** — A real failure, what you changed, the result.

**Gotchas**
- STAR stories without a measurable result. Add numbers.

**Done when:** all 8 stories fit in 2 minutes each and end with a result.

---

<a id="day-94"></a>
### Day 94 · Mock interview 1 · Cloud and architecture (whiteboard)

**Time:** ~2 h (60-minute mock + 60-minute review)

**Format:** a peer, mentor or colleague acts as interviewer. If no one is available, use an AI assistant as interviewer *and* record yourself on video.

**Run it**
- [ ] 5 min: introduction ("tell me about yourself")
- [ ] 35 min: design scenario: *"Design an Azure platform for a bank's internal AI assistant used by 10,000 staff, with document-level permissions and a 15-minute RPO."*
- [ ] 15 min: follow-up probes: private endpoint DNS failure; cost tripled; region outage
- [ ] 5 min: your questions for the interviewer

**Interviewer's scorecard (1–4):** structure · requirements · security/identity · networking · reliability/DR · cost awareness · trade-offs · communication.

**Interview questions**
1. **Design an Azure platform for a bank's internal AI assistant used by 10,000 staff.** — Full design using your capstone.
2. **Private endpoint resolution failed in production. What happened?** — DNS troubleshooting path.
3. **The region is down. What happens to your system?** — DR walkthrough with RTO/RPO.

**After**
- [ ] Write the 3 weakest moments and a better answer for each in `interview/mock-1.md`

**Done when:** feedback is written down and the weak answers are reworked.

---

<a id="day-95"></a>
### Day 95 · Mock interview 2 · AI engineering (design + live build/debug)

**Time:** ~2.5 h (75-minute mock + review)

**Run it**
- [ ] 30 min design: *"Design an AI agent that processes corporate onboarding documents and requests approvals."*
- [ ] 30 min live: build or debug a small RAG/agent endpoint (the interviewer gives a bug or a feature)
- [ ] 15 min probes: prompt injection in an uploaded document; evaluation before launch; model choice and cost

**Interviewer's scorecard (1–4):** problem framing · RAG/agent design · security and guardrails · evaluation · coding fluency · debugging approach · cost/latency awareness · communication.

**Interview questions**
1. **Design an AI agent for onboarding documents with approvals.** — Document pipeline + agent + human-in-the-loop + audit.
2. **An uploaded document contains hidden instructions. What does your system do?** — Indirect injection defences.
3. **How do you decide this is ready to launch?** — Evaluation gates, red-team, pilot, monitoring.

**After**
- [ ] `interview/mock-2.md` with feedback and improved answers

**Done when:** you've completed the live portion without freezing, even if not perfectly.

---

<a id="day-96"></a>
### Day 96 · Mock interview 3 · DevOps/platform + behavioural, then final review

**Time:** ~3 h

**Run it**
- [ ] 30 min technical: *"Design the delivery platform for 30 microservices across 6 teams on AKS."* plus a live troubleshooting question
- [ ] 20 min behavioural: 3 of your STAR stories, chosen by the interviewer
- [ ] 10 min: "Why should we hire you?" and your questions

**Interviewer's scorecard (1–4):** CI/CD design · GitOps/IaC · Kubernetes operations · security/supply chain · observability · behavioural depth · leadership signals · communication.

**Interview questions**
1. **Design the delivery platform for 30 microservices across 6 teams.** — Your pipeline + GitOps + templates + policy.
2. **Production is down after a deploy. Walk me through the first 15 minutes.** — Incident handling + rollback.
3. **Why should we hire you?** — .NET depth + cloud/AI/platform builds + architecture judgement, with proof.

**After**
- [ ] Final self-review across all three mocks; list the top 5 topics to keep practising
- [ ] Apply to 10 target roles this week; tailor the CV headline to each
- [ ] 🎉 Mark the plan complete in the tracker

**Done when:** three mocks are done, feedback is captured, and applications are out.
