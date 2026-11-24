# 6-Month Job-Ready Plan — Cloud · AI · DevOps (MLOps last)

A 96-day, interview-focused plan for an experienced .NET developer / tech lead moving into **Cloud, AI engineering and DevOps/Platform** roles. The days are numbered, not dated, so skip days, go at your pace, and keep it in Git.

**Focus order:** Cloud, AI and DevOps from Day 1 · .NET and system design run lightly in parallel (one day per sprint) · MLOps comes last (Sprints 9–10) · mock interviews at the very end (Days 94–96). No certifications.

## How to use this repo

1. **Fork or copy it** into your own GitHub account (private is fine).
2. Open [TRACKER.md](TRACKER.md) and start at Day 1. Tick a day only when its **Done when** line is true.
3. Each day has the same structure:
   - **Why it matters**: why interviewers and employers care
   - **Learn**: the topics, each with a short description of what to know
   - **Do**: hands-on checklist (this is the real work)
   - **Interview questions**: the most likely questions, with answer hints
   - **Gotchas**: mistakes and edge cases that catch people out in production and interviews
   - **Scenario**: a realistic situation to reason through out loud
   - **Done when**: the bar for ticking the day
   - **Resources**: official docs and free courses first; Pluralsight where its labs help
4. Every 8th day is **Build + Defend**: integrate the sprint's work into one portfolio piece and record yourself answering its three scenario questions.
5. Use [QUESTION-BANK.md](QUESTION-BANK.md) (all 288 questions with hints) for revision at any point.

## Sprints

| Sprint | Days | Scenario you build |
| --- | --- | --- |
| 1 | 1–8 | [Secure baseline](sprints/sprint-01-secure-baseline.md): governed subscription, Managed Identity, containers |
| 2 | 9–16 | [Private internal AI assistant](sprints/sprint-02-private-ai-assistant.md): hub-spoke, private endpoints, structured LLM output |
| 3 | 17–24 | [Policy-document Q&A](sprints/sprint-03-policy-document-qa.md): event-driven ingestion, RAG with citations, Terraform |
| 4 | 25–32 | [Permission-aware RAG](sprints/sprint-04-permission-aware-rag.md): hybrid search, security trimming, evaluation, CI/CD with OIDC |
| 5 | 33–40 | [Support-ticket agent on AKS](sprints/sprint-05-agent-on-aks.md): AKS, workload identity, LangGraph, Helm |
| 6 | 41–48 | [Production readiness](sprints/sprint-06-production-readiness.md): observability, LLM cost tracing, SLOs, DR, game day |
| 7 | 49–56 | [Secure AI gateway](sprints/sprint-07-secure-ai-gateway.md): APIM AI gateway, guardrails, prompt injection, DevSecOps, OAuth |
| 8 | 57–64 | [AWS, MCP and GitOps](sprints/sprint-08-aws-mcp-gitops.md): same platform on AWS, MCP server, Argo CD canary |
| 9 | 65–72 | [MLOps I](sprints/sprint-09-mlops-document-pipeline.md): Document Intelligence, scikit-learn, MLflow, Azure ML, CI/CD for ML |
| 10 | 73–80 | [MLOps II](sprints/sprint-10-model-and-prompt-lifecycle.md): serving, drift and retraining, LLM eval gates, model cost, FinOps |
| 11 | 81–88 | [Capstone](sprints/sprint-11-capstone.md): enterprise AI banking platform, documented like an architect |
| 12 | 89–96 | [Interview sprint](sprints/sprint-12-interview-sprint.md): rehearsal, system design rounds, STAR stories, **3 mock interviews** |

## Time

- About **2–4 hours per day**; Build + Defend days run longer.
- At ~4 study days a week the plan takes about 24 weeks; at 3 a week, about 32 weeks. Both are fine, because finishing matters more than speed.
- Short on time? Cut reading, never the **Do** list.

## Suggested layout for your own work

Keep your build artifacts in this repo (or a sibling repo) so the tracker links to real evidence:

```
docs/
  adr/            # 001-..., 002-...: one per major decision
  architecture/   # HLD/LLD diagrams
  postmortems/    # game-day and incident write-ups
design/           # system design drills (markdown + diagrams)
interview/        # self-review, mock interview feedback
infra/            # Terraform
apps/             # .NET and Python services
```

## Tracking options

- **In Markdown:** tick boxes in `TRACKER.md` and commit (`git commit -m "Day 12 done"`). Your commit history becomes a study log.
- **As a spreadsheet or GitHub Project:** import [tracker.csv](tracker.csv) (Day, Sprint, Track, Topic, Status, Date done, Confidence, Notes).
- **As GitHub Issues:** run `python scripts/create_github_issues.py --repo <you>/<repo>` to preview, then add `--apply` to create one issue per day with sprint and track labels (needs the GitHub CLI, `gh auth login`). Add them to a GitHub Project board for a Kanban view.

## Ground rules

- Use **synthetic data only**. Never employer code, credentials or real customer data in public repos or external AI services.
- Set a **cloud budget alert** before Day 1 (about USD 50/month is enough if you tear down environments). Use `terraform destroy` at the end of each sprint.
- Resource links point to official docs and free courses where possible. Pluralsight paths and labs are suggested only where the sandboxes save time and money.

## Regenerating the tracker

`TRACKER.md`, `QUESTION-BANK.md` and `tracker.csv` are generated from the sprint files. If you edit a sprint file (add a day, change a topic), rerun:

```bash
python scripts/build_tracker.py .
```

Note: regenerating resets the checkboxes in `TRACKER.md`, so track progress in the CSV or Issues if you plan to edit sprint files often.
