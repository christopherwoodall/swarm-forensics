Introducing the Agents API \| OpenAI

September 10, 2026

[Product](https://openai.com/news/product-releases/) [API](https://openai.com/stories/api/)

# Introducing the Agents API

Build and run cloud agents with the Codex harness, fully managed by OpenAI.

00:00

Listen to article5:04

Share

As we’ve scaled Codex and ChatGPT for Work to millions of people around the world, we’ve learned what it takes to make long-running agents work well in practice. Useful agents need a powerful harness that manages context, uses tools efficiently, and coordinates subagents. They also need infrastructure that keeps them running reliably for days, with environments where they can work with files, run code, and save intermediate results.

Today, we’re introducing the [Agents API⁠(opens in a new window)](https://developers.openai.com/api/docs/guides/agents-api/overview) in public beta, bringing that same harness and infrastructure that powers Codex to developers through a simple, flexible API.

## What our customers are saying about Agents API

1 of 8

> “With the Agents API, our evaluation score went from 0.71 to 0.85. The subagent support in the API is great and drastically sped up our workflow. Previously it was pretty cumbersome to observe and orchestrate subagents in our old setup but the new APIs gave us a 4x latency reduction. We spent a long time trying to optimize for this and the subagent flows were a huge out-of-the-box lift.”

Jack Weissenberger, CTO, Ciridae

> “Transforming real-world businesses means deploying AI into workflows of every shape. Agents API supplies the harness; the environment, context, and UX stay ours. With our AI platform Nexus we now stand up agents in hours across industries, from residential services to architecture.”

Rasmus Wissmann, CTO, Long Lake

> “The Agents API has enabled us to think differently about how we can architect complex, multi-step workflows. We used to write prompt chains and manage our own set of tool calls, but now we can use agents directly in our code much like how Codex works on your laptop. It’s already helped us solve several problems that would’ve otherwise required us to build custom agent infrastructure.”

Cole Striler, Director of Engineering, WithCoverage

> “After migrating our case review workflow to the Agents API, we saw a 60% reduction in cost per case, lower latency, and significantly improved token efficiency while maintaining existing performance.”

Bhavyansh Sabharwal, Member of Technical Staff, SafetyKit

> “What stood out in our testing was how naturally the Agents API handled bursty workloads. We could fan out work across hundreds of agents, run them asynchronously, and collect the results later, without keeping infrastructure idle between peaks.”

Dmitry Khanukov, Co-founder & CTO, Dwelly

> “Earning customers’ trust is critical in financial services. OpenAI’s Agents API enables us to build more reliable agents, giving customers the confidence to use them in production. By separating the agent harness from the sandbox, we reduced failed agent responses by 86%.”

Serhii Shchoholiev, Lead Engineer, Hypha

> “The Agents API handled the implementation, independent review, remediation, and real-browser validation in a real, active repository. Overall, the agent’s engineering quality was very strong.”

Maks Operlejn, Senior ML Engineer, deepsense.ai

> “At Nash, we deploy thousands of long-running AI agents that manage hundreds of millions of deliveries across global logistics networks. OpenAI’s Agents API gives us the durable session and orchestration layer we need for agents operating continuously in production managing context, recovery, and multi-step execution, while Nash provides the tools and execution environment that connect them to the physical world. This lets our agents reason, act, recover, and collaborate across complex workflows that can span hours or days. These agents are production infrastructure running mission-critical logistics operations for our partners.”

Aziz Alghunaim, Co-founder & CTO, Nash.ai

- Ciridae
- Long Lake
- WithCoverage
- SafetyKit
- Dwelly
- Hypha
- deepsense.ai
- Nash.ai

## Build cloud agents with a single API call

With the Agents API, you can create a production-ready agent in a single API call by specifying the task, model, tools, and environment:

#### JavaScript

`1import OpenAI from "openai";

2

3const client = new OpenAI();

4

5const session = await client.beta.agents.sessions.create({

6  agent: {

7    model: "gpt-6-astra",

8    tools: [\
\
9      {\
\
10        type: "mcp",\
\
11        server_label: "observability",\
\
12        transport: {\
\
13          type: "http",\
\
14          server_url: "https://observability.example.com/mcp",\
\
15        },\
\
16      },\
\
17    ],

18    multi_agent: { enabled: true, max_concurrent_subagents: 3 },

19  },

20  vault_ids: ["vault_YOUR_VAULT_ID"],

21  environment: {

22    type: "openai_hosted",

23    capability_directories: ["/workspace/capabilities/skills"],

24  },

25  input:

26    "Investigate service-api’s elevated 5xx rate over the last 30 minutes. " +

27    "Delegate deployment, error, and dependency analysis to subagents. " +

28    "Save findings, evidence, and recommended mitigation in /workspace/outputs.",

29});

`

OpenAI hosts and maintains the harness. You choose the agent’s compute environment: in an OpenAI-managed sandbox, on your own infrastructure, or with one of our sandbox partners. The Agents API gives you a strong foundation for building agents on top of our optimized agent harness and infrastructure, so you can focus on the tools, knowledge, and workflows that make your agent unique.

![An application sends tasks to the Agents API and receives events and output. The Agents API runs the managed Codex harness, sending tool calls to a sandbox and receiving tool results. The application controls self-hosted compute.](https://images.ctfassets.net/kftzwdyauwt9/7oiK2YZ2Dx7hujorDOOj6R/47ba63c3fc77253118db0dbba04e19e4/agents-api_16x9_light_1.png?w=3840&q=90&fm=webp)

Agents API powers your agents with the same harness and infrastructure behind Codex.

## Choose your agent environment

Different workloads need different compute, storage, and deployment options. The Agents API lets you choose a sandbox that fits your application.

We’re [partnering with ecosystem providers⁠(opens in a new window)](https://developers.openai.com/api/docs/guides/agents-api/environments/self-hosted#sandbox-providers), including Blaxel, Cloudflare, Daytona, DigitalOcean, E2B, Modal, Oracle, Runloop, and Vercel, to provide first-class integrations for a range of needs:

- Fully managed environments or deployments within your VPC

- Specific file and secret storage mechanisms

- Different CPU, GPU, and memory configurations, with performance, cold-start, and cost profiles to match your company’s workflow.


![Sandbox partners: Modal, Cloudflare, Daytona, Blaxel, Runloop, Vercel, Oracle, E2B, and DigitalOcean.](https://images.ctfassets.net/kftzwdyauwt9/7C7hj4p2tMhGIzv52HcvNR/f8f03bc716d9ad680b96dce7bfa66ab2/partners-light.png?w=3840&q=90&fm=webp)

The Agents API offers first-class integrations with popular ecosystem providers.

## OpenAI hosted sandboxes

For developers who want to get started quickly and scale efficiently, we’re also introducing the [OpenAI hosted sandbox⁠(opens in a new window)](https://developers.openai.com/api/docs/guides/agents-api/environments/openai-hosted). This leverages the same sandboxing infrastructure that powers Codex and ChatGPT.

OpenAI provisions and manages the sandbox, giving your agent a secure and performant environment to run code, work with files, and produce artifacts. These sandboxes can be flexibly configured with your files, packages, skills and plugins to give the agent what it needs to complete the task.

## Build with an evolving Codex harness

Taking advantage of new model capabilities often means reworking your harness, taking valuable time away from improving your application. The Agents API provides versioned access to these capabilities with each model launch. We maintain and continuously improve the harness alongside our models, helping your agents get better performance from every upgrade. For example, recent improvements to the harness include:

### Keep agents working across long sessions

To support models working for hours, we’ve built context management that helps agents carry relevant information across longer sessions. The Agents API [automatically compacts⁠(opens in a new window)](https://developers.openai.com/api/docs/guides/compaction) earlier context as a session approaches its context limit, preserving information the agent needs to continue. Developers can build workflows that span multiple context windows without implementing their own compaction logic.

### Help agents efficiently use more tools

The Agents API helps agents find the right tools and use them efficiently. [Tool search⁠(opens in a new window)](https://developers.openai.com/api/docs/guides/tools-tool-search) loads relevant tool definitions as needed, helping reduce token usage and cost while preserving the model’s cache. Once tools are available, [programmatic tool calling⁠(opens in a new window)](https://developers.openai.com/api/docs/guides/tools-programmatic-tool-calling) lets agents run calls in parallel, chain related operations, and filter or combine results in code so they can work through large volumes of data while bringing only the relevant results back into context. The Agents API supports MCP, custom functions, and built-in tools like web search.

#### JSON

`1"agent": {

2  "tools": [\
\
3    {\
\
4      "type": "mcp",\
\
5      "server_label": "openai_docs",\
\
6      "transport": {\
\
7        "type": "http",\
\
8        "server_url": "https://developers.openai.com/mcp"\
\
9      }\
\
10    },\
\
11  ]

12}

`

### Let agents parallelize work with subagents

With [multi-agent support⁠(opens in a new window)](https://developers.openai.com/api/docs/guides/agents-api/multi-agent), the Agents API can break complex tasks into independent pieces and delegate them to subagents that work in parallel. Each subagent maintains its own context, helping it stay focused on its assignment, while the main agent coordinates their work and brings the results together. This can speed up research, analysis, and coding tasks that benefit from parallel work, without requiring you to build your own orchestration.

#### JSON

`1"agent": {

2  "model": "gpt-6-astra",

3  "multi_agent": {

4    "enabled": true,

5    "max_concurrent_subagents": 3,

6  }

7}

`

## An open-source foundation

The Agents API is powered by the open-source Codex harness, giving developers visibility into the core logic that coordinates model calls, tools, and context. With the Agents API, OpenAI operates and maintains that harness while developers can inspect and learn from its [public codebase⁠(opens in a new window)](https://github.com/openai/codex).

## Start building

Agents API is available in public beta today to all developers. There are no additional fees for using the Agents API – you simply pay for the tokens and tools your agents use, as outlined on our [pricing page⁠(opens in a new window)](https://developers.openai.com/api/docs/pricing).

Explore the [Agents API overview⁠(opens in a new window)](https://developers.openai.com/api/docs/guides/agents-api/overview) to learn more, or follow the [quickstart⁠(opens in a new window)](https://developers.openai.com/api/docs/guides/agents-api/quickstart) to get started and bring the harness behind Codex into your own agents.

During the public beta, we’ll iterate quickly based on your feedback as we work toward general availability. Let us know what’s working, where you’re running into friction, and what you need to build and run your agents in production.

- [API](https://openai.com/news/?tags=api)
- [Codex](https://openai.com/news/?tags=codex)
- [2026](https://openai.com/news/?tags=2026)

## Author

OpenAI

## Keep reading

[View all](https://openai.com/news/)

![DevDay 2026 Recap — cover image (1:1)](https://images.ctfassets.net/kftzwdyauwt9/1C75hfnvbohzm6Fx3hd7ux/1391c894029045aa51d520e4d80f6f4b/DevDay_Blog_ArtCard_1x1.png?w=3840&q=90&fm=webp)

[DevDay 2026 Recap\\
\\
CompanySep 29, 2026](https://openai.com/index/devday-2026-recap/)

![GPT-6-1-Sol_Blog 1x1](https://images.ctfassets.net/kftzwdyauwt9/7reVkD9GZT81EppPxXgW4D/44c5d09530a17bf45d153b86760ee30a/GPT-6-1-Sol_1x1.png?w=3840&q=90&fm=webp)

[Introducing GPT-6.1 Sol\\
\\
ProductSep 29, 2026](https://openai.com/index/introducing-gpt-6-1-sol/)

![Introducing dots — cover art card (square)](https://images.ctfassets.net/kftzwdyauwt9/2TCcE1IdEPpWT2vaC3PDWu/e78bceb30c38422b1461a2326838e762/Art_Card___1_1_1080x1080.png?w=3840&q=90&fm=webp)

[Introducing dots\\
\\
ProductSep 29, 2026](https://openai.com/index/introducing-dots/)