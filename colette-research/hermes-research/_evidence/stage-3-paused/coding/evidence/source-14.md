[Skip to content](https://github.com/anysphere/kernel-optimization-results#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/anysphere/kernel-optimization-results) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/anysphere/kernel-optimization-results) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/anysphere/kernel-optimization-results) to refresh your session.Dismiss alert

{{ message }}

[anysphere](https://github.com/anysphere)/ **[kernel-optimization-results](https://github.com/anysphere/kernel-optimization-results)** Public

- [Notifications](https://github.com/login?return_to=%2Fanysphere%2Fkernel-optimization-results) You must be signed in to change notification settings
- [Fork\\
0](https://github.com/login?return_to=%2Fanysphere%2Fkernel-optimization-results)
- [Star\\
10](https://github.com/login?return_to=%2Fanysphere%2Fkernel-optimization-results)


main

[**1** Branch](https://github.com/anysphere/kernel-optimization-results/branches) [**0** Tags](https://github.com/anysphere/kernel-optimization-results/tags)

[Go to Branches page](https://github.com/anysphere/kernel-optimization-results/branches)[Go to Tags page](https://github.com/anysphere/kernel-optimization-results/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![wilson-anysphere](https://avatars.githubusercontent.com/u/236845017?v=4&size=40)](https://github.com/wilson-anysphere)[wilson-anysphere](https://github.com/anysphere/kernel-optimization-results/commits?author=wilson-anysphere)

[Share results](https://github.com/anysphere/kernel-optimization-results/commit/87ea087db7b6765ecdd8f5ca07a9cb3eb702e4b0)

success

6 months agoApr 14, 2026

[87ea087](https://github.com/anysphere/kernel-optimization-results/commit/87ea087db7b6765ecdd8f5ca07a9cb3eb702e4b0) · 6 months agoApr 14, 2026

## History

[1 Commit](https://github.com/anysphere/kernel-optimization-results/commits/main/)

Open commit details

[View commit history for this file.](https://github.com/anysphere/kernel-optimization-results/commits/main/) 1 Commit

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [FlashInfer-Bench](https://github.com/anysphere/kernel-optimization-results/tree/main/FlashInfer-Bench "FlashInfer-Bench") | [FlashInfer-Bench](https://github.com/anysphere/kernel-optimization-results/tree/main/FlashInfer-Bench "FlashInfer-Bench") |  |  |
| [L1](https://github.com/anysphere/kernel-optimization-results/tree/main/L1 "L1") | [L1](https://github.com/anysphere/kernel-optimization-results/tree/main/L1 "L1") |  |  |
| [L2](https://github.com/anysphere/kernel-optimization-results/tree/main/L2 "L2") | [L2](https://github.com/anysphere/kernel-optimization-results/tree/main/L2 "L2") |  |  |
| [Quant](https://github.com/anysphere/kernel-optimization-results/tree/main/Quant "Quant") | [Quant](https://github.com/anysphere/kernel-optimization-results/tree/main/Quant "Quant") |  |  |
| [.gitignore](https://github.com/anysphere/kernel-optimization-results/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/anysphere/kernel-optimization-results/blob/main/.gitignore ".gitignore") |  |  |
| [README.md](https://github.com/anysphere/kernel-optimization-results/blob/main/README.md "README.md") | [README.md](https://github.com/anysphere/kernel-optimization-results/blob/main/README.md "README.md") |  |  |
| [combined\_metrics.csv](https://github.com/anysphere/kernel-optimization-results/blob/main/combined_metrics.csv "combined_metrics.csv") | [combined\_metrics.csv](https://github.com/anysphere/kernel-optimization-results/blob/main/combined_metrics.csv "combined_metrics.csv") |  |  |
| [problem\_level\_metrics.csv](https://github.com/anysphere/kernel-optimization-results/blob/main/problem_level_metrics.csv "problem_level_metrics.csv") | [problem\_level\_metrics.csv](https://github.com/anysphere/kernel-optimization-results/blob/main/problem_level_metrics.csv "problem_level_metrics.csv") |  |  |
| View all files |

## Repository files navigation

# Multi-Agent CUDA Kernel Optimizations

[Permalink: Multi-Agent CUDA Kernel Optimizations](https://github.com/anysphere/kernel-optimization-results#multi-agent-cuda-kernel-optimizations)

Solutions and metrics from Cursor's multi-agent system that autonomously optimized 235 CUDA kernels for NVIDIA Blackwell B200 GPUs, achieving a **38% geomean speedup** over baselines.

Read the full writeup: [Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)

## Repository structure

[Permalink: Repository structure](https://github.com/anysphere/kernel-optimization-results#repository-structure)

- **`L1/`** — 94 single-operator kernel problems (e.g. attention, RoPE, RMSNorm)
- **`L2/`** — 82 multi-operator fused kernel problems (e.g. full decoder layers, MoE routing)
- **`Quant/`** — 33 quantized kernel problems (FP8, NVFP4)
- **`FlashInfer-Bench/`** — 26 problems benchmarked against FlashInfer (GEMM, GQA, MoE, fused ops)
- **`combined_metrics.csv`** — Per-workload results: baseline latency, SOL latency, selected latency, and SOL score
- **`problem_level_metrics.csv`** — Per-problem aggregate results: SOL score and speedup vs. baseline

Each problem directory contains `src/` (the kernel solution), `solution.json`, and `traces.jsonl`.

## About

No description, website, or topics provided.

### Resources

[Readme](https://github.com/anysphere/kernel-optimization-results#readme-ov-file)

[Activity](https://github.com/anysphere/kernel-optimization-results/activity)

[Custom properties](https://github.com/anysphere/kernel-optimization-results/custom-properties)

### Stars

**10** stars

### Watchers

**0** watching

### Forks

[**0** forks](https://github.com/anysphere/kernel-optimization-results/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fanysphere%2Fkernel-optimization-results&report=anysphere+%28user%29)

## Releases

## Packages

## Used by

## Contributors

## Languages

You can’t perform that action at this time.