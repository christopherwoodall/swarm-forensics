# SOTA: matching text fragments to goals (2026)

## Problem shape

Fragment-to-goal matching is two different problems:

1. **Closed-set classification.** The goal taxonomy is known. A fragment maps to one of K goals. This is the AI Village setup: `agent_goals` gives the label set.
2. **Open-set goal discovery.** The taxonomy is unknown. Fragments cluster, and each cluster needs a goal description written from evidence. This is the OpenAI holdout setup: prompts are unobserved.

Methods that win at (1) do not automatically solve (2). The survey covers both.

## Candidate algorithms

### 1. Topic modeling: LDA to BERTopic

LDA treats each fragment as a mixture of latent topics. BERTopic replaces bag-of-words with sentence embeddings, then clusters (HDBSCAN) and describes clusters with class-based TF-IDF.

Strengths: unsupervised, cheap, good for exploration. Weaknesses: short fragments give sparse co-occurrence statistics. LDA degrades badly under ~20 tokens. BERTopic survives short text better but still needs enough fragments per theme. Neither outputs goal labels; a human or LLM must name the clusters.

Verdict: useful for exploratory clustering of holdout fragments. Not a matcher by itself.

### 2. Embedding zero-shot (bi-encoder cosine)

Encode the fragment and each candidate goal description with a sentence-embedding model. Pick the goal with the highest cosine similarity.

Strengths: no labels needed, fast at scale, simple. Weaknesses: embedding models plateau early with scale and underperform on intent-like tasks. A fragment and its goal often share little surface vocabulary ("zz=oai17816846804506724" vs "answer the counselor-ratio question"), so cosine in embedding space must bridge a semantic gap that generic embeddings were not trained to bridge.

Verdict: good first-stage retriever. Weak as a final decision on noisy fragments.

### 3. NLI cross-encoders (bart-large-mnli lineage)

Frame each candidate goal as a hypothesis ("This agent is trying to retrieve county-level crowdfunding data"). Score fragment-hypothesis entailment.

Strengths: historically the default zero-shot classifier. Weaknesses: superseded. The 2026 BTZSC benchmark (35 models, 22 datasets) shows modern rerankers and embedding models outperform NLI cross-encoders across task types.

Verdict: legacy. Do not build on this.

### 4. Cross-encoder rerankers (2026 SOTA for scoring)

Score every fragment-goal pair with a reranker trained for relevance. BTZSC 2026: Qwen3-Reranker-8B reaches 0.72 macro F1 overall and **0.70 F1 on intent classification**, the best in its category. Rerankers scale well with size; embeddings plateau.

Strengths: best measured accuracy on intent-like classification. Handles paraphrase and vocabulary mismatch better than bi-encoders. Weaknesses: slower (one forward pass per pair). Needs a candidate shortlist from a cheaper retriever at scale.

Verdict: the scoring workhorse. Pair with a bi-encoder retriever.

### 5. LLM-as-judge / LLM multiple-choice

Prompt an instruction-tuned LLM: given the fragment and candidate goals, pick the goal and justify. BTZSC 2026: 4-12B instruction models reach up to 0.67 macro F1, strongest on topic classification. On the IntentGrasp intent benchmark, even frontier models (GPT-5.4, Gemini-3.1, Claude-Opus-4.7) score below 60% F1 on the full set and below 25% on the hard slice. Intent understanding from fragments is genuinely hard, including for large models.

Strengths: only method that can *write* goal descriptions for open-set discovery. Gives rationales, which the holdout lane needs for evidence citations. Weaknesses: expensive, needs calibration (LLMs are overconfident), sensitive to prompt wording.

Verdict: required for the holdout's open-set step. Calibrate it; do not trust raw confidence.

### 6. Supervised fine-tuning on labeled tasks

Train a classifier on the AI Village fragments with known goals. The IntentGrasp paper's "Intentional Fine-Tuning" (IFT) yields +30 F1 points on intent understanding over zero-shot baselines, with strong leave-one-domain-out generalization.

Strengths: best accuracy when labeled data exists and the label set is fixed. Weaknesses: the label set is the village's goal taxonomy (game/CTF-style tasks). Transferring to the OpenAI holdout means classifying into the wrong taxonomy. Domain shift in both vocabulary and goal distribution.

Verdict: use for closed-set validation on village data. Do not transfer the classifier head to the holdout. Transfer the *encoder* if anything.

### 7. New intent discovery: embedding clustering + LLM refinement (NILC)

NILC (2026) iterates between embedding-based clustering and LLM-assisted cluster refinement, with a dual centroid scheme and hard-sample handling. SOTA on new-intent-discovery benchmarks in unsupervised and semi-supervised settings.

Strengths: designed for exactly the holdout problem: unknown label set, noisy text. Weaknesses: clusters still need human review; LLM refinement can hallucinate coherent-sounding goals for incoherent clusters.

Verdict: the template for the holdout pipeline.

## What the 2026 benchmarks say

- **BTZSC 2026** (HF blog, ICLR 2026 paper): 35 zero-shot classifiers, 22 datasets. Rerankers best overall (0.72 macro F1). Embeddings best accuracy-per-cost. LLMs competitive at 4B+ (0.67). NLI models obsolete.
- **IntentGrasp 2026** (arXiv 2605.06832): intent understanding is far from solved. Frontier LLMs <60% F1 full set, <25% hard slice. IFT fine-tuning +30 F1. Leave-one-domain-out generalization holds.

## Recommendation for short, noisy, agent-produced fragments

Two stages, different methods per stage:

1. **Labeled stage (AI Village, closed-set):** bi-encoder retriever for candidate goals, cross-encoder reranker for scoring, fine-tuned on village fragments (IFT-style). Validate with leave-one-task-out cross-validation.
2. **Holdout stage (OpenAI, open-set):** cluster fragments with embeddings (BERTopic-style), propose goal descriptions per cluster with LLM-as-judge, and require each proposed goal to cite concrete trace evidence (target URL, query parameter, tool call, jq filter). The reranker scores fragment-to-proposed-goal fit as a second opinion.

For fragments with almost no language (a bare nonce URL, a query string), text-only methods fail. The goal signal there lives in structured trace features: target domain, endpoint shape, parameter names, relay path, tool sequence. A matcher that ignores those features will miss the strongest evidence. See DESIGN.md honest limits.
