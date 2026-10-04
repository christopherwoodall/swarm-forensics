[Cognition home](https://cognition.com/)

Menu

[Cognition home](https://cognition.com/) Close

![Devin's 2025 Performance Review: Learnings From 18 Months of Agents At Work](https://cdn.sanity.io/images/2mc9cv2v/production/1669b064fa3d9de7a68b62b4d2784e7856fbed27-1400x500.png?w=1600&fit=max)

Eighteen months after launch, Devin’s gone from tackling small projects, to working in engineering teams at thousands of companies, including Goldman Sachs, Santander, and Nubank.

Devin's now merged **hundreds of thousands of PRs**.

At this point, Devin's well past due for a performance review - just like any human engineer.

## How we evaluated Devin

We first tried to calibrate Devin against a traditional engineering competency matrix, but this was difficult. While human engineers tend to cluster around a level, Devin is senior-level at codebase understanding but junior at execution. It has infinite capacity but struggles at soft skills.

Instead we summarized Devin's strengths and weaknesses in real-world environments, with examples and metrics from customers. We hope this will be helpful to anyone who's interested in real-world agent deployment.

## Strength pattern \#1: Junior execution at infinite scale

Devin excels at **tasks with clear, upfront requirements and verifiable outcomes that would take a junior engineer 4-8 hrs of work.**

Unlike a human, though, it is infinitely parallelizable and never sleeps. This makes it well-suited to critical but less creative work like migrating and modernizing repos, fixing vulnerabilities surfaced by static analysis tools like SonarQube and Veracode, writing unit tests, and completing small tickets. This frees up human engineers for higher-impact projects.

Over the past year, Devin has become a faster and better junior engineer - it’s **4x faster at problem solving** and **2x more efficient in resource consumption**, and **67% of its PRs are now merged vs 34% last year**.

![Devin's 2025 Performance Review: Learnings From 18 Months of Agents At Work](https://cdn.sanity.io/images/2mc9cv2v/production/621afab3e569a2b90e61a952c733b4e0f1d65cba-2963x1467.png?w=1600&fit=max)

### Security vulnerability resolution

Devin is great at resolving vulnerabilities flagged by static analysis tools (e.g. SonarQube, Veracode).

A few standout examples: One large organization **saved 5-10% of total developer time** by using Devin for security fixes. Another saw 20x efficiency gain: **human developers average 30 minutes per vulnerability, Devin, 1.5 minutes.**

### Language and framework upgrades, migrations, and modernization

Customers use Devin for modernization and migrations, like SAS → PySpark, COBOL, Angular → React, .NET Framework → .NET Core, or switching off proprietary frameworks.

Once it gets instructions on how to update each repo, a fleet of Devins can execute on every repo in parallel. This results in massive savings. A few examples from this year:

- A large bank was migrating hundreds of thousands of proprietary ETL framework files. Devin completed each file's migration in **3-4 hours vs 30-40 for human engineers (10x improvement).**
- When Oracle sunsetted legacy support for one Java version, Devin was able to migrate each repo in **14x less time than a human engineer.**

![Devin's 2025 Performance Review: Learnings From 18 Months of Agents At Work](https://cdn.sanity.io/images/2mc9cv2v/production/56ebf7834fbe08c1dc79491f200b71307ef9da0d-1712x656.png?w=1600&fit=max)

Using agents decrease the cost of modernization, so organizations can spend more time building new features than maintaining legacy code.

### Test generation

Devin can do the first pass of [writing tests](https://docs.devin.ai/use-cases/testing-refactoring), with humans checking logic. Humans will write a unit testing playbook for Devin that spans a few hundred repos at a time. Then a fleet of Devins will go off and write the tests. After, code owners will check to see if all logic has been tested.

Companies' test coverage typically rises from **50-60% to 80-90%** when using Devin.

### Brownfield feature development

When existing code provides clear patterns, Devin can replicate and modify: adding API endpoints, creating frontend components, extending functionality. **Devin pushed about ⅓ of the commits on our web app.**

### PR review

Devin can execute first-pass reviews and catch obvious issues. Human review is still necessary, because code quality is not straightforwardly verifiable.

### Data analysis & QA work

![Devin's 2025 Performance Review: Learnings From 18 Months of Agents At Work](https://cdn.sanity.io/images/2mc9cv2v/production/8a30c06c220b9fed9bea558f9945126709fac55a-1200x721.png?w=1600&fit=max)

Devin is unexpectedly good at data analysis and quality assurance. Companies can “@” Devin in Slack and ask questions like “ _can you pull yesterday’s sales by channel?”_, _“can you check why this number looks off?”_, or ask it to create dashboards.

One customer, EightSleep, ships **[3x as many](https://cognition.ai/blog/how-eight-sleep-uses-devin-as-a-data-analyst) data features and investigations with Devin**. We constantly do use this internally (we even used Devin to pull metrics for this report.)

Another skill Devin has picked up is quality engineering. When Litera gave every engineering manager a “team of Devins” acting as QE testers, SREs, and DevOps specialists, test coverage increased by 40% and regression cycles got 93% faster.

## Strength pattern \#2: Senior intelligence on demand

**Only [20%](https://www.microsoft.com/en-us/research/wp-content/uploads/2024/11/Time-Warp-Developer-Productivity-Study.pdf) of engineering time is spent coding;** much more goes into other work, like planning and reviewing.

Devin's gotten massively better over the past year at understanding large codebases (one driver of its doubled PR merge rate). This means it can **quickly document large codebases, and assist humans with planning.**

This capability looks more like having a tenured senior engineer on-demand to answer any questions. Engineers can onboard faster, and chat with Devin to understand their codebase and plan projects.

### Documentation

When onboarding to a codebase, Devin generates comprehensive, always-updating documentation with system diagrams ( [DeepWiki](https://deepwiki.com/)). It can do this on large repos - customers have used DeepWiki to **generate docs for 5M lines of COBOL or 500GB repos.**

![Devin's 2025 Performance Review: Learnings From 18 Months of Agents At Work](https://cdn.sanity.io/images/2mc9cv2v/production/de62d08befecf33f2f0f55f4ca35f35a831a4138-2916x1908.png?w=1600&fit=max)

A bank could re-allocate several engineering teams from a big documentation project to new feature development, since **Devin generated documentation across 400,000+ repositories**.

### Planning

When engineers are planning work, they will look at the documentation and chat with Devin ( [AskDevin](https://docs.devin.ai/work-with-devin/ask-devin)) to understand the system. Devin can explain with architecture diagrams, map dependencies, and flag any breaking changes, and recommend what should be tackled by humans vs AI.

One engineer told us that he could **generate draft architecture in 15 minutes** for others to react to.

## Devin's areas for improvement

### Independent execution on ambiguous requirements

**Like most junior engineers, Devin does best with clear requirements.** Devin can't independently tackle an ambiguous coding project end-to-end like a senior engineer could, using its own judgement. For example, in visual design, Devin needs specifics like component structure, color codes, and spacing values.

When outcomes aren't straightforwardly verifiable, additional human review is necessary. Humans check unit testing logic after Devin takes the first pass, and check its code reviews.

### Scope changes and iterative collaboration

Devin handles clear upfront scoping well, but not mid-task requirement changes. It usually performs worse when you keep telling it more after it starts the task. This differs from human juniors: you can coach a human through iterative problem-solving.

This puts more of a responsibility on the engineer to scope work well up-front. Engineers working with Devin have to adjust to learning how to "manage" Devin effectively.

### Soft skills and interpersonal work

While it’s great at collaborating in Slack, Teams, and Jira, it cannot manage reports or stakeholders or deal with teammates' emotions. It definitely won’t be organizing lunch-and-learns or patiently mentoring a direct report any time soon! It is, however, infinitely friendly, patient, and responsive.

## What's next

![Devin's 2025 Performance Review: Learnings From 18 Months of Agents At Work](https://cdn.sanity.io/images/2mc9cv2v/production/43a5b52dbcc51b2be73c1385a16e3a52fdb52942-1536x1024.png?w=1600&fit=max)

In 2026, we’ll continue to work on making Devin better at understanding real-world codebases and using that context to collaborate with engineers on end-to-end SWE work. We’re also investing in UX so Devin is easier to direct in everyday development.

If you're interested in hiring Devin, you can [talk to sales](https://cognition.ai/contact). Or, try running [DeepWiki](https://deepwiki.com/) on one of your codebases to check out Devin's codebase understanding.

04\. ArticlesArticles

[![Estimating the Productivity of an Autonomous AI Software Engineer](https://cognition.com/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2F2mc9cv2v%2Fproduction%2F8527b7c1b2b03f309d7ba9189296ac76a1c7b650-1920x1080.jpg%3Fw%3D640%26h%3D360%26fit%3Dcrop&w=1920&q=75)\\
\\
Estimating the Productivity of an Autonomous AI Software Engineer\\
\\
06.04.26](https://cognition.com/blog/ai-productivity) [![AI should earn its keep: Introducing the AI Productivity Guarantee](https://cognition.com/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2F2mc9cv2v%2Fproduction%2Fd378ef146ec6070438bfaeab4d9e47e8b886e55d-1920x1080.jpg%3Fw%3D640%26h%3D360%26fit%3Dcrop&w=1920&q=75)\\
\\
AI should earn its keep: Introducing the AI Productivity Guarantee\\
\\
06.04.26](https://cognition.com/blog/ai-guarantee) [![Introducing Devin Desktop](https://cognition.com/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2F2mc9cv2v%2Fproduction%2F5841a7932386c05dc112f92fda8ff519b38d4f9a-1920x1080.jpg%3Fw%3D640%26h%3D360%26fit%3Dcrop&w=1920&q=75)\\
\\
Introducing Devin Desktop\\
\\
06.02.26](https://cognition.com/blog/introducing-devin-desktop) [![More Devins in More Places](https://cognition.com/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2F2mc9cv2v%2Fproduction%2F58309361c06f31fa49f8c36e307963f21bd3f22b-1382x777.jpg%3Frect%3D1%2C0%2C1381%2C777%26w%3D640%26h%3D360%26fit%3Dcrop&w=1920&q=75)\\
\\
More Devins in More Places\\
\\
05.27.26](https://cognition.com/blog/series-d) [![Devin in Windsurf](https://cognition.com/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2F2mc9cv2v%2Fproduction%2F89fcacf48d33b51277268808596d123237018950-1920x1080.jpg%3Fw%3D640%26h%3D360%26fit%3Dcrop&w=1920&q=75)\\
\\
Devin in Windsurf\\
\\
04.15.26](https://cognition.com/blog/devin-in-windsurf) [![An Early Preview of SWE-1.6 and Research Update](https://cognition.com/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2F2mc9cv2v%2Fproduction%2F6ce843c49d6a38e1c0045e43891aca89fccd8981-1500x844.jpg%3Fw%3D640%26h%3D360%26fit%3Dcrop&w=1920&q=75)\\
\\
An Early Preview of SWE-1.6 and Research Update\\
\\
03.01.26](https://cognition.com/blog/swe-1-6-preview) [![How Cognition Uses Devin to Build Devin](https://cognition.com/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2F2mc9cv2v%2Fproduction%2Fc1e05d959a8c25c8df5e86198a4213e4fd634b61-1500x844.jpg%3Fw%3D640%26h%3D360%26fit%3Dcrop&w=1920&q=75)\\
\\
How Cognition Uses Devin to Build Devin\\
\\
02.27.26](https://cognition.com/blog/how-cognition-uses-devin-to-build-devin) [![Introducing Cognition for Government](https://cognition.com/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2F2mc9cv2v%2Fproduction%2F164f27869605d7c326a68e511efcf1a4077fc2b7-1920x1080.jpg%3Fw%3D640%26h%3D360%26fit%3Dcrop&w=1920&q=75)\\
\\
Introducing Cognition for Government\\
\\
02.25.26](https://cognition.com/blog/cognition-for-government) [![Introducing Devin 2.2](https://cognition.com/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2F2mc9cv2v%2Fproduction%2F5638cfd0a8a65ad3074019b69c3aa05e112577b7-1920x1080.jpg%3Fw%3D640%26h%3D360%26fit%3Dcrop&w=1920&q=75)\\
\\
Introducing Devin 2.2\\
\\
02.24.26](https://cognition.com/blog/introducing-devin-2-2)