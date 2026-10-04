[Skip to main content](https://www.microsoft.com/en-us/security/blog/2026/08/04/chaindrop-supply-chain-compromise-anatomy-self-propagating-worm/#wp--skip-link--target)

Discover what’s coming to Microsoft Ignite, Nov 17-20, 2026. [Register now.](https://ignite.microsoft.com/home?wt.mc_ID=msignite26_ciarmar_corp_np_oo_Security_BlogBnrSecurity_0428)

![](https://www.microsoft.com/en-us/security/blog/wp-content/themes/security-blog-2025/dist/images/single-bg.jpg)

![](https://www.microsoft.com/en-us/security/blog/wp-content/themes/security-blog-2025/dist/images/single-bg-dark.jpg)

* * *

## Share

- [Link copied to clipboard!](https://www.microsoft.com/en-us/security/blog/2026/08/04/chaindrop-supply-chain-compromise-anatomy-self-propagating-worm/)
- [Share on Facebook](https://www.facebook.com/sharer/sharer.php?u=https://www.microsoft.com/en-us/security/blog/2026/08/04/chaindrop-supply-chain-compromise-anatomy-self-propagating-worm/)
- [Share on X](https://twitter.com/intent/tweet?url=https://www.microsoft.com/en-us/security/blog/2026/08/04/chaindrop-supply-chain-compromise-anatomy-self-propagating-worm/&text=ChainDrop+supply+chain+compromise%3A+Anatomy+of+a+self-propagating+worm)
- [Share on LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://www.microsoft.com/en-us/security/blog/2026/08/04/chaindrop-supply-chain-compromise-anatomy-self-propagating-worm/)

## Tags

- [npm](https://www.microsoft.com/en-us/security/blog/tag/npm/)
- [Supply chain attack](https://www.microsoft.com/en-us/security/blog/tag/supply-chain-attack/)

## Content types

- [Research](https://www.microsoft.com/en-us/security/blog/content-type/research/)

## Products and services

- [Microsoft Defender](https://www.microsoft.com/en-us/security/blog/product/microsoft-defender/)

## Topics

- [Actionable threat insights](https://www.microsoft.com/en-us/security/blog/topic/actionable-threat-insights/)
- [Threat intelligence](https://www.microsoft.com/en-us/security/blog/topic/threat-intelligence/)

Show more

Microsoft Threat Intelligence identified a large-scale npm supply chain attack affecting more than 400 packages across multiple unrelated publishers, including packages associated with major enterprise software ecosystems such as keyv, flat-cache, cache-manager, and others. The malicious releases contain a Mini Shai-Hulud variant, a self-propagating credential-stealing worm delivered through a large, heavily obfuscated Bun-based JavaScript payload. The malware typically executes automatically through an npm preinstall lifecycle hook before package installation completes.

Once executed, the malware searches developer workstations and continuous integration and continuous delivery (CI/CD) environments for npm, GitHub, cloud, and infrastructure credentials. It uses recovered identities to authenticate to npm, GitHub, Amazon Web Services (AWS), Kubernetes, and HashiCorp Vault, enabling it to enumerate packages, repositories, workflow secrets, cloud parameters, and secret-store values. Collected data is encrypted and transmitted through an attacker-controlled HTTPS endpoint, with GitHub repositories serving as a fallback exfiltration channel.

The payload’s most significant capability is automated propagation. After obtaining an npm publishing token, it enumerates packages available to the compromised identity, downloads their latest tarballs, inserts the malware and setup loader, adds a preinstall hook, increments the patch version, and republishes the modified packages. The malware can also use stolen GitHub credentials to inject Claude and Visual Studio Code configuration files into repositories, establishing persistence and creating an additional developer-to-developer infection path.

In this blog, we’re sharing our analysis of this supply chain attack, along with protection, detection, amd hunting guidance. Organizations that installed an affected package with lifecycle scripts enabled should treat the associated developer workstation or build runner as potentially compromised. Investigations should prioritize credentials accessible to the affected identity, unauthorized npm releases, unexpected repository or workflow modifications, suspicious cloud and secret-store access, and artifacts produced by affected build systems. Organizations should revoke and rotate exposed credentials from a known-clean environment and rebuild affected systems and downstream artifacts from trusted sources.

## Attack chain overview

The campaign appeared as a rapid sequence of unauthorized patch releases across more than 400 npm packages maintained by otherwise unrelated publishers. Many malicious versions had no corresponding source-code commit, pull request, tag, or legitimate release, indicating that the attackers modified and published package tarballs directly rather than compromising each public source repository.

Affected releases typically added a preinstall lifecycle script that launched a malicious file, setup.mjs, contained within the package, which launched the large, obfuscated Bun JavaScript bundle included in the package. Because npm runs preinstall scripts before installation completes, the payload could execute on developer workstations and build runners before application tests or conventional security checks began.

After execution, the malware performs the following actions:

1. Determines whether it is running on a developer workstation or in a CI/CD environment. On workstations, it detaches itself to continue after installation; on CI/CD systems, it remains in the active job to access workflow secrets, runner credentials, and OpenID Connect (OIDC) publishing permissions. Both paths could support further package or repository propagation when suitable credentials are found.
2. Collects credentials from local files, environment variables, command-line tools, and GitHub Actions runner memory.
3. Authenticates to npm, GitHub, AWS, Kubernetes, and HashiCorp Vault to enumerate additional accessible resources and secrets.
4. Encrypts and exfiltrates collected data through an HTTPS channel, using GitHub repositories as a fallback.
5. Uses recovered npm publishing access to modify and republish additional packages.
6. Uses GitHub credentials to inject files into Claude and Visual Studio Code configurations across repository branches for persistence.

The payload’s  package-propagation routine downloads each publisher’s latest release, inserts itself, increments the patch version, and publishes the resulting archive. This mechanism can rapidly transform one compromised npm identity into many malicious package releases.

![](https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2026/08/image.webp)Figure 1. Attack chain.

**0\. Initial publisher access**

Evidence points towards stolen maintainer credentials as the attack vector for initial compromise. Later propagation used stolen npm publishing tokens and, in targeted workflows, GitHub Actions OIDC publishing access.

**1\. Payload startup and background execution**

The malicious npm package uses a lifecycle hook to launch its bundle.

During preflight, the payload checks the environment, exits on Russian-language systems, avoids duplicate instances, and starts a detached copy in the background on developer systems.

![](https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2026/08/image-1.webp)Figure 2. Platform identification and execution.

In CI environments, the payload remains attached so it can access credentials available to the active build job.

**2\. Initial credential discovery**

The payload first collects information that is immediately available from the local system, shell, and GitHub Actions runner.

![](https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2026/08/image-2.webp)Figure 3. Credential discovery.

The shell collector attempts to obtain the GitHub CLI token and captures the values of all process environment variables. The filesystem collector searches credential files, shell histories, cloud configuration, Secure Shell (SSH) keys, and other sensitive locations.

**3\. Cloud and secret store enumeration**

The recovered code then creates dedicated collectors for cloud and infrastructure services.

![](https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2026/08/image-3.webp)Figure 4. Credential enumeration.

These modules do not merely scan files for token patterns; they use available credentials to call service APIs, verify access, and retrieve additional secrets permitted to those identities.

The following snippet shows the authentication attempt made using the found credentials:

![](https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2026/08/image-4.webp)Figure 5. Credential validation.

**4** **. GitHub credential theft and** **enumeration**

Discovered GitHub tokens are validated before being used for additional collection or repository access.

![](https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2026/08/image-5.webp)Figure 6. GitHub credential collector.

The payload checks token scopes, enumerates writable repositories, and identifies repositories where workflow execution could expose additional secrets.

**6** **. GitHub Actions OIDC abuse**

The payload also contains a targeted publishing path for GitHub Actions workflows configured as npm trusted publishers.

![](https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2026/08/image-6.webp)Figure 7. Re-publishing package using GitHub OIDC token.

Packages published through this route can carry valid provenance because the publication originates from a legitimate workflow identity.

**7\. Exfiltration and fallback**

Collected results are serialized as JSON, gzip-compressed, and encrypted with a randomly generated AES-256-GCM using a randomly generated 32-byte key and 12-byte initialization vector (IV). The AES key is then encrypted with the attacker’s RSA public key using RSA-OAEP-SHA256.

The payload first attempts delivery through an attacker-controlled dynamic HTTPS endpoint. The active domain can change through on-chain contract (0xE1f2395ee43e45A1556EC6438a88c31B83493103, selector 0x53ed5143) or, as a fallback, from a cryptographically verified signed GitHub commit (Signed fallback marker: thebeautifulmarchoftime). If that channel is unavailable, it creates a public GitHub repository with the description _Shai-Hulud: Here We Go Again_.

Encrypted results are committed as files such as: _results-<timestamp>-<counter>.json_.

At the time of analysis, the live contract returns _npm-cache\[.\]com_. Earlier candidates include _pypi-get\[.\]com_ and _js-mirror\[.\]com_.

![](https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2026/08/image-7.webp)Figure 8. Exfiltrating stolen information.

In one fallback path, a stolen GitHub token is added separately using double Base64 encoding. This token field is encoded, not encrypted.

**8\. Repository persistence and secondary spread**

The payload can use stolen GitHub credentials to inject the malware and supporting setup files into eligible repository branches. The recovered code targets Claude and Visual Studio Code configuration paths, including . _claude/settings.json_, _.claude/setup.mjs_, _.vscode/tasks.json_, and _.vscode/setup.mjs_.

These changes create a secondary infection route: future Claude or Visual Studio Code activity can restart the payload even after the original npm installation has completed. In a conditional GitHub fallback path, the payload also attempts to install a token-monitor component that maintains credential access and contains a destructive handler if the monitored token is revoked.

![](https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2026/08/image-8.webp)Figure 9. Injecting the malicious code into development ecosystems.

**9\. Worm behavior: Package modification and publication**

The npm tokens found in collected data are checked for package-write permission and two-factor authentication (2FA)-bypass capability.

![](https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2026/08/image-9.webp)Figure 10. Republishing the package using stolen NPM token.![](https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2026/08/image-10.webp)Figure 11. Malicious update to existing package and republishing.

The propagation routine downloads a package’s latest tarball, copies the current malware bundle into it, adds a loader, and replaces its lifecycle scripts. This creates the worm-like propagation pattern: one stolen token can produce malicious patch releases across every package available to that publisher. This also explains why malicious releases frequently appeared as an otherwise ordinary patch-version increment without corresponding source commits or pull requests.

## Mitigation and protection guidance

Microsoft recommends the following mitigations to reduce the impact of this threat.

- Update npm CLI to [npm CLI v 12](https://github.blog/changelog/2026-06-09-upcoming-breaking-changes-for-npm-v12/) and use the npm CLI [min-release-age](https://docs.npmjs.com/cli/v11/using-npm/config) feature.
- Review dependency trees, lockfiles, artifact repositories, and CI caches for the five compromised versions, including transitive references.
- Pin known-good package versions.
- Purge npm and yarn caches on affected developer endpoints and build hosts, especially if the compromised tarballs were written into shared CI caches.
- Rotate credentials and secrets from a clean host if a build system or workstation imported a compromised version, because second-stage execution can expose tokens and compromise build integrity.
- Ensure that Microsoft Defender Antivirus cloud-delivered protection, Microsoft Defender for Endpoint telemetry, Microsoft Defender for Containers, and Microsoft Defender XDR investigation workflows are enabled across developer and CI assets.
- Organizations that produce software artifacts should also review their own release hardening because this incident appears consistent with CI/CD pipeline abuse through GitHub Actions OIDC publishing. Defenders should review token scopes, workflow approvals, protected environments, release provenance, and anomaly detection around automated package publication. Supply chain response cannot stop at host triage; it must also include verification that the release process itself has not been subverted.
- After remediation, validate recovery deliberately. Rebuild affected projects from a known-good dependency baseline, confirm that compromised hashes are absent from package caches and artifact stores, and review endpoint telemetry for any lingering NodeJS directory artifacts such as _Math\_Symbol.js_, _Math\_init.js_,  or names similar to _math\_<guid>.js_, or suspicious node child processes. For development organizations that share base images or golden build runners, rebuild those images as well so future jobs do not silently inherit poisoned caches or post-compromise persistence.

## Indicators of compromise (IOC)

|     |     |
| --- | --- |
| **Indicator** | **Description** |
| 54dc7ea54a1317cca0e890a2770630cf7fa6c97813e0cb9d2caa93012b350668 | _setup.mjs_ (npm tarball preinstall loader) |
| fd3ca4007b225fdf8de7af4345a19179d5efa8c4bb9205f88cda806e5684b1eb | _setup.mjs_ ( _.claude_ and _.vscode_ repository loader) |
| 9fc2570b7cef51c1b8df116d144d11ff4096357be7d2c4c6367cfc2509cf1bcc | _Math\_\*.js_ |
| _npm-cache\[.\]com_ | C2 domain |
| _pypi-get\[.\]com_ | C2 domain |
| _js-mirror\[.\]com_ | C2 domain |
| _hxxps\[:\]//npm-cache\[.\]com:443/router_ | C2 URL |

## Microsoft Defender XDR detections

Microsoft Defender XDR customers can refer to the list of applicable detections below. Microsoft Defender XDR coordinates detection, prevention, investigation, and response across endpoints, identities, email, and apps to provide integrated protection against attacks like the threat discussed in this blog.

|     |     |     |
| --- | --- | --- |
| **Tactic** | **Observed activity** | **Microsoft Defender coverage** |
| **Initial access / Execution** | Malicious files embedded in compromised npm packages execute the embedded payload automatically through a malicious preinstall lifecycle hook. | **Microsoft Defender Antivirus**<br>– Trojan:NPM/ShaiLoader.BY <br>– Trojan:NPM/MalBun.A <br>– Trojan:NPM/ShaiWorm.DAY!MTB<br>**Microsoft Defender for Endpoint**<br>– Suspicious Node.js process behavior <br>– Suspicious Node.js script execution |
| **Execution / Defense evasion** | The preinstall loader launches a heavily obfuscated Bun-based JavaScript payload designed to hinder analysis and evade Node.js-focused monitoring. | **Microsoft Defender Antivirus**<br>– Behavior:Linux/SuspBunActivity.A <br>– Behavior:Win32/SuspBunActivity.A<br>**Microsoft Defender for Endpoint**<br>– Suspicious usage of Bun runtime<br>– Suspicious installation of Bun runtime<br>– Suspicious Node.js process behavior<br>– Suspicious script execution via Bun <br>– Suspicious Node.js script execution <br>**Microsoft Defender for Cloud**<br>– Suspicious npm supply-chain compromise activity detected |
| **Credential access / Collection** | The malware searches developer workstations and CI/CD environments for npm, GitHub, cloud, Kubernetes, and secrets. | **Microsoft Defender for Endpoint**<br> – Credential access attempt <br>– Suspicious cloud credential access <br>– Enumeration of files with sensitive data <br>– Suspicious access of sensitive files   <br>**Microsoft Defender for Cloud**<br>– Sha1-Hulud Campaign Detected: Possible command injection to exfiltrate credentials |

## Advanced hunting queries

Microsoft Defender XDR customers can run the following [advanced hunting](https://learn.microsoft.com/defender-xdr/advanced-hunting-overview) queries to find related activity in their networks:

**Execution of the preinstall script**

|     |
| --- |
| `DeviceProcessEvents`<br>```| where Timestamp > ago(3d)`<br>```| where FileName in~ ("node", "node.exe")`<br>```| where ProcessCommandLine in~ ("node setup.mjs", "node  setup.mjs")`<br>`CloudProcessEvents`<br>```| where Timestamp > ago(3d)`<br>```| where FileName in~ ("node", "node.exe")`<br>```| where ProcessCommandLine in~ ("node setup.mjs", "node  setup.mjs")` |

**Execution of second-stage JavaScript using Bun runtime**

|     |
| --- |
| `DeviceProcessEvents`<br>```| where Timestamp > ago(3d)`<br>```| where InitiatingProcessFileName in~ ("node", "node.exe")`<br>```| where InitiatingProcessCommandLine in~ ("node setup.mjs", "node  setup.mjs")`<br>```| where FileName in~ ("bun", "bun.exe")`<br>```| where FolderPath contains "bun-dl-" or ProcessCommandLine has "node_modules"` |

**Malicious JavaScript from malicious packages**

|     |
| --- |
| `DeviceFileEvents`<br>`| where Timestamp > ago(3d)`<br>`| where SHA256 in~ ("9fc2570b7cef51c1b8df116d144d11ff4096357be7d2c4c6367cfc2509cf1bcc", "fd3ca4007b225fdf8de7af4345a19179d5efa8c4bb9205f88cda806e5684b1eb", "54dc7ea54a1317cca0e890a2770630cf7fa6c97813e0cb9d2caa93012b350668")` |

**Credential access by malicious JavaScript**

|     |
| --- |
| `DeviceProcessEvents`<br>```| where Timestamp > ago(3d)`<br>```| where ProcessCommandLine has_any ('gh auth token', 'gcloud config config-helper', 'az account get-access-token', "azd auth token")`<br>```| where InitiatingProcessFileName in~ ("bun", "bun.exe")`<br>```| where InitiatingProcessFolderPath contains "bun-dl-" or InitiatingProcessCommandLine has "node_modules"` |

### Microsoft Security Copilot

Security Copilot customers can use the standalone experience to create their own prompts or run prebuilt promptbooks to automate investigation and response tasks related to this threat. Useful promptbooks for this activity include Incident investigation, Microsoft User analysis, Threat actor profile, Threat Intelligence 360 report based on MDTI intelligence, and Vulnerability impact assessment. Some promptbooks require access to Microsoft Defender XDR, Microsoft Sentinel, or related Microsoft security plugins.

For this campaign, Security Copilot can help analysts summarize affected devices, pivot from the package hashes to endpoint evidence, identify hosts that communicated with the IPFS path or C2 infrastructure, and build remediation actions such as cache purge, credential rotation, and containment sequencing for impacted developer systems and build runners.

### Threat intelligence reports

Microsoft customers can use Microsoft Defender XDR Threat analytics and related Microsoft threat intelligence reporting to stay current on the malicious activity, indicators, detection coverage, and recommended response actions associated with this compromise. These reports provide investigation context, protection guidance, and updated intelligence that security teams can use to prevent, mitigate, or respond to related activity in customer environments.

As with other active supply-chain investigations, defenders should monitor for updated intelligence on package status, additional affected versions, infrastructure changes, and newly surfaced post-compromise tradecraft. Microsoft will continue to incorporate validated indicators and detections into Microsoft security products as the investigation evolves.

## Learn more

For the latest security research from the Microsoft Threat Intelligence community, check out the [Microsoft Threat Intelligence Blog](https://aka.ms/threatintelblog).

To get notified about new publications and to join discussions on social media, follow us on [LinkedIn](https://www.linkedin.com/showcase/microsoft-threat-intelligence), [X (formerly Twitter)](https://x.com/MsftSecIntel), and [Bluesky](https://bsky.app/profile/threatintel.microsoft.com).

To hear stories and insights from the Microsoft Threat Intelligence community about the ever-evolving threat landscape, listen to the [Microsoft Threat Intelligence podcast](https://thecyberwire.com/podcasts/microsoft-threat-intelligence).

Review our documentation to learn more about our real-time protection capabilities and see how to enable them within your organization.

- Learn more about [securing Copilot Studio agents with Microsoft Defender](https://learn.microsoft.com/en-us/defender-cloud-apps/ai-agent-protection)
- Evaluate your AI readiness with our latest [Zero Trust for AI workshop](https://microsoft.github.io/zerotrustassessment/).
- [Microsoft 365 Copilot AI security documentation](https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-ai-security)
- [How Microsoft discovers and mitigates evolving attacks against AI guardrails](https://www.microsoft.com/en-us/security/blog/2024/04/11/how-microsoft-discovers-and-mitigates-evolving-attacks-against-ai-guardrails/)

## Related posts

- ![Detection hunting target](https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2026/08/MS_Actional-Insights_Detection-hunting_social.webp)










September 30
20 min read



### [Unauthenticated command injection on internet-facing mail servers: tracking CVE-2026-73570](https://www.microsoft.com/en-us/security/blog/2026/09/30/unauthenticated-command-injection-on-internet-facing-mail-servers-tracking-cve-2026-73570/)




Microsoft Threat Intelligence examines CVE-2026-73570 exploitation in Zimbra, including observed attack paths, detection opportunities, and mitigation guidance.

- ![Supply chain attacks](https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2026/05/MS_Actional-Insights_Links.jpg)










September 29
14 min read



### [Phishing Abuses RMM Tools for Persistent Access](https://www.microsoft.com/en-us/security/blog/2026/09/29/phishing-abuses-rmm-tools-persistent-access/)




Microsoft observed phishing campaigns that abused MSP360 RMM to deploy ScreenConnect, creating redundant remote-access channels for follow-on activity

- ![A woman and man reviewing code on various monitors while pointing at the closest screen](https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2026/09/Star-Blizzard-RedFlick-featued-image.webp)










September 29
20 min read



### [Star Blizzard refines phishing and malware delivery with the RedFlick technique](https://www.microsoft.com/en-us/security/blog/2026/09/29/star-blizzard-refines-phishing-and-malware-delivery-with-the-redflick-technique/)




Since January 2026, Microsoft has observed Russian state threat actor Star Blizzard evolve their detection evasion capabilities through large-scale phishing campaigns, the use of accounts on compromised websites, and a novel malware delivery technique, tracked by Microsoft as “RedFlick”.


![](https://www.microsoft.com/en-us/security/blog/wp-content/themes/security-blog-2025/dist/images/bg-footer.png)

![](https://www.microsoft.com/en-us/security/blog/wp-content/themes/security-blog-2025/dist/images/bg-footer.png)

## Get started with Microsoft Security

Protect your people, data, and infrastructure with AI-powered, end-to-end security from Microsoft.

[Learn how](https://www.microsoft.com/en-us/security?wt.mc_id=AID730391_QSG_BLOG_319247&ocid=AID730391_QSG_BLOG_319247)

![](https://www.microsoft.com/en-us/security/blog/wp-content/themes/security-blog-2025/dist/images/footer-promotional.jpg)

Connect with us on social

- [X](https://twitter.com/msftsecurity)
- [YouTube](https://www.youtube.com/channel/UC4s3tv0Qq_OSUBfR735Jc6A)
- [LinkedIn](https://www.linkedin.com/showcase/microsoft-security/)