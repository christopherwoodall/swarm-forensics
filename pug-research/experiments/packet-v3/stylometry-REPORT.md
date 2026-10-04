# Stylometry Report: OpenAI-side partitions

78 runs logged in `runs_log.jsonl`. Four partitions, six pairs, seven methods.
AI Village side is blocked on dataset access (see README.md).

## Headline matrix

| Pair | Jaccard@1k | cos TF-IDF | cos funcwords | Spearman | Delta | char cos |
|---|---|---|---|---|---|---|
| evals vs gems | 0.163 | 0.246 | **0.644** | 0.325 | **0.607** | **0.448** |
| evals vs traces | 0.093 | 0.108 | 0.255 | 0.197 | 0.631 | 0.212 |
| evals vs wiki | 0.124 | 0.083 | 0.268 | 0.193 | 1.790 | 0.164 |
| gems vs traces | 0.088 | 0.061 | 0.166 | 0.144 | 0.658 | 0.177 |
| gems vs wiki | 0.144 | 0.098 | 0.388 | 0.303 | 1.828 | 0.207 |
| traces vs wiki | 0.109 | 0.076 | 0.058 | **0.382** | 1.996 | 0.125 |

Bold marks the closest pair per method. Lower Delta means closer style.

## Finding 1: evals and gems share a style, not a topic

The evals partition (900 benchmark questions) and the gems partition (618
gem names plus code) are the closest pair on four of seven methods. Function
words drive the similarity (cosine 0.644). Shared bigrams are function-word
phrases ("of the", "in the", "at least"). Character 4-grams agree (0.448).

Keyness shows the topics differ completely. Eval-distinctive terms are formal
question prose ("according", "which", "states", years). Gem-distinctive terms
are Ruby code ("end", "def", "class", "thor") plus "oai".

Interpretation: benchmark questions and gem package prose share a formal
technical register. The similarity is stylistic. It is not tradecraft.

## Finding 2: the wiki is the lexical hub for tradecraft vocabulary

The relay, proxy, and archive vocabulary lives almost entirely in the wiki:

| Term | gems | traces | wiki | evals |
|---|---|---|---|---|
| relay | 0 | 0 | 13,422 | 0 |
| jina | 0 | 0 | 3,545 | 0 |
| proxy | 1 | 0 | 1,778 | 0 |
| archive | 0 | 0 | 1,332 | 7 |
| task | 27 | 0 | 26,368 | 1 |
| wayback | 0 | 0 | 113 | 0 |

The wiki is also the stylistic outlier. Burrows Delta puts it at 1.8-2.0
against every other partition. Its distinctive terms are URL-encoding
fragments ("3a", "2f", "5b" — the tokenizer strips "%") plus "https", "gov",
"county", "sec", "json", "cgi". The wiki partition IS the incident URL space.

## Finding 3: provider markers link gems, traces, and wiki — never evals

| Term | gems | traces | wiki | evals |
|---|---|---|---|---|
| oai | 814 | 89,241 | 393 | 0 |
| zz | 1 | 96,179 | 32 | 0 |

The "oai" marker appears in gem names, trace attribution, and wiki text.
It never appears in eval questions. Eval questions are task text. They do not
carry harness bookkeeping. This matches the three-level linkage model:
provider markers live in agent output, not in task prompts.

## Finding 4: shared terms rank alike between traces and wiki

Spearman rho is highest for traces vs wiki (0.382), even though Delta calls
them the farthest pair (1.996). Both facts hold. Shared terms keep similar
rank order (both are URL-heavy: "https", "gov", "api", "url" dominate both).
The full profiles diverge because each side's distinctive tail is large.
Rank order measures the shared core. Delta measures the whole profile.

## N-sensitivity

Jaccard at n=100 (core vocab): all pairs score 0.04-0.15. Cores are disjoint.
Jaccard at n=10,000 (broad vocab): evals vs gems still leads (0.141).
The partitions share the long tail of ordinary English. Their cores differ.

## Caveats

- The traces partition includes analyst attribution notes. "eval" and "agent"
  appear in 100% of sampled trace docs. This is metadata, not agent voice.
- The tokenizer strips "%", so URL-encoding appears as hex pairs ("3a").
  This inflates the wiki's distinctive-term list with encoding fragments.
- The first six Burrows Delta runs were degenerate (Delta = 2.0 for all
  pairs; two-profile z-scoring collapses). The method was fixed to z-score
  against the four-partition background and re-run at n=1000. The six
  degenerate runs remain in the log and MUST be ignored.
- The traces sample is 1-in-20 (29,498 of ~590k lines). Deterministic stride.

## Absences worth noting

- "exploit" appears zero times in all four partitions.
- "harness" appears zero times in all four partitions.
- "wget" appears zero times. "curl" appears only in the wiki (238).

## Next: the village comparison

When dataset access is granted, the interesting tests are:

1. Does village chat share the wiki's relay/proxy/archive/task vocabulary?
   Shared tradecraft words would suggest a common agent operational lexicon.
2. Do village goals read like eval questions (formal benchmark prose)?
   High evals-vs-goals similarity would support the escaped-eval framing.
3. Do village code messages share the gems' "oai"/"thor" naming habits?
4. Char 4-gram cosine is the obfuscation-robust check. Run it first.
