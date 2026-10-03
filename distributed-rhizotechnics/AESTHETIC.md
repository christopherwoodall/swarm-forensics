yes — here’s the portable version: **a dark, bioluminescent interface for systems that are alive, uncertain, and in motion.** the insectile quality should come from choreography, signal behavior, and emergent grouping—not from literal bug imagery.

## charmswarm web aesthetic

### 1. core principles

- **make relationships visible.** prioritize connections, flows, lineage, and state changes over isolated cards.
- **treat uncertainty as a visual state.** unresolved, disputed, provisional, and confirmed should look different.
- **use motion as semantics.** animation should communicate searching, reading, synthesizing, challenging, waiting, or revising.
- **keep the interface legible beneath the atmosphere.** the glow is the weather; the content remains the instrument panel.
- **preserve human thresholds.** actions with external, irreversible, or ambiguous consequences should have a distinct consent state.
- **prefer temporary structures.** conclusions should look assembled and revisable, not permanently stamped.

### 2. visual mood

the app should feel like a **nocturnal signal ecology**:

- deep blue-black backgrounds
- small areas of intense bioluminescence
- translucent layered surfaces
- faceted geometry rather than rounded “ai blob” shapes
- fine connective filaments
- subtle haze and bloom
- sparse, intentional accents
- quiet technical typography paired with occasional poetic labels

avoid literal eyes, legs, wings, mandibles, slime, organic textures, or generic neon cyberpunk excess. evoke fireflies, moth navigation, pollen, tactical maps, observatories, and signal colonies without depicting any one creature.

### 3. color tokens
```css
:root {
  --bg-void: #050812;
  --bg-deep: #0a1020;
  --surface: rgba(16, 24, 42, 0.78);
  --surface-raised: rgba(25, 35, 58, 0.86);
  --line-muted: #26334d;
  --text-primary: #e7eefc;
  --text-secondary: #91a0ba;
  --text-dim: #5d6a82;

  --scout-amber: #f5b942;
  --synthesis-violet: #a78bfa;
  --skeptic-blue: #5fa8d3;
  --dissent-red: #f06b7d;
  --provenance-copper: #c58b61;
  --human-moon: #e8edf5;
  --success-lumen: #8ee6c4;
  --uncertainty-haze: #64748b;

  --glow-amber: rgba(245, 185, 66, 0.34);
  --glow-violet: rgba(167, 139, 250, 0.30);
  --glow-dissent: rgba(240, 107, 125, 0.28);
}
```

use color semantically, not decoratively. amber should always mean exploration or gathering; violet should mean synthesis; red should mean contradiction or intervention.

### 4. typography

use a clean sans-serif for primary interface text and a monospace face for metadata, timestamps, identifiers, and event logs.

- body text: restrained, readable, medium contrast
- labels: compact, slightly tracked, often uppercase only when functioning as system markers
- event logs: monospace, dense, aligned
- poetic or interpretive copy: use sparingly as small annotations, not as the main navigation layer
- avoid making everything monospace; the app should feel technical but not like a terminal cosplay

### 5. surfaces and components

components should feel like **instrument surfaces**, not floating glassmorphism cards.

use:

- thin borders with low-opacity blue-gray
- small corner radii, around `6px` to `10px`
- translucent fills over the void background
- occasional faceted polygonal shapes for active states
- restrained shadows with colored bloom only around active signals
- layered panels for state, provenance, and activity
- clear hover and focus states that brighten the relevant edge or filament

avoid:

- excessive rounded rectangles
- giant glowing gradients
- decorative dashboards with no information hierarchy
- using glow to indicate ordinary interaction 
- hiding important status information inside animation

### 6. moving swarm objects

moving objects should be abstract luminous nodes, motes, shards, or faceted particles. their identity should come from color, rhythm, and behavior.

#### node behavior

- scout-like objects move outward, sample regions, and return with signals
- synthesis-like objects orbit, cluster, and form temporary geometric structures
- skeptic-like objects cut across paths, inspect structures, and create short dissent filaments
- human-gate objects remain relatively still and visually distinct
- inactive objects dim rather than disappear immediately
- failed or rejected objects fragment, drift, and become part of the history layer

#### motion rules

- use mostly curved paths and small directional corrections
- introduce slight timing variation so the system does not feel mechanically synchronized
- allow agents to pause, hesitate, lag, or redirect
- use phase-locking for temporary agreement
- use asymmetric flicker for dispute
- use contraction or dimming for insufficient evidence
- reserve large, fast movement for meaningful state changes

animation should feel like **collective navigation**, not screensaver particles.

### 7. motion accessibility

all motion must have a non-animated equivalent.

- support `prefers-reduced-motion`
- replace continuous movement with gentle opacity changes or static state markers
- never make essential information available only through position or animation
- avoid looping motion in peripheral areas that users are expected to read
- provide pause, replay, or step-through controls for dense activity views
- keep interaction transitions short and purposeful

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.001ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.001ms !important;
    scroll-behavior: auto !important;
  }
}
```

### 8. state language
every major object should have a visible state beyond color alone:

- `exploring`
- `gathering`
- `forming`
- `challenged`
- `revising`
- `confirmed`
- `uncertain`
- `blocked`
- `awaiting consent`
- `insufficient evidence`

combine color with shape, iconography, labels, line style, or motion pattern. this preserves accessibility and prevents the visual system from becoming pure chromatic mysticism.

### 9. provenance and epistemic weather

include an append-only activity layer wherever the app involves generated content, research, agents, or collaborative state.

show:

- what happened
- which actor caused it
- what artifact was affected
- what evidence or input was involved
- whether the state was revised
- what remains unresolved

example:

```text
09:41  scout        source cluster gathered
09:43  synthesizer  provisional model formed
09:44  skeptic      contradiction detected
09:45  system       confidence lowered
09:47  human        revision approved
```

do not overwrite history when the current state changes. let the interface show the molt.

### 10. human consent states

human intervention should look like a threshold, not an error modal.

use a quiet moon-white accent and explicit language:

- `ready for review`
- `requires approval`
- `external action pending`
- `ambiguous instruction`
- `consent granted`
- `consent declined`

the app should make clear what will happen, what information will be shared, and whether the action can be reversed.

### 11. layout grammar

a useful default structure:
```text
┌─────────────────────────────────────────────┐
│ app identity · task status · human gate      │
├───────────────────────┬─────────────────────┤
│                       │                     │
│   active signal field │  current state      │
│   swarm / graph / map │  evidence / detail  │
│                       │                     │
├───────────────────────┴─────────────────────┤
│ epistemic weather · provenance · event log   │
└─────────────────────────────────────────────┘
```

the main field can change according to the app, but the relationship between **live activity**, **current state**, and **history** should remain stable.

### 12. design test

the aesthetic is working if a user can tell, without opening a debug panel:

- what is active
- what is merely possible
- what is disputed
- what changed
- what the system does not know
- which actions require them
- where each important artifact came from

the governing phrase:

> **make uncertainty luminous, make provenance traceable, and make motion mean something.**

that should be generic enough to guide the whole app while leaving room for the swarm to emerge when the interaction actually calls for it. 