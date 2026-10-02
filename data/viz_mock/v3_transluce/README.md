# pivot graph replay (Transluce us-canada-gov hunt)

Four-tier 3D graph: top layer = source tasks, then launcher indicators, pivot
relays, and government targets at the bottom. 36 nodes, 86 edges, 91 days
(2026-04-19 to 2026-07-18). One step = one day.

The counts come from another investigation (silent-locus). This page shows
them as given. It does not rebuild them from the raw archives and the data has
no event ids. Notes in the evidence panel are source text, not verified here.

## Files

- `index.html`: page and inline module JS (three.js through an import map).
- `data/graph.json`: aggregate graph data.
- `serve.py`: static server. Loopback only. Serves `.html`, `.js`, `.json` in this folder.
- `vendor/`: three.js r160 and OrbitControls. Both are local copies.

## Run it

    make pivot-check    # check the shape of data/graph.json
    make pivot-serve    # http://127.0.0.1:8001/  (PIVOT_PORT=<n> to change)

## Use it

- Play, pause, previous, next, speed, scrub, reset. Space and arrow keys work.
- The camera stays put during playback. Drag to orbit, scroll to zoom,
  right-drag to pan. VIEW resets the camera.
- The DARK and LIGHT button switches the theme. The page remembers the choice.
  Ctrl+Y hides or shows the mouse cursor.
- Click a node, or a name in the evidence panel, to see its weight, days with
  a count, source note, and connected edges.
- A bright node has a count that day. A faded node has none but stays visible,
  so every tier always shows. A line is lit when both ends are bright. That does not prove the two ends occurred together that day.
- `L:a000_zzend` has no daily counts. It follows `L:zz_label`, as the data file documents.
