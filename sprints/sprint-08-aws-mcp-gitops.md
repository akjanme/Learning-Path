# Sprint 8 — Same platform on AWS, MCP and GitOps (Days 57–64)

**Scenario you build:** the RAG API deployed on AWS with Terraform, an MCP server that exposes internal .NET APIs safely to agents, and Argo CD managing AKS with canary releases.

[← Back to tracker](../TRACKER.md)

---

<a id="day-57"></a>
### Day 57 · Cloud · AWS foundations, mapped from Azure

**Time:** ~3 h

**Why it matters:** most enterprises are multi-cloud in practice. Showing you can map concepts quickly is enough for most Azure-first roles.

**Learn**
- **Azure → AWS mapping:** Entra ID → IAM Identity Center; subscription → account; management group → OU; Azure Policy → SCPs + AWS Config; VNet → VPC; NSG → security group (+ NACL); Private Endpoint → PrivateLink interface endpoint; Key Vault → Secrets Manager + KMS; Azure Monitor → CloudWatch.
- **IAM:** identity vs resource policies, explicit deny wins, roles and `AssumeRole`, instance profiles, EKS Pod Identity / IRSA.
- **VPC:** public/private subnets, internet gateway, NAT gateway, route tables, gateway vs interface endpoints.

**Do**
- [ ] AWS account with a budget alarm and MFA on root (then stop using root)
- [ ] Terraform: VPC across 2 AZs with public and private subnets
- [ ] Least-privilege IAM role for an ECS task (read one secret, one S3 prefix)
- [ ] `docs/azure-aws-map.md` with your own mapping table

**Interview questions**
1. **How is an IAM policy evaluated?** — Default deny. An explicit deny anywhere wins. Otherwise you need an allow from identity or resource policies, within SCPs and permission boundaries.
2. **Security group vs NACL?** — A security group is stateful, at instance/ENI level, allow-only. A NACL is stateless, at subnet level, with allow and deny rules (remember ephemeral ports).
3. **How do you structure AWS accounts for an enterprise?** — AWS Organizations with OUs (security, infrastructure, workloads, sandbox), an account per workload/environment, SCP guardrails, Control Tower for the landing zone.

**Gotchas**
- NAT Gateway hourly and data-processing charges add up quickly.
- Stateless NACLs need ephemeral return ports allowed.
- Most resources are regional. Check the region before "it's missing".

**Scenario:** your Azure-only company acquired a firm running on AWS. What do you unify first?

**Done when:** you can map any Azure service in your app to its AWS equivalent and explain the differences.

