[Wiz](https://www.wiz.io/)

- [Sign in](https://app.wiz.io/login)
- [Under attack?](https://www.wiz.io/experiencing-an-incident)

[Get a demo](https://www.wiz.io/demo?cta_source=blog&cta_page=/blog/exposed-moltbook-database-reveals-millions-of-api-keys&cta_placement=nav)

![](<Base64-Image-Removed>)![](<Base64-Image-Removed>)

![](<Base64-Image-Removed>)![](<Base64-Image-Removed>)

## What is Moltbook, and Why Did it Attract Our Attention?

Moltbook, the weirdly futuristic social network, has quickly gone viral as a forum where AI agents post and chat. But what we discovered tells a different story - and provides a fascinating look into what happens when applications are vibe-coded into existence without proper security controls.

We identified a misconfigured Supabase database belonging to Moltbook, allowing full read and write access to all platform data. The exposure included 1.5 million API authentication tokens, 35,000 email addresses, and private messages between agents. We immediately disclosed the issue to the Moltbook team, who secured it within hours with our assistance, and all data accessed during the research and fix verification has been deleted.

## **Executive Summary**

Moltbook is a social platform designed exclusively for AI agents - positioned as the "front page of the agent internet." The platform allows AI agents to post content, comment, vote, and build reputation through a karma system, creating what appears to be a thriving social network where AI is the primary participant.

![](<Base64-Image-Removed>)![](https://www.datocms-assets.com/75231/1769995299-image3.png?fm=webp)

Moltbook home page

Over the past few days, Moltbook gained [significant attention in the AI community](https://x.com/karpathy/status/2017296988589723767?s=20). OpenAI founding member Andrej Karpathy described it as "genuinely the most incredible sci-fi takeoff-adjacent thing I have seen recently," noting how agents were "self-organizing on a Reddit-like site for AIs, discussing various topics, e.g. even how to speak privately."

The Moltbook founder [explained publicly on X](https://x.com/mattprd/status/2017386365756072376?s=46&t=JS55_O2JZmKWQpZHLAse_A) that he "vibe-coded" the platform:

> I didn’t write a single line of code for @moltbook. I just had a vision for the technical architecture, and AI made it a reality.”

This practice, while revolutionary, can lead to dangerous security oversights - similar to previous vulnerabilities we have identified, including the [DeepSeek data leak](https://www.wiz.io/blog/wiz-research-uncovers-exposed-deepseek-database-leak) and [Base44 Authentication Bypass](https://www.wiz.io/blog/critical-vulnerability-base44).

We conducted a non-intrusive security review, simply by browsing like normal users. Within minutes, we discovered a Supabase API key exposed in client-side JavaScript, granting unauthenticated access to the entire production database - including read and write operations on all tables.

![](<Base64-Image-Removed>)![](https://www.datocms-assets.com/75231/1770039552-image1.png?fm=webp)

Accessible tables from the Supabase API Key

The exposed data told a different story than the platform's public image - while Moltbook boasted 1.5 million registered agents, the database revealed only 17,000 human owners behind them - an 88:1 ratio. Anyone [could register millions of agents](https://x.com/galnagli/status/2017585025475092585?s=20) with a simple loop and no rate limiting, and humans could post content disguised as "AI agents" via a [basic POST request](https://x.com/galnagli/status/2017573842051334286?s=20). **The platform had no mechanism to verify whether an "agent" was actually AI or just a human with a script.** The revolutionary AI social network was largely humans operating fleets of bots.

![](<Base64-Image-Removed>)![](https://www.datocms-assets.com/75231/1770038582-image3.jpg?fm=webp)

an HTTP Post request to create new "agent" post in Moltbook's platform

![](<Base64-Image-Removed>)![](https://www.datocms-assets.com/75231/1770038634-image16.png?fm=webp)

An "agent" post in Moltbook.

## How the Moltbook Database Was Exposed

### **Discovery of Exposed Supabase Credentials**

When navigating to Moltbook's website, we examined the client-side JavaScript bundles loaded automatically by the page. Modern web applications bundle configuration values into static JavaScript files, which can inadvertently expose sensitive credentials. **This is a recurring pattern we've observed in vibe-coded applications** \- API keys and secrets frequently end up in frontend code, visible to anyone who inspects the page source, often with significant security consequences.

By analyzing the production JavaScript file at -

https://www.moltbook.com/\_next/static/chunks/18e24eafc444b2b9.js

We identified hardcoded Supabase connection details:

\- **Supabase Project**: ehxbxtjliybbloantpwq.supabase.co

\- **API Key**: sb\_publishable\_4ZaiilhgPir-2ns8Hxg5Tw\_JqZU\_G6-

![](<Base64-Image-Removed>)![](https://www.datocms-assets.com/75231/1769995567-image8.png?fm=webp)

One of the javascript files that power Moltbook main website

![](<Base64-Image-Removed>)![](https://www.datocms-assets.com/75231/1769995593-image7.png?fm=webp)

The production supabase and API key hardcoded

The discovery of these credentials does not automatically indicate a security failure, as Supabase is designed to operate with certain keys exposed to the client - the real danger lies in the configuration of the backend they point to.

Supabase is a popular open-source Firebase alternative providing hosted PostgreSQL databases with REST APIs. It's become especially popular with vibe-coded applications due to its ease of setup. When properly configured with Row Level Security (RLS), the public API key is safe to expose - it acts like a project identifier. **However, without RLS policies, this key grants full database access to anyone who has it.** In Moltbook’s implementation, this critical line of defense was missing.

### **Unauthenticated Database Access via Supabase API**

Using the discovered API key, we tested whether the recommended security measures were in place. We attempted to query the REST API directly - a request that should have returned an empty array or an authorization error if RLS were active.

```
curl
https://ehxbxtjliybbloantpwq.supabase.co/rest/v1/agents?select=name,api_key&limit=3" -H "apikey: sb_pub...ead, the database responded exactly as if we were an administrator. It immediately returned sensitive authentication tokens - including the API keys of the platform’s top AI Agents.

![](<Base64-Image-Removed>)![](https://www.datocms-assets.com/75231/1769995852-image4.png?fm=webp)

Redacted API keys of the Platform's top AI Agents

![](<Base64-Image-Removed>)![](https://www.datocms-assets.com/75231/1769995887-image15.png?fm=webp)

List of most popular Agents

This confirmed unauthenticated access to user credentials that would allow complete account impersonation of any user on the platform.

### **Database Enumeration Through PostgREST and GraphQL**

By leveraging Supabase's PostgREST error messages, we enumerated additional tables. Querying non-existent table names returned hints revealing the actual schema.

```
curl "https://ehxbxtjliybbloantpwq.supabase.co/rest/v1/users" -H "apikey: sb_pub...sing this technique combined with GraphQL introspection, we mapped the complete database schema and found around ~4.75 million records exposed.

![](<Base64-Image-Removed>)![](https://www.datocms-assets.com/75231/1769996084-image10.png?fm=webp)

Identified tables through the technique described above

## **Sensitive Data Exposed in the Moltbook Database**

1\. **API Keys and Authentication Tokens for AI Agents**

The agents table exposed authentication credentials for every registered agent in the database

```
{

    "name": "KingMolt",

    "id": "ee7e81d9-f512-41ac-bb25-975249b867f9",

    "api_key": "moltbook_sk_AGqY...hBQ",

    "claim_token": "moltbook_claim_6gNa...8-z",

    "verification_code": "claw-8RQT",

    "karma": 502223,

    "follower_count": 18

  }
```

Each agent record contained:

\- api\_key - Full authentication token allowing complete account takeover

\- claim\_token - Token used to claim ownership of an agent

\- verification\_code - Code used during agent registration

With these credentials, an attacker could **fully impersonate any agent on the platform** \- posting content, sending messages, and interacting as that agent. This included high-karma accounts and well-known persona agents. Effectively, every account on Moltbook could be hijacked with a single API call.

2\. **User Email Addresses and Identity Data**

The owners table contained personal information for 17,000+ users

```
curl "https://ehxbxtjliybbloantpwq.supabase.co/rest/v1/owners?select=email,x_handle,x_name&email=neq.null&limit=5" -H "apikey: sb_pub...nHow exposed emails looked like in the raw data

Additionally, by querying the GraphQL endpoint, we discovered a new observers table containing 29,631 additional email addresses - these were early access signups for Moltbook's upcoming “Build Apps for AI Agents” product.

![](<Base64-Image-Removed>)![](https://www.datocms-assets.com/75231/1769996206-image12.png?fm=webp)

Additional tables from Moltbook's new developers product

Unlike Twitter handles which were publicly displayed on profiles, email addresses were meant to stay private - but were fully exposed in the database.

3\. **Private Messages & Third-Party Credential Leaks**

The agent\_messages table exposed 4,060 private DM conversations between agents.

While examining this table to understand agent-to-agent interactions, we discovered that **conversations were stored without any encryption or access controls** \-\- some contained third-party API credentials, including plaintext OpenAI API keys shared between agents.

![](<Base64-Image-Removed>)![](https://www.datocms-assets.com/75231/1769996263-image1.png?fm=webp)

Agent to Agent interaction summary

4\. **Write Access - Modifying Live Posts**

Beyond read access, we confirmed full write capabilities. Even after the initial fix that blocked read access to sensitive tables, write access to public tables remained open. We tested it and were able to successfully modify existing posts on the platform.

```
curl -X PATCH "https://ehxbxtjliybbloantpwq.supabase.co/rest/v1/posts?id=eq.74b073fd-37db-4a32-a9e1-c7652e5c0d59" -H "apikey: sb_pub...6-" -H "Content-Type: application/json" -d '{"title":"@galnagli - responsible disclosure test","content":"@galnagli - responsible disclosure test"}'
```

Proving that any unauthenticated user could:

\- Edit any post on the platform

\- Inject malicious content or prompt injection payloads

\- Deface the entire website

\- Manipulate content consumed by thousands of AI agents

This raises questions about **the integrity of all platform content** \- posts, votes, and karma scores - during the exposure window.

![](<Base64-Image-Removed>)![](https://www.datocms-assets.com/75231/1769996340-image13.png?fm=webp)

Modified post on Moltbook

![](<Base64-Image-Removed>)![](https://www.datocms-assets.com/75231/1769996367-image14.png?fm=webp)

We promptly notified the team again to apply write restrictions via RLS policies.

Once the fix was confirmed, I could no longer revert the post as write access was blocked. The Moltbook team deleted the content a few hours later and thanked us for our report.

## **5 Key Security Lessons for AI-Built Apps**

**#1\. Speed Without Secure Defaults Creates Systemic Risk**

[Vibe coding](https://www.wiz.io/blog/safer-vibe-coding-rules-files) unlocks remarkable speed and creativity, enabling founders to ship real products with unprecedented velocity - as demonstrated by Moltbook. At the same time, today’s **AI tools don’t yet reason about security posture or access controls on a developer’s behalf**, which means configuration details still benefit from careful human review. In this case, the issue ultimately traced back to a single Supabase configuration setting - a reminder of how small details can matter at scale.

**#2.  Participation Metrics Need Verification and Guardrails**

The 88:1 agent-to-human ratio shows how "agent internet" metrics can be easily inflated without guardrails like rate limits or identity verification. **While Moltbook reported 1.5 million agents, these were associated with roughly 17,000 human accounts, an average of about 88 agents per person**. At the time of our review, there were limited guardrails such as rate limiting or validation of agent autonomy. Rather than a flaw, this likely reflects how early the “agent internet” category still is: builders are actively exploring what agent identity, participation, and authenticity should look like, and the supporting mechanisms are still evolving.

**#3\. Privacy Breakdowns Can Cascade Across AI Ecosystems**

Similarly, the platform’s approach to privacy highlights an important ecosystem-wide lesson. Users shared OpenAI API keys and other credentials in direct messages under the assumption of privacy, but a configuration issue made those messages publicly accessible. A single platform misconfiguration was enough to expose credentials for entirely unrelated services - underscoring how interconnected modern AI systems have become.

**#4\. Write Access Introduces Far Greater Risk Than Data Exposure Alone**

While data leaks are bad, the ability to modify content and inject prompts into an AI ecosystem introduces deeper integrity risks, including content manipulation, narrative control, and prompt injection that can propagate downstream to other AI agents. As AI-driven platforms grow, these distinctions become increasingly important design considerations.

**#5\. Security Maturity is an Iterative Process**

Security, especially in fast-moving AI products, is rarely a one-and-done fix. **We worked with the team through multiple rounds of remediation**, with each iteration surfacing additional exposed surfaces: from sensitive tables, to write access, to GraphQL-discovered resources. This kind of iterative hardening is common in new platforms and reflects how security maturity develops over time.

Overall, Moltbook illustrates both the excitement and the growing pains of a brand-new category. The enthusiasm around AI-native social networks is well-founded, but the underlying systems are still catching up. The most important outcome here is not what went wrong, but what the ecosystem can learn as builders, researchers, and platforms collectively define the next phase of AI-native applications.

## **Closing Thoughts on Vibe Coding and Security**

As AI continues to lower the barrier to building software, more builders with bold ideas but limited security experience will ship applications that handle real users and real data. That’s a powerful shift. The challenge is that while the barrier to building has dropped dramatically, the barrier to building securely has not yet caught up.

The opportunity is not to slow down vibe coding but to elevate it. [Security](https://www.wiz.io/academy/ai-security/what-is-ai-security) needs to become a first class, built-in part of AI powered development. AI assistants that generate Supabase backends can enable RLS by default. Deployment platforms can proactively scan for exposed credentials and unsafe configurations. In the same way AI now automates code generation, it can also automate secure defaults and guardrails.

If we get this right, vibe coding does not just make software easier to build ... it makes secure software the natural outcome and unlocks the full potential of AI-driven innovation.

_**Note**_ _: Security researcher Jameson O'Reilly_ [_also discovered_](https://x.com/theonejvo/status/2017732898632437932) _the underlying Supabase misconfiguration, which has been_ [_reported by 404 Media_](https://www.404media.co/exposed-moltbook-database-let-anyone-take-control-of-any-ai-agent-on-the-site/) _. Wiz's post shares our experience independently finding the issue, the full -- unreported -- scope of impact, and how we worked with Moltbook's maintainer to improve security._

## **Disclosure Timeline**

**January 31, 2026 21:48 UTC** \- Initial contact with Moltbook maintainer via X DM

**January 31, 2026 22:06 UTC** \- Reported Supabase RLS misconfiguration exposing agents table (API keys, emails)

**January 31, 2026 23:29 UTC** \- First fix: agents, owners, site\_admins tables secured

**February 1, 2026 00:13 UTC** \- Second fix: agent\_messages, notifications, votes, follows secured

**February 1, 2026 00:31 UTC** \- Discovered POST write access vulnerability (ability to modify all posts)

**February 1, 2026 00:44 UTC** \- Third fix: Write access blocked

**February 1, 2026 00:50 UTC** \- Discovered additional exposed tables: observers (29K emails), identity\_verifications, developer\_apps

**February 1, 2026 01:00 UTC** \- Final fix: All tables secured, vulnerability fully patched

Tags

[#Research](https://www.wiz.io/blog/tag/research) [#AI](https://www.wiz.io/blog/tag/ai)

## Continue reading

[![](<Base64-Image-Removed>)![](<Base64-Image-Removed>)](https://www.wiz.io/blog/top-wiz-research-blogs-2025)

[**The Year in Wiz Research: 2025 Most Read Blogs**](https://www.wiz.io/blog/top-wiz-research-blogs-2025)

[![](<Base64-Image-Removed>)![](<Base64-Image-Removed>)](https://www.wiz.io/authors/wiz-threat-research)

[Wiz Threat Research](https://www.wiz.io/authors/wiz-threat-research)

January 30, 2026

A look back at the cloud security investigations and vulnerabilities that defined the year, from AI breakthroughs to supply chain shifts.

[![](<Base64-Image-Removed>)![](<Base64-Image-Removed>)](https://www.wiz.io/blog/ai-agents-vs-humans-who-wins-at-web-hacking-in-2026)

[**AI Agents vs Humans: Who Wins at Web Hacking in 2026?**](https://www.wiz.io/blog/ai-agents-vs-humans-who-wins-at-web-hacking-in-2026)

[![](<Base64-Image-Removed>)![](<Base64-Image-Removed>)](https://www.wiz.io/authors/gal-nagli)[![](<Base64-Image-Removed>)![](<Base64-Image-Removed>)](https://www.wiz.io/authors/irregular)

[Gal Nagli](https://www.wiz.io/authors/gal-nagli), [Irregular](https://www.wiz.io/authors/irregular)

January 29, 2026

Wiz Research teamed up with Irregular, a frontier AI security lab, to settle this once and for all.

[![](<Base64-Image-Removed>)![](<Base64-Image-Removed>)](https://www.wiz.io/blog/introducing-win-partner-index)

[**Introducing the WIN Partner Index: The Integrations That Powered Modern Cloud Security in 2025**](https://www.wiz.io/blog/introducing-win-partner-index)

[![](<Base64-Image-Removed>)![](<Base64-Image-Removed>)](https://www.wiz.io/authors/bandhna-bedi)[![](<Base64-Image-Removed>)![](<Base64-Image-Removed>)](https://www.wiz.io/authors/daphna-dayan)[![](<Base64-Image-Removed>)![](<Base64-Image-Removed>)](https://www.wiz.io/authors/katerina-greenstein)

[Bandhna Bedi](https://www.wiz.io/authors/bandhna-bedi), [Daphna Dayan](https://www.wiz.io/authors/daphna-dayan), [Katerina Greenstein](https://www.wiz.io/authors/katerina-greenstein)

January 29, 2026

A data-driven industry benchmark showing how integrations are adopted, gain traction, and deliver value across modern cloud security programs.

Get a personalized demo

## Ready to see Wiz in action?

> "Best User Experience I have ever seen, provides full visibility to cloud workloads."

David EstlickCISO

> "Wiz provides a single pane of glass to see what is going on in our cloud environments."

Adam FletcherChief Security Officer

> "We know that if Wiz identifies something as critical, it actually is."

Greg PoniatowskiHead of Threat and Vulnerability Management

[Get a demo](https://www.wiz.io/demo)

a26988130118.cdn.optimizely.com

# a26988130118.cdn.optimizely.com is blocked

This page has been blocked by an extension

- Try disabling your extensions.

ERR\_BLOCKED\_BY\_CLIENT

Reload


This page has been blocked by an extension

![](<Base64-Image-Removed>)![](<Base64-Image-Removed>)

![](https://www.datocms-assets.com/75231/1769995299-image3.png?fm=webp)

![](https://www.datocms-assets.com/75231/1770039552-image1.png?fm=webp)

![](https://www.datocms-assets.com/75231/1770038582-image3.jpg?fm=webp)

![](https://www.datocms-assets.com/75231/1770038634-image16.png?fm=webp)

![](https://www.datocms-assets.com/75231/1769995567-image8.png?fm=webp)

![](https://www.datocms-assets.com/75231/1769995593-image7.png?fm=webp)

![](https://www.datocms-assets.com/75231/1769995852-image4.png?fm=webp)

![](https://www.datocms-assets.com/75231/1769995887-image15.png?fm=webp)

![](https://www.datocms-assets.com/75231/1769996060-image9.png?fm=webp)

![](https://www.datocms-assets.com/75231/1769996084-image10.png?fm=webp)

![](https://www.datocms-assets.com/75231/1769996178-image11.png?fm=webp)

![](https://www.datocms-assets.com/75231/1769996206-image12.png?fm=webp)

![](https://www.datocms-assets.com/75231/1769996263-image1.png?fm=webp)

![](https://www.datocms-assets.com/75231/1769996340-image13.png?fm=webp)

![](https://www.datocms-assets.com/75231/1769996367-image14.png?fm=webp)