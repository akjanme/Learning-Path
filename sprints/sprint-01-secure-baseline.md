# Sprint 1 — Secure baseline (Days 1–8)

**Scenario you build:** a governed Azure subscription where a .NET API and a Python FastAPI service run in containers and read secrets through Managed Identity, with no secrets in code.

[← Back to tracker](../TRACKER.md)

---

<a id="day-1"></a>
### Day 1 · Cloud · Azure landing zones and governance

**Time:** ~3 h

**Why it matters:** this is the first thing enterprise cloud teams build. Interviewers check whether you think in guardrails and structure, not individual resources.

**Learn**
- **Resource hierarchy:** tenant → management groups → subscriptions → resource groups → resources. RBAC and Policy inherit downward, so where you assign them decides the blast radius.
- **CAF landing zones:** the *platform* landing zones (identity, connectivity, management) are separate from *application* landing zones. Subscription vending gives each workload its own governed subscription.
- **Azure Policy:** effects (Deny, Audit, Modify, Append, DeployIfNotExists), initiatives (policy sets), assignment scope, exemptions.
- **Cost governance:** required tags, budgets, Cost Management views per tag and subscription.

**Do**
- [ ] Create a small management-group tree: `Platform`, `LandingZones/Corp`, `LandingZones/Online`, `Sandbox`
- [ ] Assign 3 policies at management-group level: allowed locations, require a `CostCenter` tag, deny public IPs on NICs
- [ ] Set a budget alert at USD 50 on your subscription
- [ ] Draw the hierarchy (draw.io or Excalidraw), commit it to `docs/day-01-governance.png`

**Interview questions**
1. **How would you organise Azure for 20 application teams?** — Use management groups by archetype (corp/online/sandbox), a subscription per workload per environment as the unit of isolation and scale, and policy plus RBAC at management-group level. Use subscription vending so teams get a ready subscription in hours, not weeks.
2. **What is the difference between Azure Policy and RBAC?** — RBAC controls *who* can perform an action. Policy controls *what* configuration is allowed, whoever deploys it, even an Owner.
3. **When do you use DeployIfNotExists, and what does it need?** — For auto-remediation such as diagnostic settings or private DNS records. The assignment needs a managed identity with the right roles, and existing resources need a remediation task.

**Gotchas**
- New policy assignments can take up to about 30 minutes to evaluate, and existing non-compliant resources are not fixed automatically. You need remediation tasks.
- A blanket Deny can break platform services that create resources on your behalf (for example AKS creating a public IP in its node resource group). Test in Sandbox and use scoped exemptions.
- Management-group depth is limited to six levels below the root. Keep the tree shallow.

**Scenario:** Finance wants cost per team, Security wants no public endpoints, and developers want freedom to experiment. Design the management groups, subscriptions and policies that satisfy all three.

**Done when:** you can draw the hierarchy from memory and say why each policy sits where it does.

