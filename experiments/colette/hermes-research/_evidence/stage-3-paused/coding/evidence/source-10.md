# [Simon Willison’s Weblog](https://simonwillison.net/)

[Subscribe](https://simonwillison.net/about/#subscribe)

**Sponsored by:** Greptile — AI code reviewers catch bugs at run time and manage your code. [Trusted by Nvidia, Netflix, and many more](https://10xn.link/simon-greptile)

19th January 2026 - Link Blog

**[Scaling long-running autonomous coding](https://cursor.com/blog/scaling-agents)**. Wilson Lin at Cursor has been doing some experiments to see how far you can push a large fleet of "autonomous" coding agents:

> This post describes what we've learned from running hundreds of concurrent agents on a single project, coordinating their work, and watching them write over a million lines of code and trillions of tokens.

They ended up running planners and sub-planners to create tasks, then having workers execute on those tasks - similar to how Claude Code uses sub-agents. Each cycle ended with a judge agent deciding if the project was completed or not.

In my predictions for 2026 [the other day](https://simonwillison.net/2026/Jan/8/llm-predictions-for-2026/#3-years-someone-will-build-a-new-browser-using-mainly-ai-assisted-coding-and-it-won-t-even-be-a-surprise) I said that by 2029:

> I think somebody will have built a full web browser mostly using AI assistance, and it won’t even be surprising. Rolling a new web browser is one of the most complicated software projects I can imagine\[...\] the cheat code is the conformance suites. If there are existing tests that it’ll get so much easier.

I may have been off by three years, because Cursor chose "building a web browser from scratch" as their test case for their agent swarm approach:

> To test this system, we pointed it at an ambitious goal: building a web browser from scratch. The agents ran for close to a week, writing over 1 million lines of code across 1,000 files. You can explore [the source code on GitHub](https://github.com/wilsonzlin/fastrender).

But how well did they do? Their initial announcement a couple of days ago was met with [unsurprising skepticism](https://embedding-shapes.github.io/cursor-implied-success-without-evidence/), especially when it became apparent that their GitHub Actions CI was failing and there were no build instructions in the repo.

It looks like they addressed that within the past 24 hours. The [latest README](https://github.com/wilsonzlin/fastrender/blob/main/README.md#build-requirements) includes build instructions which I followed on macOS like this:

```
cd /tmp
git clone https://github.com/wilsonzlin/fastrender
cd fastrender
git submodule update --init vendor/ecma-rs
cargo run --release --features browser_ui --bin browser
```

This got me a working browser window! Here are screenshots I took of google.com and my own website:

![The browser chrome is neat but has a garbled tab name at the top. The Google homepage looks mostly correct but the buttons are not styled correctly and the Google Search one has a huge plus icon floating near it.](https://static.simonwillison.net/static/2026/cursor-google.png)

![My blog looks mostly correct, but the right closing quotation mark on a quotation (which is implemented as a background image on the final paragraph) is displayed incorrectly multiple times.](https://static.simonwillison.net/static/2026/cursor-simonwillison.jpg)

Honestly those are very impressive! You can tell they're not just wrapping an existing rendering engine because of those very obvious rendering glitches, but the pages are legible and look mostly correct.

The FastRender repo even uses Git submodules [to include various WhatWG and CSS-WG specifications](https://github.com/wilsonzlin/fastrender/tree/main/specs) in the repo, which is a smart way to make sure the agents have access to the reference materials that they might need.

This is the second attempt I've seen at building a full web browser using AI-assisted coding in the past two weeks - the first was [HiWave browser](https://github.com/hiwavebrowser/hiwave), a new browser engine in Rust first announced [in this Reddit thread](https://www.reddit.com/r/Anthropic/comments/1q4xfm0/over_christmas_break_i_wrote_a_fully_functional/).

When I made my 2029 prediction this is more-or-less the quality of result I had in mind. I don't think we'll see projects of this nature compete with Chrome or Firefox or WebKit any time soon but I have to admit I'm very surprised to see something this capable emerge so quickly.

**Update 23rd January 2026**: I recorded a 47 minute conversation with Wilson about this project and published it on YouTube. Here's [the video and accompanying highlights](https://simonwillison.net/2026/Jan/23/fastrender/).

Posted [19th January 2026](https://simonwillison.net/2026/Jan/19/) at 5:12 am

## Recent articles

- [OpenAI DevDay 2026 live blog](https://simonwillison.net/2026/Sep/29/openai-devday-2026-live-blog/) \- 29th September 2026
- [2026 in LLMs (so far)](https://simonwillison.net/2026/Sep/27/2026-in-llms-so-far/) \- 27th September 2026
- [Claude Opus 5.5, GPT-6 Sol, GPT-6 Luna, and a new price war](https://simonwillison.net/2026/Sep/22/opus-and-sol-and-luna/) \- 22nd September 2026

This is a **link post** by Simon Willison, posted on [19th January 2026](https://simonwillison.net/2026/Jan/19/).

[browsers\\
107](https://simonwillison.net/tags/browsers/) [ai\\
2,258](https://simonwillison.net/tags/ai/) [rust\\
114](https://simonwillison.net/tags/rust/) [generative-ai\\
2,002](https://simonwillison.net/tags/generative-ai/) [llms\\
1,969](https://simonwillison.net/tags/llms/) [ai-assisted-programming\\
407](https://simonwillison.net/tags/ai-assisted-programming/) [coding-agents\\
253](https://simonwillison.net/tags/coding-agents/) [cursor\\
13](https://simonwillison.net/tags/cursor/) [parallel-agents\\
16](https://simonwillison.net/tags/parallel-agents/) [conformance-suites\\
11](https://simonwillison.net/tags/conformance-suites/) [browser-challenge\\
4](https://simonwillison.net/tags/browser-challenge/)

### Monthly briefing

Sponsor me for **$10/month** and get a curated email digest of the month's most important LLM developments.


Pay me to send you less!


[Sponsor & subscribe](https://github.com/sponsors/simonw/)

- [Disclosures](https://simonwillison.net/about/#disclosures)
- [Colophon](https://simonwillison.net/about/#about-site)
- ©
- [2002](https://simonwillison.net/2002/)
- [2003](https://simonwillison.net/2003/)
- [2004](https://simonwillison.net/2004/)
- [2005](https://simonwillison.net/2005/)
- [2006](https://simonwillison.net/2006/)
- [2007](https://simonwillison.net/2007/)
- [2008](https://simonwillison.net/2008/)
- [2009](https://simonwillison.net/2009/)
- [2010](https://simonwillison.net/2010/)
- [2011](https://simonwillison.net/2011/)
- [2012](https://simonwillison.net/2012/)
- [2013](https://simonwillison.net/2013/)
- [2014](https://simonwillison.net/2014/)
- [2015](https://simonwillison.net/2015/)
- [2016](https://simonwillison.net/2016/)
- [2017](https://simonwillison.net/2017/)
- [2018](https://simonwillison.net/2018/)
- [2019](https://simonwillison.net/2019/)
- [2020](https://simonwillison.net/2020/)
- [2021](https://simonwillison.net/2021/)
- [2022](https://simonwillison.net/2022/)
- [2023](https://simonwillison.net/2023/)
- [2024](https://simonwillison.net/2024/)
- [2025](https://simonwillison.net/2025/)
- [2026](https://simonwillison.net/2026/)