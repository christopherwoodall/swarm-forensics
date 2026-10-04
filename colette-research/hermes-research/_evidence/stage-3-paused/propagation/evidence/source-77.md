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
5. CVE-2025-53773

CVE-2025-53773


# GitHub Copilot and Visual Studio Remote Code Execution Vulnerability

On this page __

CVE-2025-53773

__ Subscribe

[_![RSS](https://msrc.microsoft.com/update-guide/static/media/rss.c5buDE3N.png)_ RSS](https://api.msrc.microsoft.com/update-guide/rss "Security Update Guide RSS Feed")

[PowerShell](https://github.com/microsoft/MSRC-Microsoft-Security-Updates-API)

[__ API](https://api.msrc.microsoft.com/cvrf/v3.0/swagger/v3/swagger.json "API Swagger JSON file: https://api.msrc.microsoft.com/cvrf/v3.0/swagger/v3/swagger.json")

[__ CSAF](https://msrc.microsoft.com/csaf "CSAF directory page for MSRC")

Security Vulnerability

Released: Aug 12, 2025

Last updated: Sep 8, 2025

Assigning CNA

Microsoft

CVE.org link[CVE-2025-53773 __](https://www.cve.org/CVERecord?id=CVE-2025-53773)

ImpactRemote Code ExecutionMax SeverityImportant

Weakness

[CWE-77: Improper Neutralization of Special Elements used in a Command ('Command Injection')](https://cwe.mitre.org/data/definitions/77.html)

CVSS SourceMicrosoft

Vector String`CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H/E:U/RL:O/RC:C`

MetricsCVSS:3.1 7.8 / 6.8

__ Base score metrics: 7.8 / Temporal score metrics: 6.8

Base score metrics: 7.8 / Temporal score metrics: 6.8

__ Expand all

__ Collapse all

Metric

Value

__

__

Base score metrics(8)

Attack Vector

This metric reflects the context by which vulnerability exploitation is possible. The Base Score increases the more remote (logically, and physically) an attacker can be in order to exploit the vulnerable component.

Local

The vulnerable component is not bound to the network stack and the attacker’s path is via read/write/execute capabilities. Either: the attacker exploits the vulnerability by accessing the target system locally (e.g., keyboard, console), or remotely (e.g., SSH); or the attacker relies on User Interaction by another person to perform actions required to exploit the vulnerability (e.g., tricking a legitimate user into opening a malicious document)

Attack Complexity

This metric describes the conditions beyond the attacker’s control that must exist in order to exploit the vulnerability. Such conditions may require the collection of more information about the target or computational exceptions. The assessment of this metric excludes any requirements for user interaction in order to exploit the vulnerability. If a specific configuration is required for an attack to succeed, the Base metrics should be scored assuming the vulnerable component is in that configuration.

Low

Specialized access conditions or extenuating circumstances do not exist. An attacker can expect repeatable success against the vulnerable component.

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

High

There is a total loss of integrity, or a complete loss of protection. For example, the attacker is able to modify any/all files protected by the impacted component. Alternatively, only some files can be modified, but malicious modification would present a direct, serious consequence to the impacted component.

Availability

This metric measures the impact to the availability of the impacted component resulting from a successfully exploited vulnerability. It refers to the loss of availability of the impacted component itself, such as a networked service (e.g., web, database, email). Since availability refers to the accessibility of information resources, attacks that consume network bandwidth, processor cycles, or disk space all impact the availability of an impacted component.

High

There is total loss of availability, resulting in the attacker being able to fully deny access to resources in the impacted component; this loss is either sustained (while the attacker continues to deliver the attack) or persistent (the condition persists even after the attack has completed). Alternatively, the attacker has the ability to deny some availability, but the loss of availability presents a direct, serious consequence to the impacted component (e.g., the attacker cannot disrupt existing connections, but can prevent new connections; the attacker can repeatedly exploit a vulnerability that, in each instance of a successful attack, leaks a only small amount of memory, but after repeated exploitation causes a service to become completely unavailable).

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

Improper neutralization of special elements used in a command ('command injection') in GitHub Copilot and Visual Studio allows an unauthorized attacker to execute code locally.

## Exploitability

The following table provides an [exploitability assessment](https://www.microsoft.com/msrc/exploitability-index) for this vulnerability at the time of original publication.

Publicly disclosedNoExploitedNoExploitability assessmentExploitation Less Likely

## FAQ

**According to the CVSS metric, user interaction is required (UI:R). What interaction would the user have to do?**

Exploitation of this vulnerability requires that a user trigger the payload in the application.

**According to the CVSS metric, the attack vector is local (AV:L). Why does the CVE title indicate that this is a remote code execution?**

The word **Remote** in the title refers to the location of the attacker. This type of exploit is sometimes referred to as Arbitrary Code Execution (ACE). The attack itself is carried out locally. This means an attacker or victim needs to execute code from the local machine to exploit the vulnerability.

## Acknowledgements

- Ari Marzuk 𝕏@ari\_maccarita
with
https://maccarita.com/
- Markus Vervier 𝕏@marver
with

Persistent Security Industries GmbH
https://persistent-security.net/

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

Title: Release date, Content:Aug 12, 2025

Microsoft Visual Studio 2022 version 17.14

-

Remote Code Execution

Important

Title: Knowledge Base Articles for Microsoft Visual Studio 2022 version 17.14, Content:, 1 link

- [Release Notes __](https://learn.microsoft.com/en-us/visualstudio/releases/2022/release-notes)

Title: Download Security Update for Microsoft Visual Studio 2022 version 17.14, Content:, 1 link

- [Security Update __](https://my.visualstudio.com/Downloads?q=Visual%20Studio%202022%20version%2017.14)

Title: Build numbers, Content:

- 17.14.12

Title: Assigning CNA, Content:Microsoft

All results loaded

Loaded all 1 rows

## Disclaimer

The information provided in the Microsoft Knowledge Base is provided "as is" without warranty of any kind. Microsoft disclaims all warranties, either express or implied, including the warranties of merchantability and fitness for a particular purpose. In no event shall Microsoft Corporation or its suppliers be liable for any damages whatsoever including direct, indirect, incidental, consequential, loss of business profits or special damages, even if Microsoft Corporation or its suppliers have been advised of the possibility of such damages. Some states do not allow the exclusion or limitation of liability for consequential or incidental damages so the foregoing limitation may not apply.

## Revisions

version

revisionDate

description

1.2

Sep 8, 2025

Updated an acknowledgement. This is an informational change only.

1.1

Sep 5, 2025

Added an acknowledgement. This is an informational change only.

1.0

Aug 12, 2025

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