**Resources:** [AWS Well-Architected](https://aws.amazon.com/architecture/well-architected/) · [Azure for AWS professionals](https://learn.microsoft.com/azure/architecture/aws-professional/)

---

<a id="day-58"></a>
### Day 58 · Cloud · AWS services for the app: ECS/EKS, Lambda, SQS/SNS, data, Bedrock

**Time:** ~3 h

**Why it matters:** this proves you can deliver the same architecture on AWS, not just name services.

**Learn**
- **Compute:** ECS on Fargate vs EKS; Lambda limits (15-minute max, cold starts, VPC networking).
- **Messaging:** SQS standard vs FIFO, visibility timeout, DLQs; SNS fan-out; EventBridge.
- **Data:** RDS/Aurora; DynamoDB (partition key, GSIs, on-demand vs provisioned).
- **AI:** Bedrock (model access, knowledge bases, guardrails) and CloudWatch for observability.

**Do**
- [ ] Deploy the RAG API to ECS Fargate via Terraform, behind an ALB, with an SQS-driven worker
- [ ] Use Bedrock for generation (or keep Azure OpenAI and call it across clouds, and document the trade-off)
- [ ] Compare cost and effort with Azure in `docs/azure-vs-aws.md`

**Interview questions**
1. **Azure Container Apps vs ECS Fargate vs EKS: when do you pick each?** — Container Apps / Fargate for simple, serverless container ops. EKS/AKS for platform needs (operators, mesh, multi-tenant clusters).
2. **What goes wrong if the SQS visibility timeout is too short?** — The message reappears while it's still being processed, so it's processed twice. Set the timeout above processing time, or extend it during processing.
3. **Bedrock or Azure OpenAI?** — Model choice and availability, data residency, existing cloud and identity, enterprise agreements, guardrail features, latency to your data.

**Gotchas**
- Lambda in a VPC needs a NAT or VPC endpoints to reach the internet and AWS APIs.
- DynamoDB hot partitions, same as Cosmos DB.
- Bedrock model access must be enabled per model and region.

**Scenario:** leadership asks for "cloud-agnostic" everything. Where do you agree, and where do you push back?

**Done when:** the same `/ask` request works against both deployments.

**Resources:** [Amazon ECS docs](https://docs.aws.amazon.com/ecs/) · [Amazon Bedrock docs](https://docs.aws.amazon.com/bedrock/)

---

<a id="day-59"></a>
### Day 59 · AI · Model Context Protocol (MCP)

**Time:** ~3 h

**Why it matters:** MCP is becoming the standard way to connect AI agents to enterprise systems, and forward-deployed AI roles ask about it.

**Learn**
- **Roles:** host, client, server.
- **Primitives:** tools, resources, prompts.
- **Transports:** stdio (local) vs Streamable HTTP (remote).
- **Authorization:** OAuth-based authorization for remote servers. Servers must validate tokens issued *for them* (no token passthrough).
- **Risks:** tool poisoning, over-permissioned tools, confused deputy, untrusted servers.

**Do**
- [ ] Python MCP server (official SDK) exposing `get_mandate` and `list_pending_approvals`, which call the .NET API *with the user's token*
- [ ] Connect it to your agent and to one desktop MCP client (e.g. VS Code)
- [ ] Write `docs/mcp-security.md`: what each tool can do and who can call it

**Interview questions**
1. **MCP vs plain function calling?** — Function calling is the model-side mechanism. MCP is a standard protocol to package and expose tools/resources so any compatible client can use them, decoupling integrations from one app.
2. **How do you secure a remote MCP server?** — OAuth with audience-validated tokens, per-user authorization inside each tool, least-privilege tools, rate limits, audit logs, and allow-listed clients.
3. **How do you let an LLM call internal systems safely?** — Narrow, typed tools; the user's identity enforced by the backend; approvals for writes; input validation; logging; no raw database or shell access.

**Gotchas**
- stdio MCP servers run with your local user's full permissions.
- Forwarding the client's token to downstream APIs without proper exchange (token passthrough).
- Tool descriptions from third-party servers can contain injected instructions.

**Scenario:** a team wants to plug a community MCP server into the production agent. What's your review checklist?

**Done when:** a non-approver calling `list_pending_approvals` through MCP is rejected by the .NET API.

**Resources:** [MCP docs](https://modelcontextprotocol.io/) · [MCP security best practices](https://modelcontextprotocol.io/specification/draft/basic/security_best_practices)

---

<a id="day-60"></a>
### Day 60 · AI · AI in .NET: Microsoft.Extensions.AI and Semantic Kernel

**Time:** ~3 h

**Why it matters:** your .NET background is an advantage. Many enterprises want AI inside existing .NET systems, not only in Python.

**Learn**
- **`Microsoft.Extensions.AI`:** `IChatClient` and `IEmbeddingGenerator` abstractions, with middleware (logging, caching, telemetry).
- **Semantic Kernel:** plugins/functions, function calling, memory/connectors.
- **Microsoft Agent Framework:** awareness of the newer agent framework from the SK/AutoGen teams; check its current status.
- **Where AI belongs:** a .NET service vs a separate Python AI service.

**Do**
- [ ] .NET endpoint that summarises a mandate using `IChatClient` (Azure OpenAI via Entra auth)
- [ ] Semantic Kernel plugin that calls a domain service; let the model use it
- [ ] Short comparison note: .NET vs Python for this feature

**Interview questions**
1. **Should AI features live in the .NET service or a separate Python service?** — Simple completions, summarisation and tool calls fit well in .NET (one stack, one deploy). Heavy RAG/agent/ML ecosystems and fast-moving libraries favour Python. Decide by team skills and ownership.
2. **How do you avoid vendor lock-in in AI code?** — Abstractions (`IChatClient`), prompts and config outside code, evaluation suites to validate a model switch, a gateway in front of providers.
3. **How do you test AI code in .NET?** — Mock `IChatClient` for unit tests, contract tests on structured outputs, evaluation tests against a fixed dataset.

**Gotchas**
- AI SDKs change fast. Pin versions and read release notes.
- Duplicating prompts and logic across .NET and Python drifts.

**Scenario:** the .NET team refuses to run Python in production. Deliver the AI feature anyway.

**Done when:** the .NET API has one working AI feature with telemetry.

**Resources:** [Microsoft.Extensions.AI](https://learn.microsoft.com/dotnet/ai/microsoft-extensions-ai) · [Semantic Kernel](https://learn.microsoft.com/semantic-kernel/)

---

<a id="day-61"></a>
### Day 61 · DevOps · Terraform for multiple environments and clouds

**Time:** ~3 h

**Why it matters:** structuring IaC for many teams, environments and clouds is a key platform-engineer question.

**Learn**
- **Repo layouts:** modules repo + live/environments repo, or monorepo with clear boundaries.
- **Module versioning:** git tags or a private registry; semantic versioning.
- **Environment promotion:** same module version through dev → test → prod.
- **Provider aliases** for multi-region/multi-account.
- **Multi-cloud:** separate modules per cloud behind a similar interface. A "universal" module is usually an anti-pattern.
- **Ecosystem awareness:** `terraform test`, Terragrunt, Terraform Stacks, OpenTofu.

**Do**
- [ ] Refactor into versioned modules; dev and prod environments consume pinned versions
- [ ] Write a `terraform test` for one module
- [ ] Promote a module change from dev to prod by bumping the version

**Interview questions**
1. **How do you structure Terraform for multiple teams and environments?** — Shared versioned modules, separate state per environment and component, PR plans, policy checks, environment-scoped pipeline identities.
2. **How do you promote an infrastructure change safely?** — Version the module, apply to dev, test, then bump the version in prod with plan review and approval.
3. **Is a single multi-cloud module a good idea?** — Usually not: lowest-common-denominator features and leaky abstractions. Standardise the interface and conventions, not the implementation.

**Gotchas**
- One huge root module: slow plans and a huge blast radius.
- Unpinned module sources (`ref=main`).
- Shared state between teams.

**Scenario:** a module change meant for dev was applied to prod. How did your structure allow it, and how do you fix that?

**Done when:** dev and prod run different module versions on purpose, and both plan cleanly.

**Resources:** [Terraform modules](https://developer.hashicorp.com/terraform/language/modules) · [terraform test](https://developer.hashicorp.com/terraform/language/tests)

---

<a id="day-62"></a>
### Day 62 · DevOps · GitOps with Argo CD and progressive delivery

**Time:** ~3 h

**Why it matters:** GitOps is the dominant deployment model for Kubernetes in enterprises.

**Learn**
- **GitOps principles:** declarative, versioned, pulled, continuously reconciled.
- **Argo CD:** Applications, sync policies, self-heal, prune, ApplicationSets, app-of-apps, sync waves. (Flux is the main alternative.)
- **Progressive delivery:** Argo Rollouts canary/blue-green with automated analysis and rollback.
- **Secrets in GitOps:** External Secrets Operator or the Key Vault CSI driver. Never plain Secrets in Git.

**Do**
- [ ] Install Argo CD on AKS; manage your 3 services from a Git repo
- [ ] ApplicationSet for dev and prod
- [ ] Canary for the RAG API with Argo Rollouts: roll back automatically when the error rate rises

**Interview questions**
1. **Push-based CI/CD vs GitOps?** — Push: the pipeline has cluster credentials and pushes changes. GitOps: an in-cluster agent pulls from Git and reconciles. No cluster credentials in CI, drift is corrected, and Git is the audit log.
2. **How do you roll back in GitOps?** — Revert the commit and let Argo sync, or let Rollouts abort the canary automatically on bad metrics.
3. **How do you handle secrets with GitOps?** — External Secrets / CSI driver pulling from Key Vault. Git holds references, never values.

**Gotchas**
- Manual `kubectl` fixes get reverted by self-heal. Change Git instead.
- CRDs must sync before the resources that use them (sync waves).
- Auto-sync with prune on a misconfigured path can delete workloads.

**Scenario:** someone hot-fixed production with `kubectl edit`, and Argo reverted it during an incident. What's your process?

**Done when:** a bad release is rolled back automatically by the canary analysis.

**Resources:** [Argo CD docs](https://argo-cd.readthedocs.io/) · [Argo Rollouts](https://argoproj.github.io/argo-rollouts/)

---

<a id="day-63"></a>
### Day 63 · .NET + Design · Event-driven design, sagas, CQRS and migration strategy

**Time:** ~2 h

**Why it matters:** these patterns and cloud migration strategy are core solution-architect material.

**Learn**
- **Events vs commands;** choreography vs orchestration.
- **Sagas:** compensating actions, timeouts, idempotency.
- **CQRS read models;** when event sourcing is worth it (and when it isn't).
- **CAP / PACELC** in plain terms.
- **Migration:** the 6 Rs (rehost, replatform, refactor, repurchase, retire, retain) and the strangler fig pattern.

**Do**
- [ ] Orchestrated saga for mandate approval (Durable Functions or a MassTransit state machine) with a compensation step
- [ ] 45-minute drill: migration plan for a 10-year-old on-prem .NET app (`design/migration.md`)

**Interview questions**
1. **Migrate a 10-year-old on-prem .NET app to the cloud: which R, and in what order?** — Assess, then usually rehost/replatform first for quick wins (containers, managed DB), then refactor the hot spots with the strangler fig. Retire what's unused.
2. **Choreography or orchestration for a saga?** — Choreography for a few simple steps (loose coupling). Orchestration for complex flows needing visibility, timeouts and compensation.
3. **When should you *not* use event sourcing?** — Simple CRUD domains, teams new to it, heavy reporting needs without read models, or when audit needs are met by simpler change logs.

**Gotchas**
- Distributed transactions (2PC) across services don't scale and couple availability.
- Eventual consistency without UX design confuses users.
- Event schema changes without versioning break consumers.

**Scenario:** a mandate approval succeeded in one service and failed in another. The customer is charged but not set up. Design the fix.

**Done when:** your saga compensates correctly when the last step fails.

**Resources:** [Saga pattern](https://learn.microsoft.com/azure/architecture/patterns/saga) · [Cloud migration strategies (CAF)](https://learn.microsoft.com/azure/cloud-adoption-framework/migrate/)

---

<a id="day-64"></a>
### Day 64 · Build + Defend · Same platform on AWS, plus MCP and GitOps

**Time:** ~4 h

**Do**
- [ ] RAG API running on AWS (ECS + SQS + Secrets Manager) from Terraform
- [ ] MCP server in front of internal APIs, using the user's identity
- [ ] Argo CD + canary on AKS
- [ ] `docs/adr/007-multi-cloud-scope.md`
- [ ] Record answers to the three questions below

**Interview questions**
1. **The company is going multi-cloud. What do you standardise and what do you leave cloud-native?** — Standardise identity federation, IaC tooling, CI/CD, observability, security policies and containers. Keep managed data and AI services native per cloud.
2. **Migrate a 10-year-old on-prem .NET app to the cloud: which of the 6 Rs, and in what order?** — Your migration drill.
3. **How do you let an LLM call internal systems safely?** — Your MCP server and its security note.

**Gotchas**
- Cross-cloud calls add egress cost and latency. Show the numbers in your ADR.

**Done when:** both clouds serve the same API, and the README explains why Azure stays primary.