**Resources:** [Azure landing zones (CAF)](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/) · [Azure Policy docs](https://learn.microsoft.com/azure/governance/policy/)

---

<a id="day-2"></a>
### Day 2 · Cloud · Identity: Entra ID, RBAC, Managed Identity, Key Vault

**Time:** ~3 h

**Why it matters:** identity is the security perimeter in the cloud. Almost every enterprise incident question comes back to it.

**Learn**
- **Entra ID objects:** users, groups, app registrations (the application definition) vs enterprise applications (the service principal in your tenant).
- **Azure RBAC:** role definitions, assignments and scope. Control-plane roles (Owner, Contributor, Reader) are separate from data-plane roles (Storage Blob Data Reader, Key Vault Secrets User).
- **Managed Identity:** system-assigned vs user-assigned. The app gets tokens from the local identity endpoint, and in code `DefaultAzureCredential` picks it up.
- **Key Vault:** RBAC mode vs legacy access policies, soft delete, purge protection, secret rotation, Key Vault references in App Service and Container Apps.
- **PIM:** just-in-time elevation for admin roles instead of standing access.

**Do**
- [ ] Create a Key Vault in RBAC mode and add a secret
- [ ] Deploy a tiny .NET API (App Service or Container Apps) with a system-assigned identity that reads the secret via `DefaultAzureCredential`
- [ ] Grant `Key Vault Secrets User` at the *vault* scope, not the subscription
- [ ] Repeat with a user-assigned identity and note when you would prefer it

**Interview questions**
1. **Managed Identity vs service principal vs workload identity federation?** — Use Managed Identity for workloads running in Azure: no secret to manage. Use a service principal with a certificate for systems outside Azure that can't federate. Use workload identity federation for GitHub Actions, Kubernetes and other identity providers: they swap a trusted token for an Entra token, again with no secret.
2. **System-assigned or user-assigned identity?** — A system-assigned identity lives and dies with its resource. A user-assigned identity has its own lifecycle: you can grant it permissions before deployment and share it across instances. That suits blue-green, scale sets and recreated resources.
3. **What is the difference between the control plane and the data plane?** — The control plane manages the resource (create, configure). The data plane is the content (blobs, secrets). Contributor on a storage account doesn't give Entra-based blob read access, but it can list the account keys.

**Gotchas**
- New role assignments can take several minutes to take effect, so the first calls return 403. Don't "fix" this by granting a broader role.
- Contributor can call `listKeys` on storage and other services, which is effectively full data access. Disable shared-key and local auth where you can.
- Purge protection can't be turned off once enabled, and a soft-deleted vault name blocks you from re-creating it.
- `DefaultAzureCredential` uses your `az login` identity locally, so code that works on your laptop fails in prod if the managed identity lacks the role.

**Scenario:** a developer committed a production connection string to a public repo. What do you do in the next hour, and what stops it happening again?

**Done when:** your app reads the secret with zero credentials in code, config or pipeline variables.

**Resources:** [Managed identities](https://learn.microsoft.com/entra/identity/managed-identities-azure-resources/overview) · [Key Vault docs](https://learn.microsoft.com/azure/key-vault/)

---

<a id="day-3"></a>
### Day 3 · AI · Python for a C# developer

**Time:** ~3 h

**Why it matters:** almost all AI engineering happens in Python. You need idiomatic, typed, tested Python, not "C# written in Python".

**Learn**
- **Environments and dependencies:** `venv` and `uv` (or Poetry), `pyproject.toml`, lock files, pinned versions.
- **Typing:** type hints, `Optional`, generics, `Protocol` (the closest thing to an interface), checking with mypy or pyright.
- **Data models:** `dataclass` for internal data, Pydantic models for validation at system boundaries (API input, LLM output).
- **Async:** `asyncio`, `async`/`await`. Unlike .NET there is one event loop thread, so a blocking call stalls everything.
- **Testing:** pytest fixtures, `parametrize`, mocking with `monkeypatch` or `unittest.mock`.

**Do**
- [ ] Create a project with `pyproject.toml`, ruff (lint/format), mypy and pytest
- [ ] Port a small C# class (for example a `MandateValidator`) to Python with type hints and 5 tests
- [ ] Write an async script that calls 3 HTTP endpoints concurrently with `httpx` and `asyncio.gather`

**Interview questions**
1. **What is the GIL and when does it matter?** — In standard CPython only one thread runs Python bytecode at a time. CPU-bound threads don't run in parallel, so use multiprocessing or native libraries. I/O-bound work is fine with async or threads. (Free-threaded builds exist but are not the default.)
2. **When do you use Pydantic vs a dataclass?** — Pydantic validates and coerces data from untrusted sources such as requests and LLM output. A dataclass is a lightweight internal container.
3. **How do you make Python dependencies reproducible?** — Pin versions with a lock file (uv/Poetry), build containers from the lock file, and scan dependencies in CI.

**Gotchas**
- Mutable default arguments (`def f(items=[])`) are shared across calls.
- A blocking library (`requests`, a sync DB driver) inside `async def` blocks the whole event loop.
- A coroutine you forget to `await` never runs. You only get a warning.
- `is` compares identity and `==` compares value. Small-integer caching hides bugs that use `is`.

**Scenario:** a FastAPI endpoint gets slow under load while CPU stays low. What is the likely cause, and how do you prove it?

**Done when:** tests and type checks pass in one command (`uv run pytest && uv run mypy .`).

**Resources:** [Python tutorial](https://docs.python.org/3/tutorial/) · [Pydantic docs](https://docs.pydantic.dev/latest/)

---

<a id="day-4"></a>
### Day 4 · AI · FastAPI service and first LLM call

**Time:** ~3 h

**Why it matters:** "wrap an LLM in a secure, observable API" is the most common first task for an AI engineer in an enterprise.

**Learn**
- **FastAPI:** path operations, Pydantic request/response models, dependency injection with `Depends`, async routes, auto-generated OpenAPI.
- **Configuration:** `pydantic-settings` reading environment variables. No secrets in code.
- **Azure OpenAI basics:** resource, *deployments* (your deployment name is not the model name), API versions, chat messages (system/user/assistant).
- **Parameters and usage:** `max_tokens`, temperature, and the `usage` field (prompt vs completion tokens) for cost tracking.
- **Keyless auth:** Entra ID via `DefaultAzureCredential` token provider instead of API keys.

**Do**
- [ ] Build `POST /summarize` that calls Azure OpenAI (or OpenAI) with Entra auth and returns the summary plus token usage
- [ ] Add a `/health` endpoint, structured JSON logging and a request timeout
- [ ] Write tests with the LLM client mocked
- [ ] Write a Dockerfile

**Interview questions**
1. **How does an app authenticate to Azure OpenAI without keys?** — Give the app a Managed Identity with the `Cognitive Services OpenAI User` role and request tokens through the Azure Identity SDK. Disable key-based (local) auth on the resource.
2. **What drives the cost and latency of an LLM call?** — Cost is input tokens + output tokens × the model's price. Latency is dominated by the number of output tokens and the model size, plus time to first token.
3. **How do you handle 429 (rate limit) errors?** — Retry with exponential backoff that honours `retry-after`. Size quota (tokens and requests per minute) per deployment. Spread load across deployments or regions, often through a gateway.

**Gotchas**
- Passing the model name where the API expects the *deployment* name.
- Quotas are per subscription, per region and per model, so a load test in one environment can starve another.
- No client timeout means a hung request ties up a worker.
- Logging full prompts and responses can put customer PII into shared logs.

**Scenario:** the business wants "ChatGPT for our policies" by Friday. What is your MVP, and which three things do you refuse to skip?

**Done when:** `curl` to `/summarize` returns a summary and token counts, and the code holds no API key.

**Resources:** [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/) · [Azure OpenAI docs](https://learn.microsoft.com/azure/ai-services/openai/)

---

<a id="day-5"></a>
### Day 5 · DevOps · Git workflows and Linux essentials

**Time:** ~3 h

**Why it matters:** DevOps interviews often start with Git recovery and Linux troubleshooting before any tool talk.

**Learn**
- **Branching:** trunk-based development vs GitFlow; pull requests, branch protection, CODEOWNERS, conventional commits.
- **Git recovery:** rebase vs merge, revert vs reset, `reflog`, `cherry-pick`.
- **Linux basics:** filesystem layout, permissions (`chmod`/`chown`, octal), users and groups, `sudo`.
- **Processes and services:** `ps`, `top`, signals (`SIGTERM` vs `SIGKILL`), `systemctl`, `journalctl`.
- **Networking commands:** `ip`, `ss`, `curl`, `dig`/`nslookup`, `traceroute`.

**Do**
- [ ] Protect `main` in a GitHub repo (PR required, 1 review), add CODEOWNERS
- [ ] Practise an interactive rebase on a feature branch and a `git revert` on main
- [ ] On a Linux VM or WSL, run a small script as a `systemd` service and read its logs with `journalctl -u`
- [ ] Find which process holds port 8080 (`ss -ltnp`) and check a DNS name with `dig`

**Interview questions**
1. **Trunk-based or GitFlow for microservices with CI/CD, and why?** — Trunk-based: short-lived branches, feature flags, frequent small merges. GitFlow's long-lived branches slow down continuous delivery.
2. **Revert or reset on a shared branch?** — Revert, because it adds a new commit that undoes the change. Reset rewrites history and breaks everyone who already pulled.
3. **A service fails to start after a reboot. How do you troubleshoot?** — `systemctl status`, `journalctl -u <svc> -b`, check the unit file and its dependencies, permissions, port conflicts and environment differences.

**Gotchas**
- Force-pushing rewritten history to a shared branch.
- `chmod 777` as a "fix" for a permissions problem.
- Windows CRLF line endings break bash scripts (`/bin/bash^M: bad interpreter`).
- Files created as root inside a container, then "permission denied" when the app runs as non-root.

**Scenario:** someone force-pushed over the release branch and commits are missing. How do you recover them?

**Done when:** you can explain how you would recover commits with `reflog` without looking it up.

**Resources:** [Pro Git book](https://git-scm.com/book/en/v2) · [Linux Journey](https://linuxjourney.com/)

---

<a id="day-6"></a>
### Day 6 · DevOps · Docker fundamentals

**Time:** ~3 h

**Why it matters:** containers are the unit of deployment everywhere else in this plan.

**Learn**
- **Images vs containers:** layers, build cache, registries.
- **Dockerfile:** `FROM`, `COPY`, `RUN`, `ENV`, `EXPOSE`, `ENTRYPOINT` vs `CMD`, `.dockerignore`.
- **Multi-stage builds:** .NET SDK stage → ASP.NET runtime stage; Python builder → slim runtime.
- **Runtime:** bridge networking, port mapping, volumes vs bind mounts.
- **Docker Compose** for running several services locally.

**Do**
- [ ] Write multi-stage Dockerfiles for the .NET API and the FastAPI service, and compare image sizes
- [ ] Add `docker-compose.yml` with both APIs plus Postgres and Redis
- [ ] Run both apps as a non-root user

**Interview questions**
1. **ENTRYPOINT vs CMD?** — ENTRYPOINT is the executable. CMD supplies default arguments that `docker run` can override. Use exec (JSON) form so signals reach the process.
2. **How do you make image builds faster?** — Order layers from least to most frequently changed. Copy `*.csproj`/lock files and restore before copying source. Use BuildKit cache mounts and a good `.dockerignore`.
3. **Container vs VM?** — Containers share the host kernel: process isolation, fast start, small footprint. VMs virtualise hardware with a full OS: stronger isolation, heavier.

**Gotchas**
- The `latest` tag in production makes deployments unreproducible.
- Secrets passed as build args or copied in stay in the image history.
- An app listening on `127.0.0.1` inside a container is unreachable from outside. Bind to `0.0.0.0`.
- The app is PID 1 and ignores `SIGTERM`, so you lose graceful shutdown and requests.

**Scenario:** an image is 1.8 GB and takes 12 minutes to build. Walk through how you'd fix both.

**Done when:** `docker compose up` brings the whole stack up from a clean machine.

**Resources:** [Docker get started](https://docs.docker.com/get-started/) · [.NET container images](https://learn.microsoft.com/dotnet/core/docker/introduction)

---

<a id="day-7"></a>
### Day 7 · .NET + Design · Clean Architecture refresh and design-interview framework

**Time:** ~2 h

**Why it matters:** your .NET depth is a differentiator. This day keeps it sharp and gives you a repeatable structure for every design interview.

**Learn**
- **Clean Architecture:** the layers and the dependency rule, and where EF Core and external clients belong.
- **Modular monolith vs microservices:** decide by team size, deployment independence and domain boundaries.
- **DDD essentials:** aggregates protect invariants; bounded contexts define model boundaries.
- **Design-interview framework:** requirements → estimates → API → data model → high-level design → deep dive → bottlenecks and trade-offs.
- **Back-of-envelope maths:** requests per second, storage, bandwidth.

**Do**
- [ ] Create (or refresh) the mandate service skeleton: Domain / Application / Infrastructure / API projects
- [ ] 45-minute timed drill: design a URL shortener with the framework and save your notes as `design/url-shortener.md`

**Interview questions**
1. **Microservices or modular monolith for a new product with one team?** — A modular monolith: clear module boundaries, one deployment, easy to split later. Microservices add operational cost that one team can't absorb.
2. **What belongs in the domain layer?** — Entities, value objects, aggregates, domain events and business rules. No EF, HTTP or infrastructure concerns.
3. **Estimate storage for 100 million short URLs over 5 years.** — About 500 bytes per record (URL, key, metadata) × 100M ≈ 50 GB before replicas and indexes. State your assumptions out loud.

**Gotchas**
- An anemic domain model: all logic in services and entities that are just property bags.
- Splitting services by technical layer instead of business capability, or sharing one database across services.
- In interviews, drawing boxes before you've clarified requirements and scale.

**Scenario:** the CTO wants the monolith split into 30 microservices next quarter. How do you respond?

**Done when:** you can run the design framework from memory in a timed drill.

**Resources:** [.NET architecture guides](https://learn.microsoft.com/dotnet/architecture/) · [System Design Primer](https://github.com/donnemartin/system-design-primer)

---

<a id="day-8"></a>
### Day 8 · Build + Defend · Secure baseline, end to end

**Time:** ~4 h

**Why it matters:** this day turns the sprint's pieces into one portfolio item and rehearses how you'll talk about it.

**Do**
- [ ] Deploy both containers (Container Apps or App Service) using Managed Identity to read Key Vault and pull from ACR
- [ ] Verify the three policies block a non-compliant deployment (try deploying a public IP)
- [ ] README: identity diagram, policy table, cost note
- [ ] `docs/adr/001-container-apps-vs-app-service.md`
- [ ] Record yourself answering the three questions below, 5 minutes each

**Interview questions**
1. **20 application teams are moving to Azure. How do you structure subscriptions, identity and guardrails?** — Cover management groups by archetype, subscription vending, Entra groups mapped to RBAC roles, PIM for admins, policy initiatives at management-group level, and a central connectivity hub.
2. **Explain Managed Identity vs service principal vs workload identity federation with a real example of each.** — Managed Identity: Container App → Key Vault. Certificate-based service principal: an on-prem batch job. Federation: GitHub Actions → Azure.
3. **A connection string was committed to Git. What do you do now and later?** — Now: rotate the secret immediately, assess access logs, then purge it from history. Later: push protection and secret scanning, Managed Identity instead of secrets, and pre-commit hooks.

**Gotchas**
- Container Apps needs the `AcrPull` role on its identity to pull images. Without it you only see an image pull failure.
- Policy evaluation delay can make the test deployment succeed the first time. Wait, then retry.

**Done when:** a stranger could clone the repo, read the README and understand the identity and governance model in 3 minutes.
