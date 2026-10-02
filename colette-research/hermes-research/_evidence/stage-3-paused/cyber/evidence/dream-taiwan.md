August 12, 2026

# Inside a Multi-Agent AI Framework Used to Compromise Government Entities in Asia

Dream Research Labs

## Executive Summary

AI-enabled offensive operations are now at an inflection point. This is driven by the convergence of three curves:

- Model capability keeps climbing, and it climbs on open weights that puts frontier-adjacent reasoning in the hands of any operator with hardware
- Agentic harnesses have matured from demonstrations into operational scaffolding: planning loops, parallel dispatch, persistent memory, and structured after-action reporting that let a model run an intrusion campaign rather than answer questions about one
- Guardrails, the last practical constraint, hold only against operators who ask honestly.

What follows is but one concrete example of what appears to be a near-autonomous attack, running off readily available harnesses and models and aimed at a nation state. Some details on the attack were initially shared with the [Financial Times](https://www.ft.com/content/7d2ab3e0-9085-48f6-b38a-d90260d58795?syn-25a6b1a6=1).

In roughly four days, the agentic attacker produced 1,395 files, 85 cracked credentials, thousands of exfiltrated personnel records, and gained a persistent foothold inside state infrastructure. It spells out one thing loudly - **the cost of running a competent attack has collapsed, but the cost of defending against one has not.**

_Dream follows responsible disclosure practices. Impacted organizations were notified prior of our findings to publication and given time to remediate and we avoid identifying the targeted entities or the operator behind this framework._

## The Anatomy of a Government AI Attacker

In early July 2026, DREAM Lab's Threat Research team uncovered the complete operational workspace of an autonomous AI attack framework that had been actively conducting intrusion campaigns against government entities in Asia. The archive, spanning over 160 megabytes and 1,395 files, reveals a multi-agent AI system that achieved confirmed, real-world compromises against state infrastructure.

The framework — built on the [Hermes](https://hermes-agent.org/) and [OpenClaw](https://openclaw.ai/) agents — deploys up to 8 lettered sub-agents in parallel per wave (Agent A through Agent Q observed across the campaign), each assigned to distinct targets and attack techniques. Across 12 documented attack waves conducted over approximately four days (July 1-4, 2026), these agents autonomously cracked government employee credentials, exfiltrated hundreds of personnel records from unauthenticated API endpoints, discovered a signature validation flaw in the government's personal authentication service, and installed persistent backdoors on government web applications.

What distinguishes this framework from attack tooling that we've seen before is its operational intelligence:

- **Bayesian prioritization**: Posterior probability scoring to continuously rank and reprioritize 14 parallel attack chains, focusing effort on the highest-value targets first
- **Autonomous research**: "Learning Cycles" that search vulnerability databases, GitHub repositories, and security publications for new exploitation techniques when existing methods are blocked
- **Feedback loops**: Structured after-action reporting that feeds results from each wave back into the planning for the next, enabling the framework to adapt mid-operation without human intervention
- The framework's own safety guardrails — LLM model refusals — were bypassed by framing all activity as "authorized penetration testing".

Linguistic analysis of the operational documentation — which code-switches between Simplified Chinese in internal status reports and Traditional Chinese in target-facing analysis — points to a Chinese-language operator.

This report details the framework's architecture, its confirmed impact, and the paradigm shift it represents for defenders: the era of AI-orchestrated, parallel, autonomously adaptive cyber operations against government infrastructure is a reality that will only get more dangerous, with offensive capabilities that outstrip most traditional defensive capabilities.

## Attack Chain: What the Attacker Successfully Achieved

![](https://cdn.prod.website-files.com/6a146a5aca0b1a41051708a5/6a745c3fea190d933b884b91_attack_chain_diagram_editable-01.png)

The Full Attack Chain

### Step 1: Reconnaissance: Understanding the Target

The framework began by automatically mapping the entire government ecosystem. It downloaded and decompiled JavaScript bundles from an Angular-based government portal, extracting every embedded URL, API endpoint, OAuth client ID, and Keycloak configuration object hidden in the compiled code. From this single starting point, it identified 21 connected government systems and mapped the full national SSO architecture — 6 sub-realms, all OIDC endpoints, 2 RSA signing keys, and every supported authentication flow.

On one target alone, it discovered 36+ API endpoints spanning account management, user data retrieval, file upload, and administrative functions — many completely unauthenticated. **Critically, it found that one of the systems exposed its entire user database without any authentication — thousands of employee records including names, departments, and SSO account IDs**.

### Step 2: SDK Harvesting: Accelerating Reconnaissance

In what appears to be a fully autonomous decision, a URL extracted from the JS bundles led the framework to a GitBook documentation portal hosting the national SSO integration guide. Using GitBook's built-in features (`llms.txt` for page indexing, `.md` suffix for raw content), it systematically scraped the documentation, found a download link, and obtained two SDK integration example projects (Java Spring Boot and ASP.NET Core 8.0) — client-side demo applications showing how agencies connect to the national SSO.

The framework then ran an AI-powered static analysis (its `Local-LLM-SAST-0day` methodology) on the SDK sample code, identifying potential security issues — including an open redirect (CSRF disabled + unvalidated `redirectUri` parameter) and an unauthenticated authorization code-to-token exchange pattern. However, none of these findings translated into confirmed exploits against the live system. Cross-referencing the SAST results against the framework's own final validated vulnerability list shows zero overlap — the actual breaches came from server-side flaws (backdoor endpoints, unsigned JWT acceptance, unauthenticated APIs) discoverable through standard black-box testing without any SDK knowledge.

### Step 3: Initial Access: Multiple Ways In

With the attack surface mapped, the framework found several entry points running in parallel:

**Authentication backdoors**: On a government web application, it discovered three hidden API endpoints that accept any request body and return a valid authenticated session. No credentials needed — these were developer debug endpoints left exposed in production.

**Automated credential spraying**: Using the employee usernames harvested from the unauthenticated users API endpoint, the framework attacked the department's office automation portal. The portal was protected by CAPTCHA, but the framework used Tesseract OCR to solve each small CAPTCHA image with 100% accuracy. It tested predictable password patterns based on each employee's ID — capitalizing or decorating the username with common symbols — and cracked 85 accounts across multiple spray rounds (an initial 12, then 73 more as additional patterns were discovered).

**JWT signature bypass**: A government API accepted JWT tokens with the algorithm field set to none, meaning anyone could forge valid identity tokens without knowing the signing key.

### Step 4: Lateral Movement and Persistence

The cracked employee credentials from Step 3 were systematically tested against every other internal system connected via Single Sign-On. Each internal system exposed a dedicated SSO entry point that automatically trusted the office automation session (from step 3) — no additional authentication, MFA, or user confirmation required.

84 of the 85 cracked accounts (98.8%) successfully authenticated to the department's internal information system via an SSO bridge endpoint, gaining access to internal dashboards, equipment management interfaces, and personnel statistics pages. The framework automated this at scale, testing each credential against multiple connected systems in parallel.

The framework also uploaded a web shell through an unrestricted file upload API, placing it at a known path on the server. However, a secondary layer of Forms Authentication blocked execution — a partial success that stopped short of remote code execution.

### Step 5: Data Exfiltration

Combining backdoor access, cracked credentials, and unauthenticated API endpoints, the framework extracted:

- **2,564+ personnel records**: 1,409 employees (name, department, SSO ID), 916 users from an unauthenticated API, and 239 legal professionals from an unauthenticated Ministry of Justice endpoint
- **Complete user database**: full JSON export of all department system users
- **Internal architecture**: 7 SSO client secrets (rotated but naming conventions revealed), 6 internal database credentials (MSSQL, Oracle, Sybase), and internal network IP ranges

### Step 6 : Supply Chain Expansion: Pivoting to Vendors

The attacker didn't stop at primary targets. It expanded the operation to government IT supply chain vendors, a nuclear safety agency, a government email system, and 7+ energy sector companies — scanning them all in parallel for misconfigurations, exposed admin interfaces, and exploitable vulnerabilities.

### The Architecture: Hermes and OpenClaw

The framework operates under two workspace identifiers — .hermes and .openclaw — with reports generated into structured paths.

Each sub-agent is assigned a letter designation and a specific mission — from credential theft to API exploitation to supply chain reconnaissance. In a single attack wave, we observed up to 8 agents deployed concurrently, each targeting a different attack surface:

![](https://cdn.prod.website-files.com/6a146a5aca0b1a41051708a5/6a745c562d47aa78246d912f_attack_chain_diagram_editable-02.png)

Hermes and OpenClaw Usage

Across the campaign's 12 documented attack waves, we identified agents labeled A through Q, with up to 8 deployed concurrently in a single wave (dispatched in 3 batches). The sheer volume of output — 1,395 files produced in approximately four days — is consistent with heavy automation far beyond what a human operator could produce alone.

### The Bayesian Brain: A Two-Layer Probabilistic Decision Engine

Perhaps the most striking feature of this framework is its use of Bayesian posterior probability scoring — not as a single metric, but as a two-layer decision engine that operates at both the individual vulnerability level and the strategic attack chain level. In other words, this was not a “spray and pray” approach but a deliberate strategically drive attack that dynamically reprioritized its approach.

**Layer 1: Individual Vulnerability Scoring**

The framework's triage report reveals the first layer — an autonomous triage system that scores each individual finding using a formal Bayesian model. The methodology starts every vulnerability at an uninformative prior of P=0.50, then updates based on evidence using explicit likelihood ratios:

| Evidence type | Likelihood ratio |
| --- | --- |
| Tool scan positive | LR+ = 6.0 |
| Manual curl confirmation | LR+ = 10.0 |
| Impact assessment positive | LR+ = 3.0 |
| WAF/constraint present | LR− = 0.30 |

The resulting posterior determines what happens next:

| Posterior | Action |
| --- | --- |
| P > 0.95 | Confirmed exploitable — promote to attack chain |
| P > 0.70 | High confidence — allocate more testing resources |
| P > 0.50 | Needs more evidence — queue for next wave |
| P < 0.30 | Discard — stop investing effort |

**Layer 2: Attack Chain Scoring**

Once individual vulnerabilities are triaged, the framework connects them into multi-step attack paths and applies a second probability layer. The explicit formula from the archive:

> **P\_success = P\_chain × (1 - P\_blocker)**

Where:

P\_chain = confirmed steps / total steps in the chain

P\_blocker = probability of an insurmountable blockerScoring thresholds:

- **95%+** = all critical steps already confirmed and directly exploitable
- **60-94%** = most steps confirmed, minor attempts needed
- **20-59%** = partial confirmation, significant blockers present
- **5-19%** = chain exists but critical conditions are missing
- **<5%** = insurmountable blocker identified

‍

**Worked example — SSO Lateral Movement, rated 99%:**

The framework assembled this chain from three separately confirmed findings: (1) an unauthenticated user list yielding thousands of employee accounts, (2) a password spray cracking multiple accounts, and (3) SSO token acquisition confirming lateral pivot capability. The precondition table:

| Precondition | Status |
| --- | --- |
| OA SSO credentials | ✅ Already obtained |
| OA portal online | ✅ Responding |
| Target internal system online | ✅ Responding |

All critical steps were already tested and working. The only theoretical blocker — the target going offline — had near-zero probability since it was actively responding:

- **P\_chain** = 3/3 confirmed steps = 1.0
- **P\_blocker** = ~0.01 (target going offline)
- **P\_success** = 1.0 × (1 - 0.01) = **0.99 = 99%**

The framework later validated this prediction: 98.8% of the accounts successfully pivoted to the internal system.

### The Learning Engine: Mid-Operation Technique Research

The framework also implements dedicated research phases it calls "Learning Cycles" — autonomous sessions where the AI system searches vulnerability databases, GitHub repositories, and security research publications for techniques specifically applicable to its target government's infrastructure.

We found five documented learning cycles (v1 through v5), each producing structured reports of newly discovered techniques categorized by:

- Relevance to the current target environment
- Available public exploits or proof-of-concept code
- Probability of success given current defenses
- Implementation priority

The research isn't limited to generic techniques — it is tailored to the specific target environment. The learning cycles include dedicated sections on known vulnerability patterns in the target government's systems, cataloging documented CVEs in country-specific products and common weaknesses observed across government portals. The framework researches its target's known weak spots also from published security literature.

### Self-Correction: When the AI Got It Wrong

One of the most operationally significant behaviors in the archive is the framework's ability to identify and discard its own mistakes. The final 12-wave summary explicitly lists 7 false positives alongside the confirmed real vulnerabilities — errors the framework made and then caught through its own verification process.

The most instructive example is the SQL injection false positive. During early testing, the framework reported a blind SQL injection in a registration endpoint's nickname field. Its evidence: a 21-second response delay that the agent interpreted as a successful SLEEP(5) injection. Its verification protocol requires "physical confirmation". When the agent retested the endpoint methodically, it discovered the 21-second delay was caused by SMTP timeout — the server was trying to send a verification email, not executing injected SQL. The finding was reclassified as a false positive and permanently excluded.

The final summary's notation — 8个真实漏洞(物理确权+3+3交叉验证) — means each confirmed finding required not just the discovering agent's verification, but two additional rounds of three independent agent re-verifications. A security finding had to survive six separate retests before the framework would include it in its confirmed findings.

## Conclusion

AI-powered attacks are not new and, as we recently shared, [we don't believe that governments are ready for this emerging threat](https://dreamgroup.com/blog/governments-are-not-ready-for-autonomous-ai-attacks). This threat is not limited to technical threats; AI is also capable of [replacing the nation-state cyber back office](https://dreamgroup.com/blog/the-intelligence-factory-how-ai-is-replacing-the-nation-state-back-office).

We increasingly see threat actors leveraging AI for autonomous offensive operations. But building a system that actually works at this level takes more work than "just" running a model. It demands careful adjustment to the specific task, optimization of agent coordination, and fine-tuning of decision logic - the kind of sophistication evident in this framework's Bayesian prioritization, self-correction loops, and adaptive research cycles.

That same sophistication now needs to exist on the defensive side, but, for the most part, [governments are not ready for autonomous AI attacks](https://dreamgroup.com/blog/governments-are-not-ready-for-autonomous-ai-attacks).

Just as defenders have always asked which assets are most vulnerable and what an attacker is most likely to target next, security products must shift toward an AI-native approach, one that reasons probabilistically about which attack path is most likely, which exposure will be exploited next, and where defensive resources should concentrate before the next wave hits.

‍

[**Additional research about national sovereign AI, cyber-security and more is available here.**](https://dreamgroup.com/research-and-news)

## Get Dream's research and briefings first

Email

Yes, send me Dream updates. I can unsubscribe at any time. [Privacy Policy](https://dreamgroup.com/privacy-notice)

Thanks, you're in.

Oops! Something went wrong while submitting the form.

### Fill out the form to get in touch with our Expert Team.

First Name

Last Name

Company

Job title

Phone

Email

CategorySelect a Category...CareerPartnershipMediaRequest demoOther

Email

Thank you!

Your submission has been received!

Oops! Something went wrong while submitting the form.