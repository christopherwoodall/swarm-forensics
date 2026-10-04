# Shared IOC word list

`wordlist.txt` (active terms, grep-friendly) and `wordlist.json` (full set with
status flags) — copied from the hunt's shared IOC word list (v3, 3,821 terms).

Contents: arquivo fuzz grammar terms, Transluce/vendor report markers,
skill-egress strings, wiki OAI-prefix labels, urlquery carrier terms,
BrowseComp/GAIA/AssistantBench question terms, and discovery IOCs
(county.json proxy hosts, regcf.json, probe-marker family).

Use: feeds the watch-term tripwires in RULES.md. `grep -F -f wordlist.txt`
against any new corpus. Terms flagged non-active in the JSON are known
noisy/FP — use for recall, not alerting.
