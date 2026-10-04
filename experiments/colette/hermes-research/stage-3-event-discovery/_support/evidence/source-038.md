[Jump to main content](https://www.theregister.com/security/2026/07/29/word-worm-crawls-into-copilot-spreads-chaos/5280588#main)

REG AD

security


# Word worm crawls into Copilot, spreads chaos

Researcher says months of coordination with Microsoft have yet to produce a robust mitigation


Brandon Vigliarolo [BrandonVigliarolo](https://www.theregister.com/author/brandon-vigliarolo) GOVERNMENT AND IT NEWS REPORTER

PublishedWed 29 Jul 2026 // 16:43 UTC

UPDATEDWatch out for untrusted documents. According to research, an attacker can hide malicious instructions in a Word document that, when included in Copilot for Word’s context, may alter document output and copy the instructions into newly created files that use the affected document as source material, without the victim noticing.

Håkon Måløy, a Norwegian data scientist with a PhD in applied AI and ML, publicly disclosed the issue in a [blog post](https://enklypesalt.com/posts/context-collapse-part3-ai-worming-through-word/) Tuesday. Måløy describes the issue in considerable detail while withholding the specific prompt payload, arguing that, because no robust mitigation exists, it would be irresponsible to disclose anything beyond the class of the vulnerability.

REG AD

“To my knowledge, this is among the first public demonstrations of document-borne AI-worm self-propagation through normal workflows in a mainstream commercial productivity suite,” Måløy noted.

REG AD

Måløy said that he has been working with Microsoft since March 2026 on addressing the vulnerability, but after multiple updates to Copilot, this new class of Copilot worm is still viable. Microsoft mitigated the exploit demonstrated by his original proof-of-concept prompt, but Måløy said rewording the payload allowed him to successfully propagate the worm and alter financial data in a target document. Måløy and Microsoft twice delayed public disclosure of the issue, but, after 144 days, he said in his report that people needed to be made aware.

“The coordination period agreed with Microsoft has been exhausted, and testing shows that no robust mitigation for the broader vulnerability class is currently available,” Måløy wrote. “Two mitigation attempts, including a model upgrade, did not close the class.”

### How Copilot propagates a Word worm

Måløy explained the worm’s execution with an example involving an employee preparing a financial report for their company.

The employee downloads a market analysis from a trusted website to help with the preparation of a financial report in Copilot, unaware that the source had been compromised and the document they downloaded contains hidden malicious instructions. The hidden instructions (inserted as small white text in his proof of concept) tell Copilot to alter figures in the report the employee generates and to copy the worm into the report they create with Copilot.

If another employee later adds that report to their own work, the whole process begins again, and documents generated from it also contain the worm, and, as it spreads, it makes tracing the infection to its source extremely difficult.

“The attack can therefore continue without further involvement from either the compromised website or the original malicious document,” Måløy said. “The attacker does not need access to the victim’s Microsoft 365 tenant. The attacker only needs to share a malicious document with the victim.”

Copilot should use information in documents a user includes in its context for a project without treating instructions embedded in a document as additional prompts, Måløy said, but his research suggests it doesn't always do that.

REG AD

### A fundamental flaw

Måløy argues that he’s essentially dug up a new type of cross-domain prompt injection attack that abuses a fundamental part of modern LLM architecture.

“For AI-assistants to be useful, they often must process emails, documents, webpages, memories, tool outputs, and other information that may be controlled by an attacker,” the researcher said. But if an LLM has to process data in order to determine it contains an attack, the attack could already be influencing that determination.

“Relying on the model to detect XPIAs therefore resembles asking an interpreter to execute an untrusted program to determine whether that program is safe to execute,” Måløy asserted.

Were Microsoft or some other company to pop another model in front of that model to check for malicious content, it only moves the problem outward, Måløy said, creating a “LLMs all the way down” scenario.

## MORE CONTEXT

- [**Microsoft's solution to AI security: more AI and more acronyms**](https://www.theregister.com/security/2026/07/27/microsofts-solution-to-ai-security-more-ai-and-more-acronyms/5279140)
- [**Tech giants link hands to praise open AI models after OpenAI - Hugging Face attack**](https://www.theregister.com/ai-and-ml/2026/07/27/tech-giants-link-hands-to-praise-open-ai-models-after-openai-hugging-face-attack/5279061)
- [**AI's cheatin' heart will make you weep**](https://www.theregister.com/ai-and-ml/2026/07/21/ais-cheatin-heart-will-make-you-weep/5275784)
- [**AI insiders ask Uncle Sam to help slow the race they started**](https://www.theregister.com/ai-and-ml/2026/07/29/ai-insiders-ask-uncle-sam-to-help-slow-the-race-they-started/5280323)

“The long-term challenge likely lies in designing systems in which goals and intentions also exist independently of the information being processed,” he said. Until that time, Måløy argues, “any system that integrates an LLM into a trusted workflow today must assume that attacker-controlled content entering the model’s context will result in compromise at some rate.”

What can Copilot customers do to reduce the risk? Short of ditching Copilot, there’s not much.

“No customer-side remediation fully addresses the issue at the time of publication,” Måløy said, but he does have a few tips.

REG AD

Treat externally sourced documents as untrusted when using them in Copilot, he recommends, and fully review every single document before sending it to Copilot, and fully review any Copilot-generated or edited documents before distributing them.

Sheesh - if you’re going to have to actually read that stuff, you might as well just cut Copilot out of the loop and [do the thinking yourself](https://www.theregister.com/software/2025/02/11/some-workers-are-already-outsourcing-their-brains-to-ai/1094150).

Microsoft has been in touch to confirm the research, but the company's statement doesn't do anything to allay fears this is an unsolved issue.

“We have addressed the findings reported by the researcher and thank them for working with us through coordinated vulnerability disclosure. To address this class of risk, we use a defense-in-depth strategy with safeguards that block malicious instructions at multiple points and help keep tasks aligned with users’ requests. We are continuously strengthening these safeguards as the technology and threat landscape evolve. We encourage customers to install the latest updates, use multiple layers of security protection, treat content from unknown sources with caution, and review AI-generated content before using or sharing it.”

We also reached out to Måløy, but didn’t hear back before publication. ®

Updated at 1841 GMT on July 29 to add Microsoft's statement.

[artificial intelligence](https://www.theregister.com/tag/artificial%20intelligence) [ai and ml](https://www.theregister.com/tag/ai%20and%20ml) [copilot](https://www.theregister.com/tag/copilot) [microsoft](https://www.theregister.com/tag/microsoft) [security](https://www.theregister.com/tag/security)

REG AD

[![](https://image.theregister.com/5300669.jpg?imageId=5300669&panox=0.00&panoy=0.00&panow=100.00&panoh=100.00&heightx=0.00&heighty=0.00&heightw=100.00&heighth=100.00&width=960&height=432&format=webp&format=jpg)\\
\\
**AI agents hacked the hackers, stealing email addresses from security research org**\\
\\
Chained Zammad flaws enabled session hijacking, code execution, and root escalation in seconds](https://www.theregister.com/security/2026/10/01/ai-agents-hacked-the-hackers-stealing-email-addresses-from-security-research-org/5300652)

[**Cloudflare tries to outplay Jev with open-weight Clef models**\\
\\
Sure, it costs more, but it can handle images and video and it's available on Hugging Face if you have the hardware horsepower to run it locally](https://www.theregister.com/ai-and-ml/2026/10/01/cloudflare-tries-to-outplay-jev-with-open-weight-clef-models/5300649)

[**Huawei Cloud Rolls Out Enterprise AI Products Across the Board, Building an Open Agentic Cloud**\\
\\
PARTNER CONTENT: Huawei Cloud strengthens the silicon bedrock on the cloud](https://www.theregister.com/ai-and-ml/2026/09/25/partner-content-huawei-cloud-rolls-out-enterprise-ai-products-across-the-board-building-an-open-agentic-cloud/5298765)

[**Stanford prof is beating the drum for a new protocol to replace TCP**\\
\\
Homa is a rethink of networks for the AI age](https://www.theregister.com/networks/2026/10/01/stanford-prof-is-beating-the-drum-for-a-new-protocol-to-replace-tcp/5300629)

[![](https://image.theregister.com/238110.jpg?imageId=238110&panox=0.00&panoy=0.00&panow=100.00&panoh=100.00&heightx=0.00&heighty=0.00&heightw=100.00&heighth=100.00&width=960&height=432&format=webp&format=jpg)\\
\\
**OpenAI apes AWS Marketplace while Anthropic remains stubbornly Microsoftian**\\
\\
By including Baseten in its marketplace, OpenAI signals it wants its models to win on the merits, not through coercion](https://www.theregister.com/columnists/2026/09/30/openai-apes-aws-marketplace-while-anthropic-remains-stubbornly-microsoftian/5300056)

[**Cloudflare launches Data Platform with bland 'Basin' branding, promise of fewer fees**\\
\\
Serverless data management without egress fees, sort of](https://www.theregister.com/databases/2026/10/01/cloudflare-launches-data-platform-with-bland-basin-branding-promise-of-fewer-fees/5300618)

### TOP STORIES

- [![](https://image.theregister.com/5299648.jpg?imageId=5299648&x=0&y=0&cropw=100&croph=100&panox=0&panoy=0&panow=100&panoh=100&width=70&height=60)](https://www.theregister.com/ai-and-ml/2026/09/29/ai-models-keep-posting-screenshots-showing-sensitive-data-from-inside-tech-companies/5299640)
[**AI models keep posting screenshots showing sensitive data from inside tech companies**](https://www.theregister.com/ai-and-ml/2026/09/29/ai-models-keep-posting-screenshots-showing-sensitive-data-from-inside-tech-companies/5299640)

- [![](https://image.theregister.com/229400.jpg?imageId=229400&x=0&y=0&cropw=100&croph=100&panox=0&panoy=0&panow=100&panoh=100&width=70&height=60)](https://www.theregister.com/science/2026/09/25/astronomer-watches-starlink-satellites-sinking-to-build-a-planetary-barometer/5299036)
[**Astronomer watches Starlink satellites sinking to build a ‘planetary barometer’**](https://www.theregister.com/science/2026/09/25/astronomer-watches-starlink-satellites-sinking-to-build-a-planetary-barometer/5299036)

- [![](https://image.theregister.com/5299436.jpg?imageId=5299436&x=0&y=0&cropw=100&croph=100&panox=0&panoy=0&panow=100&panoh=100&width=70&height=60)](https://www.theregister.com/saas/2026/09/28/microsoft-tells-nonprofits-their-deleted-m365-data-isnt-coming-back/5299433)
[EXCLUSIVE\\
**Microsoft tells nonprofits their deleted M365 data isn't coming back**](https://www.theregister.com/saas/2026/09/28/microsoft-tells-nonprofits-their-deleted-m365-data-isnt-coming-back/5299433)

- [![](https://image.theregister.com/226413.jpg?imageId=226413&x=0&y=0&cropw=100&croph=100&panox=0&panoy=0&panow=100&panoh=100&width=70&height=60)](https://www.theregister.com/os-platforms/2026/09/29/google-ending-chromeos-support-two-years-early/5299674)
[**Google ending ChromeOS support two years early**](https://www.theregister.com/os-platforms/2026/09/29/google-ending-chromeos-support-two-years-early/5299674)

- [![](https://image.theregister.com/256583.jpg?imageId=256583&x=0&y=0&cropw=100&croph=100&panox=0&panoy=0&panow=100&panoh=100&width=70&height=60)](https://www.theregister.com/security/2026/09/29/fbi-to-shinyhunters-we-know-how-to-find-you/5299901)
[**FBI to ShinyHunters: 'We know how to find you'**](https://www.theregister.com/security/2026/09/29/fbi-to-shinyhunters-we-know-how-to-find-you/5299901)

- [![](https://image.theregister.com/4093591.jpg?imageId=4093591&x=0&y=0&cropw=100&croph=100&panox=0&panoy=0&panow=100&panoh=100&width=70&height=60)](https://www.theregister.com/ai-and-ml/2026/09/28/microsofts-copilot-super-app-comes-with-a-meter-attached/5299515)
[**Microsoft's Copilot super app comes with a meter attached**](https://www.theregister.com/ai-and-ml/2026/09/28/microsofts-copilot-super-app-comes-with-a-meter-attached/5299515)


### [AI](https://beta.theregister.com/tag/ai)

- [**Stanford prof is beating the drum for a new protocol to replace TCP** \\
\\
Homa is a rethink of networks for the AI age](https://www.theregister.com/networks/2026/10/01/stanford-prof-is-beating-the-drum-for-a-new-protocol-to-replace-tcp/5300629)
- [**Hot Dog! America's new chatbot is packed with wieners** \\
\\
Just ask America.gov and you'll receive a favorite July 4th food.](https://www.theregister.com/public-sector/2026/09/30/hot-dog-americas-new-chatbot-is-packed-with-wieners/5300292)
- [**Huawei boss claims homegrown AI chip sales top Nvidia in China** \\
\\
The chips may not be as advanced, but they won't get banned at a moment's notice, Eric Xu says](https://www.theregister.com/systems/2026/09/30/huawei-boss-claims-homegrown-ai-chip-sales-top-nvidia-in-china/5300266)
- [**Add one more AI worry to the nightmare scenario: self-replicating prompt injections** \\
\\
It's a worm attack, AI-style](https://www.theregister.com/security/2026/09/29/add-one-more-ai-worry-to-the-nightmare-scenario-self-replicating-prompt-injections/5299922)
- [**Zuckerberg touts enterprise AI push because Meta would never do anything to damage your reputation** \\
\\
New business unit to be led by former MongoDB CEO 'CJ' Desai](https://www.theregister.com/ai-and-ml/2026/09/29/zuckerberg-touts-enterprise-ai-push-because-meta-would-never-do-anything-to-damage-your-reputation/5299655)

### [Infosec](https://beta.theregister.com/security)

- [Security\\
\\
**Russians are posing as Signal support to launch phishing attacks** \\
\\
PLUS: US takes down Iranian propaganda sites; Marketing company asks 'Why Do We Have Your Information?' And more!](https://www.theregister.com/security/2026/03/22/russians-posing-as-signal-support-to-launch-phishing-raids/5221189)
- [Security\\
\\
**Microsoft patches failed to fix on-prem SharePoint, which is now under zero-day attack** \\
\\
PLUS: China upgrades smartphone surveillance tools; Ring eases anti-snooping stance; and more](https://www.theregister.com/security/2025/07/21/microsoft-warns-on-prem-sharepoint-users-of-a-zero-day/550805)
- [Black Hat and DEF CON\\
\\
**DEF CON Franklin project enlists hackers to harden critical infrastructure** \\
\\
Voting village reports have been so successful, says Jeff Moss, that the whole of DEF CON will now be included](https://www.theregister.com/special-features/2024/08/12/def-con-launches-public-policy-report-volunteer-program/408600)
- [Security\\
\\
**EQT buys majority share in Swiss cybersecurity biz Acronis** \\
\\
Went at equivalent of $3.5B+ valuation for entire firm, though portion sold not specified](https://www.theregister.com/security/2024/08/07/eqt-buys-majority-share-in-cybersecurity-outfit-acronis/853853)
- [Malware Month\\
\\
**Ten years since the first corp ransomware, Mikko Hyppönen sees no end in sight** \\
\\
On the plus side, infosec's a good bet for a long, stable career](https://www.theregister.com/special-features/2024/05/08/10-years-since-the-first-corp-ransomware-and-no-end-in-sight/1259096)

### [FOSS](https://beta.theregister.com/tag/FOSS)

- [**Firefox 157: Could bold new look be just what Mozilla needs?\*** \\
\\
Yet another new version of Firefox, with a significant reskin](https://www.theregister.com/software/2026/09/30/firefox-157-could-bold-new-look-be-just-what-mozilla-needs/5300059)
- [**KDE turns 30 and someone's brought an AI-native desktop proposal** \\
\\
Akademy talk imagines Plasma assembling itself around a personal model of each user](https://www.theregister.com/software/2026/09/18/kde-turns-30-and-someones-brought-an-ai-native-desktop-proposal/5297282)
- [**Shopify extends lifeline to Tailwind as vibe coding erodes web dev platform's bottom line** \\
\\
Acquisition gives open source CSS framework 'a stable long-term home'](https://www.theregister.com/devops/2026/09/10/shopify-extends-lifeline-to-tailwind-as-vibe-coding-erodes-web-dev-platforms-bottom-line/5295672)
- [**Switzerland tests a FOSS escape route from Microsoft 365** \\
\\
Swiss Army sticks a knife in American cloud apps with its own FOSS push](https://www.theregister.com/os-platforms/2026/09/09/switzerland-tests-a-foss-escape-route-from-microsoft-365/5294878)
- [**Feel peak Windows was 7? You might like Kumander Linux** \\
\\
Debian and Xfce – solid, sensible choices – with a pretty skin](https://www.theregister.com/os-platforms/2026/09/07/feel-peak-windows-was-7-you-might-like-kumander-linux/5294760)
- [**Canonical shuttering some of its legacy chat channels** \\
\\
The Ubuntu Pastebin went in June, IRC gets demoted next](https://www.theregister.com/os-platforms/2026/09/04/canonical-shuttering-some-of-its-legacy-chat-channels/5294524)

✕

Twitter Widget Iframe