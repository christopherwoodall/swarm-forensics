# Qualified and boundary cases

Research cutoff: 2026-10-01. Citation IDs belong to the Stage 3 ledger, not the parent collection.

Useful comparators, not additions to a count of independently verified field swarms: one platform-integrity incident with uncertain agent authorship, and one evaluation-heavy executed optimization project.

## S3-MOLTBOOK — Moltbook launch-window identity and shared-content integrity failure

Classification: Real platform technical investigation; autonomous-collective attribution bounded.

### 1. What happened

Moltbook launched January 28, 2026.[31]
Wiz reported a production Supabase authorization failure, access to authentication tokens/private messages and successful modification of an existing post; its timeline runs January 31 through final restrictions at February 1, 01:00 UTC.[24]
404 reported the exposure January 31; Wiz/Reuters February 2.[27][24][25]

### 2. Why it is relevant

A forensic counterexample to trusting ‘agent society’ appearances: identity failure allowed human-authored material and account impersonation, while mutable shared content could expose readers to poisoned traces.[24][25]
Useful for separating platform connectivity, AI authorship and autonomous coordination.

### 3. What evidence exists

Wiz supplies schema-level findings, a demonstrated post change and a remediation sequence; Reuters interviews Wiz and separately quotes researcher O’Reilly, while explicitly declining to authenticate bot authorship.[24][25]
404’s saved body contains only its public opening; MITTR adds observed reporting and expert interpretation, not an agent-by-agent provenance audit.[27][31]

### 4. Autonomy and control topology

Wiz observed about 1.5 million agent registrations associated with roughly 17,000 owner accounts—not 1.5 million verified autonomous actors.[24]
A central platform mediated participation; individual runtime permissions, prompts and autonomy varied or were unknown, and humans could impersonate participants.[24][25]
Human provisioning alone does not prove every subsequent action needed explicit human approval.

### 5. Coordination substrate

Posts, comments, votes/reputation and private messaging formed a central social substrate.[24]
Wiz demonstrated that stored posts could be changed without authentication.[24]
That establishes a writable shared-trace attack surface, not an observed cascade in which downstream agents obeyed a payload.

### 6. Strong claims versus speculative claims

Strong: disclosure of read/write failure and inability to verify exclusively AI participation.[24][25]
Unknown: malicious downstream propagation, shared goals, independent cross-agent organization and true autonomous population. Keep units distinct: Reuters reports emails of more than 6,000 owners; Wiz reports 35,000 email addresses across exposure surfaces—neither equals the owner-account census.[24][25]

### 7. Distinctness

One launch-window platform incident, not separate swarms for Wiz, O’Reilly/404, Reuters and MITTR. Distinct from controlled provider marketplaces and excluded wiki/PixelLeak cases: this is compromised authentication/content integrity, without confirmed autonomous propagation. Retain as a boundary/security event, not a positive demonstration of decentralized emergence.

## S3-KERNELS — Cursor/NVIDIA CUDA-kernel optimization

Classification: executed workload-derived optimization evaluation; not documented production deployment.

### 1. What happened

April 14, 2026 disclosure: a three-week multi-agent optimization experiment over 235 workload-derived problems evaluated on 27 Blackwell B200 GPUs.[19]
Retain as an executed technical experiment, not deployed production inference infrastructure.[19]
Exact activity boundaries are absent.[19]

### 2. Why it is relevant

A planner distributed and rebalanced autonomous workers using performance metrics.[19]
The system repeatedly benchmarked, debugged and optimized kernels—clear feedback-driven coordination beyond parallel text generation.[19]

### 3. What evidence exists

Provider collaboration account plus a public results repository listing kernel solutions, per-workload/per-problem metrics and traces.[19][20]
Individual CSVs and trace bodies were not examined here; this is not an independent rerun.[20]

### 4. Autonomy and control topology

Hierarchical planner–worker operation; the operator reports no developer intervention in the optimization loop.[19]
Human-provided problems, evaluator, documentation and protocol define the environment.[19]
The source says all 235 problems were addressed in a single run, but separately specifies two language-separated runs, CUDA C/inline PTX and CuTe DSL.[19]
Count one experiment family; do not manufacture 235 swarms or treat the headline as clearly language-specific.[19]

### 5. Coordination substrate

A single Markdown protocol specified output formats, rules and tests; benchmark results informed work reallocation and subsequent optimization.[19]
The evaluator was designed to invalidate implausible hardware performance, including caching-based cheating.[19]
Detailed scheduler telemetry and exact agent count are absent.[19]

### 6. Strong claims versus speculative claims

Reported 1.38× geometric-mean speedup is versus single-agent-optimized PyTorch, not uniformly best human libraries.[19]
Only 149/235 problems outperformed baselines; median SOL score was 0.56, and an illustrated GEMM reached 86% of cuBLAS performance.[19]
One attention-kernel substitution reportedly improved SGLang time-to-first-token by 3%—a bounded integration test, not fleet-wide adoption.[19]
Universal expert superiority, causal benefits of coordination and scaling gains from more GPUs remain unestablished.[19]

### 7. Distinctness

Same Cursor harness lineage, but a later, explicitly separate NVIDIA workload/optimization episode rather than another outcome from the browser post.[19]
Mechanism and measurement are useful comparators; lower priority because the setting remains evaluation-heavy and its independent agent population is not documented.[19]

## Sources

[19] https://cursor.com/blog/multi-agent-kernels — Speeding up GPU kernels by 38% with a multi-agent system
[20] https://github.com/anysphere/kernel-optimization-results — Multi-Agent CUDA Kernel Optimizations (anysphere/kernel-optimization-results)
[24] https://www.wiz.io/blog/exposed-moltbook-database-reveals-millions-of-api-keys — Hacking Moltbook: AI Social Network Reveals 1.5M API Keys | Wiz Blog
[25] https://www.reuters.com/legal/litigation/moltbook-social-media-site-ai-agents-had-big-security-hole-cyber-firm-wiz-says-2026-02-02 — 'Moltbook' social media site for AI agents had big security hole, cyber firm Wiz says | Reuters
[27] https://www.404media.co/exposed-moltbook-database-let-anyone-take-control-of-any-ai-agent-on-the-site — Exposed Moltbook Database Let Anyone Take Control of Any AI Agent on the Site
[31] https://www.technologyreview.com/2026/02/06/1132448/moltbook-was-peak-ai-theater — Moltbook was peak AI theater | MIT Technology Review
