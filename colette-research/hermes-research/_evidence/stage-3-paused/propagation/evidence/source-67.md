Context Collapse, Part 3 - AI Worming through Word

Contents

> I would like to thank Microsoft product teams and Microsoft Security Response Center (MSRC) for collaborating with me on this technical analysis and mitigation of the disclosed vulnerabilities. The editorial opinions reflected below are solely the author’s and do not necessarily reflect those of the organizations I collaborated with.

## Summary

The findings described in this post are part of a coordinated disclosure with [MSRC](https://www.microsoft.com/en-us/msrc) and Microsoft product teams. Microsoft was provided with reproduction steps, videos, environmental assumptions, and the exact proof-of-concept (PoC) prompts used during testing. They were also informed of a 90-day coordination period before disclosure. This was extended two times, resulting a 144-day coordination period.

In parts [1](https://enklypesalt.com/posts/context-collapse-part1-poisoning-copilot-memory/) and [2](https://enklypesalt.com/posts/context-collapse-part2-when-emails-instruct/) in this series, I have shown how external inputs could influence Copilot responses and, in some cases, potentially lead to confidentiality impacts through [Cross-Domain Prompt Injection Attacks (XPIAs)](https://genai.owasp.org/llmrisk2023-24/llm01-24-prompt-injection/). This report builds on those findings and extends the XPIA analysis from single-interaction compromise to propagation across trusted document workflows. It shows that attacker-controlled instructions in one document can be copied into Copilot-generated or Copilot-edited Word documents, causing those downstream documents to become new carriers of the same attack.

Previous examples of AI-worms exist. Notably, [Morris II](https://arxiv.org/abs/2403.02817) demonstrated self-replicating prompt propagation in GenAI-powered email-assistant ecosystems. However, to my knowledge, this is among the first public demonstrations of document-borne AI-worm self-propagation through normal workflows in a mainstream commercial productivity suite.

The reported scenario is:

1. Malicious instructions hidden in an externally shared document could make Copilot alter drafted or edited documents in Word and propagate the attack to new documents.

## The full attack in brief

### The attack

An attacker places hidden instructions in a document that is later used as source material in Copilot for Word. Copilot may interpret those instructions as part of the user’s request, causing it to manipulate the document being drafted or edited. Copilot may then also copy the hidden instructions into the resulting document, turning that document into a new carrier. If the carrier is subsequently used in another Copilot-assisted workflow, the instructions can trigger again and propagate into further documents, even without the attacker’s original document being present.

### Example

Consider an employee preparing a financial report. The employee downloads a market analysis from a trusted website that has been compromised, unaware that the document contains hidden instructions. The employee then includes the analysis as source material when drafting the report with Copilot. The hidden instructions cause Copilot to alter internal figures in the financial report and copy the attack into the new document. The employee saves and shares the apparently legitimate report internally. Later, a colleague uses it as source material for another report; the instructions trigger again, alter the new report, and copy themselves forward. The attack can therefore continue without further involvement from either the compromised website or the original malicious document. As affected reports are reused, additional reports and documents can become carriers of the attack.

## Disclosure status at publication

- Vendor: Microsoft
- Coordinated disclosure: Handled through MSRC and Microsoft product teams
- Included in this post: XPIA and self-propagation scenario in Microsoft Copilot for Word
- Customer action: No customer-side remediation fully addresses the issue at the time of publication. Customers can reduce exposure by:
1. Treating externally sourced documents as untrusted when used with Copilot.
2. Reviewing any attached document before starting a Copilot generation or edit.
3. Carefully reviewing Copilot-generated or Copilot-edited documents before reusing, sharing, or distributing them.
- Microsoft-side status: Testing has reproduced the attack with all current mitigations deployed. At the time of publication, no robust mitigation for the broader vulnerability class is available.

## A note on disclosing before a fix

Unlike Parts 1 and 2, this scenario remains exploitable at publication. I have weighed that carefully. The coordination period agreed with Microsoft has been exhausted, and testing shows that no robust mitigation for the broader vulnerability class is currently available. Two mitigation attempts, including a model upgrade, did not close the class.

I have therefore chosen to disclose at the class level rather than the payload level. My reasoning is that defenders cannot reduce exposure to a risk they are unaware of, and the propagation mechanism described here affects ordinary document workflows that many organizations already rely on. Withholding the existence of the issue would leave those organizations unable to make an informed decision, while providing no additional protection.

## Disclosure timeline

- **2026-03-06**: Initial report submitted to MSRC with reproduction steps, videos, environmental assumptions, and PoC prompts.
- **2026-03-09**: MSRC acknowledged receipt and opened a case.
- **2026-03-31**: Microsoft confirms the reported behavior.
- **2026-03-31**: Microsoft product teams began mitigation work; ongoing technical discussion.
- **2026-04-03**: First mitigation go-live (The new “Edit with Copilot” experience)
- **2026-04-09**: Original attack prompt wording verified mitigated with “Edit with Copilot”.
- **2026-04-09**: Attack behavior reproduced in “Edit with Copilot” using a new XPIA prompt task (manipulating financials). Reported as separate case to MSRC.
- **2026-04-10**: MSRC acknowledged receipt and opened a case.
- **2026-04-10**: Microsoft product teams began mitigation work; ongoing technical discussion.
- **2026-06-08**: At Microsoft’s request, public disclosure was moved to 2026-07-15.
- **2026-07-14**: Second mitigation fix go-live. This mitigation consisted of upgrading the underlying model to GPT-5.5.
- **2026-07-15**: Successful exploit with worming reproduced using GPT-5.6, the latest available model at the time.
- **2026-07-15**: I suggest we postpone disclosure a further two weeks to 2026-07-28, to allow time for a new mitigation.
- **2026-07-15**: Microsoft agreed.
- **2026-07-28**: Attack class still reproduces.
- **2026-07-28**: Coordinated public disclosure (this post).

## Threat model

The attacker does not need access to the victim’s Microsoft 365 tenant. The attacker only needs to share a malicious document with the victim. This can be done through SharePoint, Teams, Outlook or any other way of sharing documents.

## Security boundary and observed behavior

The relevant security boundary in this scenario is the boundary between attached documents and the current drafting document. If any of the attached documents contain an XPIA the attack may trigger.

Copilot must read every attached document to determine which parts to include in its current drafting task. However, attached documents should be treated as untrusted information, not trusted user instruction.

**Boundary violation**

Attacker-controlled documents are downloaded or shared through email/sharepoint/other sharing option. If such documents are attached to Copilot during a drafting task, trust is broken.

**Expected behavior**

When a user asks Copilot to draft e.g. a Q1 financial report based on attached documents, Copilot should utilize the information in the attached documents without treating instructions embedded within documents as authoritative instructions.

**Observed behavior**

Instructions embedded in documents cause Copilot to alter its behavior. Here presented as:

1: Copilot silently changing numerical values in financial reports

2: Copilot propagating the full XPIA by pasting into downstream documents, which may then be used as attachments in later drafting sessions\

## Crossing the trust boundary in Word

The initial attack vector for these scenarios uses a malicious document. The malicious document contains a JSON-formatted malicious prompt that triggers the attack when the document is included in Copilot’s context. The prompt can be rendered as white text on a white background and in a small font size to conceal it from the victim. Since Copilot for Word strips all text formatting like color and font size before passing the text into the underlying Large Language Model (LLM), this text remains fully readable to Copilot even though the victim cannot see it. The attack can be further concealed by embedding it in a seemingly benign document with task-relevant text.

This attack requires the malicious document to be included as part of Copilot’s context in Word. Thus, depending on the version of Copilot in use, the victim must either:

1. Actively attach or upload the document in Copilot for Word.
2. Use the “Edit with Copilot” functionality in work/Work IQ mode and let Copilot find the malicious document in the victim’s OneDrive. In this case, Copilot must deem the document relevant and include it in the context. An attacker therefore needs to craft a document that increases the likelihood of either or both.

The exploit is relevant both for the “magic pen” and the “Edit with Copilot” functionalities in Word.

The attack happens in two stages. The first stage establishes foothold and in the second stage the attack self-propagates across documents that use Copilot for Word as part of drafting or editing.

### Stage 1:

In the first stage the attacker has crafted a document that contains a malicious hidden prompt. In my initial PoC I used a document that only contained the malicious prompt as white text on white background. This was done to illustrate that the malicious document did not need to be relevant to the victim’s task for Copilot to use it. If it was included in the context, it is read and therefore the attack may trigger.

_The PoC prompt was structured in two parts:_

- The first part contained the instructions on how to affect a document. This could range from slightly changing meanings of summaries to altering numbers in financial documents. The key was formulating the prompt in a way that made Copilot believe it was task-relevant and benign. In many of my experiments I actually needed to also instruct Copilot to highlight which changes it made, since they were often meaningful changes that were difficult to spot. This shows how effective the attack is at subtly changing the text in meaningful ways that easily elude even an attentive reviewer. In a real-world setting, the attacker would obviously not include such instructions. For the rest of this disclosure, therefore, I’ll use altering numbers in financial reports since that is an immediately visible change.

- The second part contained the instructions to self-propagate the attack. The exact wording also matters here, but it was generally framed as serving the purpose of tracking sources in downstream documents. It also contained instructions on how to hide itself, framed as instructions to improve readability.


_Figure 1: The initial attack vector document. I created a full mock company named Tfosorcim Ltd. for this PoC, with mock economics and vision. This attack vector document is a fake market analysis made using information about the company that would typically be available to an attacker. The attack is appended at the end of the document using white text. \[Most of the XPIA text is blurred for security\]_

Once this malicious document was included in the context when drafting or editing a document with Copilot for Word, the attack would trigger and Copilot would execute the instructions. Thus, the affected document would have financial numbers changed. Copilot would then also copy the entire malicious prompt into the bottom of the affected document using white text and font size 8, effectively concealing it from the victim.

_Figure 2: The downstream draft generated by Copilot used my malicious document as an attachment (\[att\] Direct wmr.docx). In the resulting Q1 financial report draft, all financial numbers are halved. The screenshot also shows other attached documents (Tfosorcim internal documents)._

_Figure 3: The figure demonstrates that GPT-5.6, the latest model from OpenAI at the time of writing, was used in these PoCs._

_Figure 4: After having halved all financial numbers in the Q1 financial report draft, Copilot also appends the full attack prompt using white text to effectively conceal it from the victim. It also makes no mention about its halving of numbers or that it includes the attack. Thus, the victim is clueless of it. \[Most of the XPIA text is blurred for security\]_

_Figure 5: Copilot does not require the victim to attach the malicious document though. In this screenshot the victim only instructs Copilot to write a Tfosorcim Q1 financial report. Copilot then searches through the victim’s OneDrive to find relevant documents. Among the documents, we find the malicious Market Analysis document. This document does not reside in the same folder as the rest of the Tfosorcim document. However, Copilot still finds it, reads it and is successfully exploited._

### Stage 2:

Stage two is the self-propagation stage. It relies entirely on the instruction for Copilot to copy the malicious prompt into the affected document. Once the affected document contained the prompt, the new document itself became the new attack vector.

_Figure 6: The screenshot shows a new drafting session using Copilot. This time the original attack vector is no longer included among the attachments. However, the previously created document is (Tfosorcim Q1 2026 report.docx). The result is the same, and Copilot again halves all financial numbers in the drafted Q2 financial report._

_Figure 7: In addition to halving all financial numbers, Copilot adds the full attack prompt, again using white text. Thus, the attack propagates through Word documents, effectively creating a document-borne AI worm. \[Most of the XPIA text is blurred for security\]._

Of note, this new attack vector is now an internally created document, with all the trust that follows. Thus, the victim needs only share this document with coworkers for the attack to spread. If the victim or a colleague then uses the affected document as an attachment to Copilot for Word while drafting or editing, the attack spreads to these new documents.

In all reported PoC scenarios, Copilot would alter generated or edited documents and copy the hidden instruction into these documents. When these documents were themselves used as part of the context for new downstream documents, the attack triggered again. Note that for the second phase, the original attack document was no longer part of the attachments for the new downstream documents, yet the attack triggered and spread to these as well.

### Impact

Since the attack is able to spread through internal documents, once it has moved beyond its initial point of entry, the traceability of the attack becomes extremely difficult. This is further exacerbated by each document being created by a legitimate internal resource and that Copilot edits are not made visible after they have been approved by the victim. The broader concern is that, if the attack silently spread within an organization through ordinary document workflows, it could erode the informational foundation on which organizations make decisions.

In addition, organizations that are not aware that they are affected by the attack are also likely to spread it to other organizations through collaborative efforts on shared Microsoft SharePoint sites or shared Microsoft Teams. Thus, the initial attack vector for a particular organization may actually come from an already affected trusted partner. This again increases likelihood of the victim choosing to include the affected document in the Copilot for Word context during drafting.

Recently Copilot is also becoming more deeply integrated with systems such as Microsoft Cowork or Microsoft Scout, which extend the assistant to automatic manipulation and creation of documents, tools, and collaborative workflows. In such systems the practical impact of the issues described here may scale rapidly. The underlying mechanism remains the same, but the potential surface over which it can propagate or influence expands at machine speed.

## Mitigating the vulnerabilities

Microsoft successfully mitigated the originally submitted PoC prompt, and deployed multiple fixes over the course of this disclosure. Each of these raised the bar by closing the specific payloads reported, and reproducing the behavior afterwards required altered payloads rather than reusing the old ones directly.

The original report, however, also described the broader vulnerability class, in which instructions embedded in a source document could influence Copilot’s generation and copy themselves into downstream documents. Changing the requested action or wording changes the payload, but not the underlying vulnerability or propagation mechanism. Using a modified payload, the complete attack chain has been reproduced with all mitigations deployed (the PoC in this report is one such case). The vulnerability class therefore remains exploitable at the time of publication.

That the class is not yet fully closed reflects how hard the underlying problem is. As the closing thoughts discuss, the weakness is architectural and shared across current LLM-based systems. I’m not aware of a complete mitigation for this class in any comparable product today. Fully resolving it requires research rather than a single patch. Within those limits, Microsoft’s fixes meaningfully reduce exposure, and the memory and email-body vectors covered in Parts 1 and 2 were mitigated outright. I would like to thank Microsoft for their continued and substantive effort on a genuinely difficult problem.

## Implications

Taken together with the two previous parts in this series, these findings point to a broader issue in modern work environments. Namely that the integrity of information becomes a primary security concern in systems that integrate LLMs as part of their operating workflows. The scenarios presented show that attacker-controlled content can not only influence individual outputs and potentially leak information. The attacks themselves can also be replicated and self-propagate through normal user workflows.

This introduces challenges that extend well beyond initial exploitation. Once malicious instructions are embedded in generated content, they may persist across documents, be redistributed by legitimate users, and be reintroduced into new contexts. At that point, the attack is no longer dependent on its original entry point. It has instead become part of the system’s internal information flow.

A related implication is the loss of traceability. Since affected content is generated and modified through legitimate workflows, the origin of the manipulation becomes difficult to identify after the fact. This complicates both detection and response, particularly in environments where such content is widely shared.

Independently of prompt-injection prevention, generated documents should preserve provenance for source material and model-performed edits in metadata. Such controls would not prevent the underlying injection, but they could make traceability much easier.

## Closing thoughts

The findings in this series point beyond any single product or implementation. They expose a broader architectural weakness in current LLM-based systems.

For AI-assistants to be useful, they often must process emails, documents, webpages, memories, tool outputs, and other information that may be controlled by an attacker. To process that information, it must be included in the model’s context window, where it participates in the same computation as system instructions, user requests, and other trusted information.

This creates a fundamental problem: the LLM must process external content to determine what it means, whether it is relevant, and whether it contains an attack. But by the time it makes that determination, the attacker-controlled tokens are already influencing the computation that produces it. The content being inspected participates in the act of inspection. Relying on the model to detect XPIAs therefore resembles asking an interpreter to execute an untrusted program to determine whether that program is safe to execute.

Detecting and removing malicious content before it reaches the target model merely moves the same problem outward.

Because LLMs can recover semantics across radically different representations, an effective detector must possess comparable semantic recovery capabilities. A detector weaker than the target LLM will cover a smaller representational space, leaving malicious formulations that the target understands but the detector fails to recognize.

The only generally available technology with comparable semantic capabilities is another LLM. Placing one model in front of another may reduce the success rate of particular attacks, but it creates an “LLMs all the way down” problem, where every LLM introduced to protect another LLM must itself be protected.

The long-term challenge likely lies in designing systems in which goals and intentions also exist independently of the information being processed. Current LLM architectures provide no reliable separation between intention and interpretation. Thus, in current systems with embedded LLMs, attacker-controlled information can influence not only what the model produces, but what the model believes it has been asked to produce.

For that reason, any system that integrates an LLM into a trusted workflow today must assume that attacker-controlled content entering the model’s context will result in compromise at some rate.

## Change Log

The following is a change log that shows which part of this post have been changed and at what time. Spelling mistakes and similar errors will not be logged. However, I will strive to include any meaningful changes to the post.

- 2026-07-28: Change log added
- 2026-07-30: Fixed line in timeline stating that attack class reporduces.

[Coordinated Vulnerability Disclosures](https://enklypesalt.com/categories/coordinated-vulnerability-disclosures/)

[ml](https://enklypesalt.com/tags/ml/) [llm](https://enklypesalt.com/tags/llm/) [cvd](https://enklypesalt.com/tags/cvd/) [vulnerability](https://enklypesalt.com/tags/vulnerability/)

This post is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) by the author.

Share

## Trending Tags

[llm](https://enklypesalt.com/tags/llm/) [ml](https://enklypesalt.com/tags/ml/) [prediksjon](https://enklypesalt.com/tags/prediksjon/) [statistikk](https://enklypesalt.com/tags/statistikk/) [cvd](https://enklypesalt.com/tags/cvd/) [lineær regresjon](https://enklypesalt.com/tags/line%C3%A6r-regresjon/) [vulnerability](https://enklypesalt.com/tags/vulnerability/) [agenter](https://enklypesalt.com/tags/agenter/) [attention](https://enklypesalt.com/tags/attention/) [autoregressive språkmodeller](https://enklypesalt.com/tags/autoregressive-spr%C3%A5kmodeller/)