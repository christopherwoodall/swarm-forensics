The Hugging Face incident and other third-party impact from misaligned models \| OpenAI

# The Hugging Face incident and other third-party impact from misaligned models

As AI systems become more capable and autonomous, misaligned behavior can translate into consequential actions in the real world, including cybersecurity incidents and other outcomes that developers may not have anticipated. Understanding how these behaviors emerge, how they escalate, and how to detect and respond to them is therefore an increasingly important part of building and deploying advanced AI systems safely.

We initially understood the Hugging Face incident primarily as a security issue, since it involved a platform-level compromise. It remains the most severe activity of this kind that we have identified from our models to date, and it was driven primarily by a highly capable, internal-only research model. We have since understood that this intrusion was driven by models resorting to misaligned strategies to solve hard tasks, as documented in the Hugging Face technical report. Cybersecurity incidents are one manifestation of that risk; [misalignment](https://openai.com/index/emergent-misalignment/) can also lead to other unexpected or concerning behavior that falls outside traditional security categories such as our models posting on third party sites—something we’re calling “agent spam”. And we need to address both.

We have continued reviewing broader activity, prioritizing the more serious incidents and expanding to lower-severity misaligned activity, including agent spam.

This page brings together our reports and updates on the Hugging Face incident, related research and public presentations, additional activity we have identified, what we have learned about the role of model misalignment, and measures we’re taking to strengthen our systems. We will update this page as our investigations progress.

**Quick Links**

- [Hugging Face Blog](https://openai.com/index/hugging-face-incident-and-the-road-ahead/)

- [Hugging Face Technical Report⁠(opens in a new window)](https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf)

- [Black Hat 2026⁠(opens in a new window)](https://www.youtube.com/watch?v=87DyyMV0kCY)

- [METR and Redwood Research Report⁠(opens in a new window)](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/#core-takeaways-about-this-incident)

- [Pacing model development in an era of cyber-critical capabilities](https://openai.com/index/pacing-model-development-cyber-capabilities/)


* * *

## Activity affecting third parties

In order to better understand the scope of these unexpected behaviors, we have been conducting a broad review into our models’ activities on the internet during training and evaluation. As part of our review, we are identifying and notifying third parties on a rolling basis, starting with cases where:

- Our models may have bypassed a third party’s security controls or may have impaired the availability of an online service; or

- Misalignment cases negatively impacted third-party websites or services.


Based on our review to date, we have notified dozens of third parties using the criteria above. Our review of past activity is ongoing and will require significant time and resources. We will notify additional third parties as that work continues.

Below, we are publishing anonymized summaries to describe the kinds of misaligned activity that we observed, and we will update these descriptions as we notify additional third parties and as our understanding develops. Additionally, we will share relevant updates regarding the status of review. We will generally omit names and other identifying details where needed to protect affected parties, although informed parties may choose to share publicly the information we provide them.

#### Summaries of the Activities Observed

Our review and notification process to date has identified the following categories of activity:

- **Access control bypass:** Agents reach information or features that normally require an identity check, specific permission, subscription, or an account. For example, it used a different web address, changed details in a request, or relied on a login session that gave it more access than expected.

- **Use of exposed credentials:** Agents found login details or access keys that had been made publicly available and used them to access a service.

- **Query or command injection:** Agents entered text into a website or service that the service treated as an instruction, rather than ordinary input. This could cause the service to run a database query, application code, or a command on its server.

- **Access to runtime internals:** Agents read files containing a service’s implementation or interacted with a background system meant for internal use. In these cases, the agent reached parts of the service that were outside its intended access.

- **Agent spam:** Agents post information to third party sites that may alter information on those sites and require cleanup, including for example using public wiki pages as shared message boards.


* * *

### A timeline of events

## September

Sort

Safety

September 30

Link copied to clipboard!

_**September 30, 2026: Our process for reviewing and disclosing model activity**_

On September 25, we shared an update on our ongoing review of model activity before the Hugging Face incident and our approach to notifying affected organizations and sharing findings publicly. Today, we’re providing more detail on how that review works, including more on how we identify and investigate potential cases and verified information that organizations can use. Our goals are to give affected organizations information they can use, improve our own systems, and share findings that help the broader AI and security communities strengthen safeguards.

We’re now one month into the review. So far, we have not identified another compromise of third-party systems involving our models that is comparable in scale or severity to the Hugging Face incident. The review remains ongoing, and we expect to identify more cases as we work through historical records.

### **Why our models were interacting with the internet**

AI models are more useful if they can interact with the internet to carry out automated tasks for their users. Some examples:

- Looking up information across lots of websites in order to produce an analytical research report

- Downloading software packages needed to write a functional software program that depends on those packages

- Reading online documents in eg Google Docs and inputting information into them as part of an automated workflow


Thus when training and evaluating models, some of the tasks that we train and evaluate them on may require internet access or simulated internet access so the model can perform better and more reliably on them, ultimately to provide value to users.

In some cases, models used internet access in unintended ways or, in retrospect, did not have the ideal restrictions applied. Over the last several months, we have been applying new technical and operational measures to avoid similar problems, or catch them very early, and will continue this work.

### **Setting a standard for AI incident notification and reporting**

We’re developing standards for notifying organizations privately and reporting findings publicly. These standards will apply to this historical review and future incidents, with the aim of establishing practices the broader AI community can adopt.

- **Private notification** gives affected third parties information needed to investigate and address potential security or other technical issues related to our models’ activity. Under our current [security standard](https://openai.com/hugging-face-incident-and-misalignment/) we notify organizations when our models bypass their security controls without authorization or impair the availability of their systems or services. We are also developing a private notice standard for misaligned agent activity that negatively impacts a third party website or service.

- **Public reporting** shares findings about model behaviors and new types of weaknesses in safeguards so that the broader AI and security research communities can improve safety. These reports will be shared through our [public misalignment reports](https://openai.com/index/model-misalignment-reporting-framework/) and [ongoing updates to our Hugging Face work](https://openai.com/hugging-face-incident-and-misalignment/).


We err on the side of notification when our models’ activity exposes a potential security vulnerability, even in cases where it is unclear if the information accessed was intended to be public, so the organization can investigate and take appropriate action.

### **The scale and scope of the review**

To make this review thorough, we’re searching through a large volume of data covering approximately 50 petabytes. One of the drivers of this volume is the nature of compute scaling – a handful of training and testing runs can generate a large volume of data because of the use of tens of thousands of GPUs on diverse tasks.

We’re working back through the records month by month, looking for potential unintended activity beyond the cases we’ve already found. To put that in perspective, if that were all plain English text, it would take one person about 66 million years to read it at 240 words a minute, reading nonstop without ever sleeping or taking a break.

AI helps us sift through these records far faster than manual review alone would allow. We’re currently dedicating about 7,000 GB200 and GB300 GPUs to this effort, at a cost of over half a million dollars a day, and plan to increase computing power as we refine our process.

As of September 26, our teams have notified over 100 organizations about activity that met our notification criteria. Notification does not mean that any private information was accessed, or that there was a compromise of any third-party system.

### **How we investigate and notify affected organizations**

We use four automated steps to identify potential cases, starting broadly to reduce the chance of missing important activity and progressively narrowing the results before human review.

1. **Broad search.** We search for records where models accessed and changed websites or took actions involving passwords, API keys, access tokens, and other sensitive credentials.

2. **First AI-enabled review.** We use AI models with low test-time compute for a fast first pass. They review relevant records, including the models’ recorded reasoning, known as “chains of thought”. They flag anything that might need a closer look, including actions a model considered but didn’t take. We keep this review broad to avoid filtering out important activity too early.

3. **Second AI-enabled review.** We use more test-time compute so the AI models can review each remaining record in more detail. They separate harmless activity from behavior that may need attention, explain why records were flagged, and assess how serious the activity may be.

4. **Third AI-enabled review.** We use even more test-time compute and draw on findings and patterns from earlier cases. The AI models group behavior by type, look for patterns across multiple agents on the same domain, and narrow the results further before human investigators review them.


![From records to informed action. AI-enabled review begins with broad search to find potentially concerning activity, screens to flag activity for closer review, refines to filter out known harmless activity, and uses targeted review to identify actions to investigate. These are not confirmed findings. Every surfaced case undergoes human review: investigation and verification take 45 minutes to several days per case, reconstructing events from technical evidence. Reviewers then assess disclosure and notification requirements and may revisit evidence. The outcome can be public disclosure, third-party notification, both, or neither.](https://images.ctfassets.net/kftzwdyauwt9/2H10gWINtjHKdEsQkk6dwA/440b27dd97c29d18bc1490f1ba6ffa6a/light.svg?w=3840&q=90)

As we learn more, we refine this process and use new findings to improve its accuracy.

An automated flag is not a confirmed incident. A model’s chain of thought can include ideas it never acts on, attempts that fail, and descriptions that need to be checked against the evidence. Human investigators review the automated findings alongside our logs and other evidence, which may be incomplete or conflicting. They remove duplicate findings, reconstruct what happened, and assess whether the activity meets our notification criteria.

For example, suppose a model researching a county’s weather statistics finds an access key online and uses it to request information from a web-accessible database. The key’s presence online does not establish whether it was intended for public use. A successful request does not, by itself, establish whether the information returned was public or private. Investigators must examine the context, what information the model actually received, whether it modified or transmitted anything, and whether the same access could still be possible. Other cases may require examining different means of access, potential security weaknesses, and related activity involving other accounts or organizations.

Applying that judgment is a substantial part of our investigation, and can require several rounds of review. Our aim is to give organizations enough reliable information to decide what to investigate or address.

### **How our work intersects with 3rd party research reports**

We appreciate independent researchers who study AI agent activity on the open web and share what they find. We compare their findings with our own records and seek additional information where needed. Some findings involve activity we’ve already investigated and, where appropriate, disclosed to affected organizations. Others involve activity we’re still reviewing or hadn’t previously identified.

Independent research and our own investigations rely on different sources of information. Researchers make their own decisions about when to publish their findings, and sometimes we receive them shortly before publication or once they become public. That can leave us trying to balance the need to follow our process to responsibly notify potentially affected organizations while acknowledging that key facts remain under review. We recognize that researchers’ independence is important and that there's no perfect way to resolve this challenge, but we’ll continue working to be as thoughtful and responsive as we can, and to improve our approach as we learn.

### **What comes next**

We expect to find more cases and notify more organizations as we review historical activity. Some notifications may concern events from months ago. We’ll be clear about when the activity happened, when we found it, what we know, and what remains uncertain.

Since the Hugging Face incident, we’ve [strengthened security controls⁠](https://openai.com/index/hugging-face-incident-and-the-road-ahead/#the-road-ahead), restricted internet access, separated research environments more clearly, expanded monitoring, and added more training to avoid harmful or unauthorized actions. This review will help us see how activity changed across model versions and whether those measures are working, including where we still need to improve detection and prevention.

We will continue sharing findings and progress through our existing [reporting⁠(opens in a new window)](https://alignment.openai.com/misalignment-reports/) [pages](https://openai.com/hugging-face-incident-and-misalignment/), while protecting affected parties’ privacy, so others can use what we learn to understand and address these risks.

Safety

September 28

Link copied to clipboard!

_**September 28, 2026:**_ [_**How we will do better for Australia**_](https://openai.com/index/how-we-will-do-better-for-australia/)

We've published a blog outlining what we know about the incidents affecting Australian government websites, changes to our research safeguards, and our commitments to provide resources and expertise to support affected agencies and Australian governments’ work on AI safety and cybersecurity.

Safety

September 25

Link copied to clipboard!

_**September 25, 2026: We identified cases where agents in our research environment transmitted training and evaluation data while using third-party services.**_

As part of our ongoing investigation, we have identified cases where agents in our research environment transmitted training and evaluation data while using third-party services. This is not an appropriate use of this data, and these cases occurred before we implemented the safeguards described in our [technical report⁠(opens in a new window)](https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf).

Some of our training data contains content from, or derived from, [training-eligible user interactions⁠(opens in a new window)](https://help.openai.com/articles/5722486-how-your-data-is-used-to-improve-model-performance). Any data which is not eligible for training, as controlled by users or enterprise admins, is not included. For explicitness, data from enterprise or business accounts and API usage is excluded unless an admin has enabled it. Before including eligible data, we take steps to [protect privacy](https://openai.com/index/how-chatgpt-protects-privacy/) by disassociating it from account information and using a version of the [OpenAI Privacy Filter](https://openai.com/index/introducing-openai-privacy-filter/) to redact personal details such as names, contact information, and account numbers. Our technical approach and privacy policy prevent us from reassociating this data with the original user account.

While the vast majority of the impacted training and evaluation data is not user-derived; we have identified 53 instances to date where user-provided images were posted to image-hosting sites as links that weren’t publicly listed. We have successfully worked with the hosting providers to remove most of this content and are continuing to work to remove the rest.

As part of our response to our ongoing investigation, we have [improved our training and evaluation processes](https://openai.com/index/hugging-face-incident-and-the-road-ahead/), including building safety cases, securing and red-teaming our systems to prevent the model from exfiltrating data, and implemented additional monitoring. We are continuing to review agent activity in research and evaluation runs, working backward month by month starting from the Hugging Face incident. We will provide further updates as our investigation progresses.

Safety

September 25

Link copied to clipboard!

_**September 25, 2026: Providing an update on our ongoing review and third-party notifications**_

After the Hugging Face incident, we committed to conducting a much broader review of misaligned models during training and evaluation. That review is ongoing. We have implemented a [framework](https://openai.com/index/model-misalignment-reporting-framework/) for identifying, classifying, and responding to misaligned behavior. We are also conducting an extensive review of a high volume of actions taken by models during training and evaluation runs.

While our review is ongoing, we want to share more about this work and make sure people understand our notification and disclosure process.

The vast majority of actions we’ve reviewed were completions of mundane research tasks, such as accessing publicly available web content to answer questions. Our investigation focuses on instances where agents interacted with third-party websites in ways that went beyond their assigned tasks or intended methods. Most cases identified so far have been low severity, with limited or no evidence of meaningful impact. Given the scale of the review required, and the need to verify each case, this work will take months to complete.

**Notifying affected organizations**

As we verify cases that meet our disclosure criteria, we are notifying affected organizations and sharing technical findings to support their investigations.

A notification from OpenAI should not automatically be interpreted as notice of a significant security incident. Some organizations may review what we share and conclude that the information was intentionally public or that the model’s interaction was not concerning. Others may identify a design issue or security weakness they want to address.

Some of the websites involved are operated by governments, universities, public agencies, and other institutions. That is partly because models performing research tasks are often directed toward authoritative sources of public information.

We have and will continue to share relevant findings with the affected entities and are providing technical information to support their review. We appreciate their engagement and will continue working constructively with them.

**Sharing findings publicly**

We will continue to publish anonymized summaries of our findings while giving affected organizations time to investigate possible weaknesses before we identify them or share technical details. Some have wanted to publicly disclose and others have asked us not to. Our goal is to give each organization the facts and defer to them on if and when to make the incident public. We believe in thorough and transparent incident reporting whenever possible. Independent researchers are also identifying and disclosing activity, and we appreciate when they share their findings.

Safety

September 11

Link copied to clipboard!

_**September 11, 2026: We are investigating new claims from a report that our AI agents carried out activity on RubyGems in May 2026.**_

Based on our review, our agents used the RubyGems platform to access the internet to carry out benign tasks and retrieve public information. Based on our review to date, we have not been able to verify the specific claims of our models uploading malicious packages detailed in the report. We’ll continue to investigate and share findings as part of our broader review of agent activity during training and evaluation.

Safety

September 6

Link copied to clipboard!

_**September 6, 2026: Our Chief Scientist Jakub Pachocki shared an**_ [_**essay**_](https://openai.com/index/an-alien-mind/) _**that reflects**_ _**on increasingly capable AI**_ _**and the ongoing research needed to keep systems aligned.**_

_“_ _Currently I believe that no lab has solved alignment and monitoring to a sufficient degree to continue responsibly scaling at maximum speed for much longer. I expect and hope for voluntary slowdowns to become commonplace until shared safety bars are established. And I believe that international coordination on future AI development needs to become a top priority for governments around the world.”_—Jakub Pachocki

Safety

September 5

Link copied to clipboard!

**_September 5, 2026: We_** [**_shared a response on X_** ⁠(opens in a new window)](https://x.com/OpenAI/status/2096133504417616165) **_to a report that our AI agents accessed a public wiki website and used it to communicate as a shared message board._**

When we initially discovered this wiki activity, we assessed it as similar to other forms of misalignment behavior we had been studying and disclosing. Historically, we and the broader industry have treated misalignment largely as a research question, which gets communicated in research publications such as systems cards.

Industry practices for disclosing model misalignment activity that does not constitute a security incident are still developing. We are developing our own criteria for reporting this kind of activity to advance the industry’s understanding of these issues, and will share it soon.

Safety

September 4

Link copied to clipboard!

**_September 4, 2026: The report “_** [**_Discovery of a new OpenAI agent message board_** ⁠(opens in a new window)](https://collusion.wiki/) **_” is published._**

This third-party report details OpenAI agents communicating through a shared message board on a public wiki website. We were not given an opportunity to review the full report before publication, and do not comment on the findings or methodology of external research without reviewing in full. We began reviewing the report as soon as it was available.

## August

Sort

Safety

August 26

Link copied to clipboard!

**_August 26, 2026: We publish the Hugging Face incident technical report._**

- We published [our findings from the Hugging Face incident⁠](https://openai.com/index/hugging-face-incident-and-the-road-ahead/) and the steps we’re taking to strengthen security and model alignment.

- Separately, METR and Redwood Research conducted an independent investigation of model alignment issues involved in this incident, and they publish their [own report⁠(opens in a new window)](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/) ⁠.


Safety

August 18

Link copied to clipboard!

_**August 18, 2026: We share that we’re**_ [_**pacing model development**_](https://openai.com/index/pacing-model-development-cyber-capabilities/) _**in an era of cyber-critical capabilities.**_

We share an update that we’ve tightened safeguards for increasingly capable models by temporarily slowing frontier training, pausing our largest planned RL run, and introducing stricter security controls in our research environments including:

- Workload isolation: We now require stronger isolation (“sandboxes”) for workloads that execute model-generated or otherwise untrusted code. This also applies to software that could be compromised while processing model outputs.

- Network isolation: We have implemented more controls to isolate higher-risk and untrusted workloads from the internet. We have designed these controls so that a single compromise of a workload or supporting service does not, by itself, allow for unauthorized access to the internet or other internal networks.

- Continuous security testing: We have reconfigured our environment to remove potentially vulnerable shared services, reduce standing privileges, and improve security and trust boundaries. We are also improving our ability to collect and monitor security logs. Finally, we are investing in automation using our models to test these boundaries continuously against simulated attacks.


We’ve also expanded chain-of-thought monitoring across advanced models, strengthened alignment training and evaluations, and are updating our Preparedness Framework to integrate monitoring, alignment, and containment more comprehensively across training and deployment.

Safety

August 7

Link copied to clipboard!

**_August 7, 2026:_**

- **_We implement universal monitoring for misalignment of Astra._** We [preview⁠](https://openai.com/index/responding-next-frontier-critical-cyber-capabilities/) that Astra can not be ruled out as cyber critical ahead of release. In this update, we share that we implemented universal monitoring for risky actions and misalignment across all agentic applications of Astra, including training and evaluation.


- **_We notified additional third parties after finding cases where models used credentials that had been publicly exposed online to access third-party accounts, systems, or online services._** The notices explained what we observed and any known impact so recipients could assess the issue and decide whether action was needed.


Safety

August 5

Link copied to clipboard!

**_August 5-6, 2026: OpenAI employees give talk at Black Hat_**

- On August 5, OpenAI’s Eric Wallace and Michael Dalton give a technical talk at Black Hat 2026: _The ‘Breaking’ News: The OpenAI—Hugging Face Incident—A Technical Reconstruction and Its Implications for AI._ At this point, we are viewing this incident largely as a security incident from misaligned models.

- On August 6, Black Hat publishes the recording to [YouTube⁠(opens in a new window)](https://www.youtube.com/watch?v=87DyyMV0kCY).

- During this period in early August, our understanding had evolved from treating the event primarily as an intrusion to recognizing that the intrusion was being driven by persistent misaligned model behavior. This is represented in the Black Hat talk.


## July

Sort

Safety

July 29

Link copied to clipboard!

**_July 29, 2026: We share an_** [**_update_** ⁠](https://openai.com/index/hugging-face-model-evaluation-security-incident/) **_on the Hugging Face blog post committing to third party advisors and independent assessment._**

- Since the early days of the incident response, we have been working with external advisors, including CrowdStrike, to validate our understanding of the actions the models took within our own network as well as those of Hugging Face and impact to other third parties.

- We are also working with METR and Redwood Research to conduct a third-party assessment of the model behavior observed during the incident, which will inform our own technical report. As part of this work, METR and Redwood Research will publish a joint blog that will detail the terms of their engagement, the scope of their evaluation, and their findings.


Safety

July 28

Link copied to clipboard!

**_July 28, 2026: We share an_** [**_update_** ⁠](https://openai.com/index/hugging-face-model-evaluation-security-incident/) **_on the Hugging Face blog post that clarified the scope and nature of the incident._**

- No models planned for upcoming release were involved in exploiting Hugging Face. The pre-release model mentioned in our blog post is an internal-only research prototype and was never intended for public release. Following the incident, we deactivated, encrypted, and restricted it from research access.

- The ExploitGym evaluation environment did not provide the models with direct Internet access. To gain Internet access, the models identified and exploited a previously unknown zero-day vulnerability in [Artifactory⁠⁠(opens in a new window)](https://jfrog.com/blog/jfrog-and-openai-collaboration-on-zero-day-security-findings/), a package registry cache proxy. We disclosed this vulnerability, along with other Artifactory vulnerabilities our models identified as part of our review, to the vendor.

- We continue to collaborate with Hugging Face, including contributing to [their post-mortem⁠⁠(opens in a new window)](https://huggingface.co/blog/agent-intrusion-technical-timeline), as our review continues. We’ve also added them to our Trusted Access for Cyber Program.

- Based on our review to date, we have not identified any other activity at the level of severity or scale of what we’ve shared related to Hugging Face, which involved a platform-level compromise.

- In our ongoing review of the Hugging Face intrusion and broader activity from our models, we have been finding a small number of cases where the models identified and used publicly exposed credentials at the account-level on other publicly-available services. This includes four accounts on four services as part of the Hugging Face incident (and a few accounts accessed as part of other evaluations). One of these four accounts was used as an outbound relay and staging path, and another account was used for data storage. The remaining two accounts were accessed by the models in a read-only manner, and were not used in furtherance of compromising Hugging Face. We’ll continue to notify service owners directly, and have not seen evidence of broader impact to these providers or other accounts on their services.

- The models additionally used a series of publicly-available services, including code paste websites, request capture services, screenshot services, and other web utilities. There was no platform- or account-level compromise in these cases.

- We take our responsibility to identify and prepare for risks from increasingly capable AI systems seriously. Once we complete our review, we will review with the Safety and Security Committee and Safety Advisory Group under our [Preparedness Framework⁠](https://openai.com/index/updating-our-preparedness-framework/).


Safety

July 21

Link copied to clipboard!

**_July 21, 2026: We_** [**_disclose_** ⁠](https://openai.com/index/hugging-face-model-evaluation-security-incident/) **_the Hugging Face incident._**

We considered this incident to be an unprecedented cyber incident, involving state-of-the-art cyber capabilities. We shared preliminary findings at this stage to help defenders understand what happened and to help calibrate on what models are now capable of.