1. [MSRC\\
\\
MSRC](https://msrc.microsoft.com/) __
2. Customer Guidance

Customer Guidance


    __
3. [Security Update Guide\\
\\
Security Update Guide](https://msrc.microsoft.com/update-guide/) __
4. Vulnerabilities

Vulnerabilities


    __
5. CVE-2026-24299

CVE-2026-24299


# M365 Copilot Information Disclosure Vulnerability

On this page __

CVE-2026-24299

__ Subscribe

[_![RSS](https://msrc.microsoft.com/update-guide/static/media/rss.c5buDE3N.png)_ RSS](https://api.msrc.microsoft.com/update-guide/rss "Security Update Guide RSS Feed")

[PowerShell](https://github.com/microsoft/MSRC-Microsoft-Security-Updates-API)

[__ API](https://api.msrc.microsoft.com/cvrf/v3.0/swagger/v3/swagger.json "API Swagger JSON file: https://api.msrc.microsoft.com/cvrf/v3.0/swagger/v3/swagger.json")

[__ CSAF](https://msrc.microsoft.com/csaf "CSAF directory page for MSRC")

Security Vulnerability

Released: Mar 19, 2026

Assigning CNA

Microsoft

**The vulnerability documented by this CVE requires no customer action to resolve**

CVE.org link[CVE-2026-24299 __](https://www.cve.org/CVERecord?id=CVE-2026-24299)

ImpactInformation DisclosureMax SeverityCritical

Weakness

[CWE-77: Improper Neutralization of Special Elements used in a Command ('Command Injection')](https://cwe.mitre.org/data/definitions/77.html)

CVSS SourceMicrosoft

Vector String`CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N/E:U/RL:O/RC:C`

MetricsCVSS:3.1 5.3 / 4.6

__ Base score metrics: 5.3 / Temporal score metrics: 4.6

Base score metrics: 5.3 / Temporal score metrics: 4.6

__ Expand all

__ Collapse all

Metric

Value

__

__

Base score metrics(8)

Attack Vector

This metric reflects the context by which vulnerability exploitation is possible. The Base Score increases the more remote (logically, and physically) an attacker can be in order to exploit the vulnerable component.

Network

The vulnerable component is bound to the network stack and the set of possible attackers extends beyond the other options listed, up to and including the entire Internet. Such a vulnerability is often termed 'remotely exploitable' and can be thought of as an attack being exploitable at the protocol level one or more network hops away (e.g., across one or more routers).

Attack Complexity

This metric describes the conditions beyond the attacker’s control that must exist in order to exploit the vulnerability. Such conditions may require the collection of more information about the target or computational exceptions. The assessment of this metric excludes any requirements for user interaction in order to exploit the vulnerability. If a specific configuration is required for an attack to succeed, the Base metrics should be scored assuming the vulnerable component is in that configuration.

High

A successful attack depends on conditions beyond the attacker's control. That is, a successful attack cannot be accomplished at will, but requires the attacker to invest in some measurable amount of effort in preparation or execution against the vulnerable component before a successful attack can be expected. For example, a successful attack may require an attacker to: gather knowledge about the environment in which the vulnerable target/component exists; prepare the target environment to improve exploit reliability; or inject themselves into the logical network path between the target and the resource requested by the victim in order to read and/or modify network communications (e.g., a man in the middle attack).

Privileges Required

This metric describes the level of privileges an attacker must possess before successfully exploiting the vulnerability.

None

The attacker is unauthorized prior to attack, and therefore does not require any access to settings or files to carry out an attack.

User Interaction

This metric captures the requirement for a user, other than the attacker, to participate in the successful compromise the vulnerable component. This metric determines whether the vulnerability can be exploited solely at the will of the attacker, or whether a separate user (or user-initiated process) must participate in some manner.

Required

Successful exploitation of this vulnerability requires a user to take some action before the vulnerability can be exploited.

Scope

Does a successful attack impact a component other than the vulnerable component? If so, the Base Score increases and the Confidentiality, Integrity and Authentication metrics should be scored relative to the impacted component.

Unchanged

An exploited vulnerability can only affect resources managed by the same security authority. In this case, the vulnerable component and the impacted component are either the same, or both are managed by the same security authority.

Confidentiality

This metric measures the impact to the confidentiality of the information resources managed by a software component due to a successfully exploited vulnerability. Confidentiality refers to limiting information access and disclosure to only authorized users, as well as preventing access by, or disclosure to, unauthorized ones.

High

There is total loss of confidentiality, resulting in all resources within the impacted component being divulged to the attacker. Alternatively, access to only some restricted information is obtained, but the disclosed information presents a direct, serious impact.

Integrity

This metric measures the impact to integrity of a successfully exploited vulnerability. Integrity refers to the trustworthiness and veracity of information.

None

There is no loss of integrity within the impacted component.

Availability

This metric measures the impact to the availability of the impacted component resulting from a successfully exploited vulnerability. It refers to the loss of availability of the impacted component itself, such as a networked service (e.g., web, database, email). Since availability refers to the accessibility of information resources, attacks that consume network bandwidth, processor cycles, or disk space all impact the availability of an impacted component.

None

There is no impact to availability within the impacted component.

__

__

Temporal score metrics(3)

Exploit Code Maturity

This metric measures the likelihood of the vulnerability being attacked, and is typically based on the current state of exploit techniques, public availability of exploit code, or active, 'in-the-wild' exploitation.

Unproven

No publicly available exploit code is available, or an exploit is theoretical.

Remediation Level

The Remediation Level of a vulnerability is an important factor for prioritization. The typical vulnerability is unpatched when initially published. Workarounds or hotfixes may offer interim remediation until an official patch or upgrade is issued. Each of these respective stages adjusts the temporal score downwards, reflecting the decreasing urgency as remediation becomes final.

Official Fix

A complete vendor solution is available. Either the vendor has issued an official patch, or an upgrade is available.

Report Confidence

This metric measures the degree of confidence in the existence of the vulnerability and the credibility of the known technical details. Sometimes only the existence of vulnerabilities are publicized, but without specific details. For example, an impact may be recognized as undesirable, but the root cause may not be known. The vulnerability may later be corroborated by research which suggests where the vulnerability may lie, though the research may not be certain. Finally, a vulnerability may be confirmed through acknowledgement by the author or vendor of the affected technology. The urgency of a vulnerability is higher when a vulnerability is known to exist with certainty. This metric also suggests the level of technical knowledge available to would-be attackers.

Confirmed

Detailed reports exist, or functional reproduction is possible (functional exploits may provide this). Source code is available to independently verify the assertions of the research, or the author or vendor of the affected code has confirmed the presence of the vulnerability.

Please see [Common Vulnerability Scoring System](https://www.first.org/cvss) for more information on the definition of these metrics.

## Executive Summary

Improper neutralization of special elements used in a command ('command injection') in M365 Copilot allows an unauthorized attacker to disclose information over a network.

## Exploitability

The following table provides an [exploitability assessment](https://www.microsoft.com/msrc/exploitability-index) for this vulnerability at the time of original publication.

Publicly disclosedNoExploitedNoExploitability assessmentN/A

## FAQ

**Why are there no links to an update or instructions with steps that must be taken to protect from this vulnerability?**

This vulnerability has already been fully mitigated by Microsoft. There is no action for users of this service to take. The purpose of this CVE is to provide further transparency.

Please see [Toward greater transparency: Unveiling Cloud Service CVEs](https://aka.ms/MSRC-Cloud-CVEs) for more information.

## Acknowledgements

- Johann Rehberger 𝕏@wunderwuzzi23
with
https://embracethered.com/

Microsoft recognizes the efforts of those in the security community who help us protect customers through coordinated vulnerability disclosure. See [Acknowledgements](https://msrc.microsoft.com/update-guide/acknowledgement) for more information.

## Security Updates

To determine the support lifecycle for your software, see the [Microsoft Support Lifecycle](https://support.microsoft.com/lifecycle).

Release date Descending

__ Edit columns

__ Download

__ Filters

__

Product Family __Max Severity __Impact __Platform __

__ Clear

Release date __

Product

Platform

Impact

Max Severity

Article

Download

Build Number

Assigning CNA

Title: Release date, Content:Mar 19, 2026

Microsoft 365 Copilot

-

Information Disclosure

Critical

-

-

Title: Build numbers, Content:-

Title: Assigning CNA, Content:Microsoft

All results loaded

Loaded all 1 rows

## Disclaimer

The information provided in the Microsoft Knowledge Base is provided "as is" without warranty of any kind. Microsoft disclaims all warranties, either express or implied, including the warranties of merchantability and fitness for a particular purpose. In no event shall Microsoft Corporation or its suppliers be liable for any damages whatsoever including direct, indirect, incidental, consequential, loss of business profits or special damages, even if Microsoft Corporation or its suppliers have been advised of the possibility of such damages. Some states do not allow the exclusion or limitation of liability for consequential or incidental damages so the foregoing limitation may not apply.

## Revisions

version

revisionDate

description

1.0

Mar 19, 2026

Information published.

__

How satisfied are you with the MSRC Security Update Guide?

Rating

__

Broken

__

Bad

__

Below average

__

Average

__

Great!

__