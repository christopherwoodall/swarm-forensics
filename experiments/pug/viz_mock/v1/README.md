# swarm-forensics / viz

`pipeline-mock-v1.html` — single-file interactive 3D mock (Three.js via CDN) of the
stratified origin → egress → shared artifact → target pipeline.

Open in a browser (needs internet for the Three.js CDN). Representative mock data,
not real telemetry. Edge/timeline tables at the top of the `<script type="module">`
block are the swap-in point for real data.

`pipeline-mock-v2.html` — v2 adds: idle nodes gray out as days change (selected node
stays lit), playback camera auto-follows the tiers each day's events touch, and
Reset restores everything to a fresh day-1 state.
