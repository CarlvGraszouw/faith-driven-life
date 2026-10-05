# Whiteboard art — style guide v2 (Episode 1)

Goal: illustrations that look like a gifted sketch artist drew them live on a whiteboard,
with the craft of a good graphic-novel inker. Every drawing must *tell the moment of the story*
being narrated, not just label it. Nothing clip-art, nothing childish, no icon people.

## File format (hard rules — the renderer depends on them)
- `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900">`, no background rect.
- Only `<path>` elements (no circle/rect/ellipse/text/use/transform). Path data uses ABSOLUTE
  commands only: `M L C Q Z` (no arcs, no lowercase). Use `lib_v2.py` helpers (circle/ellipse
  return absolute cubic paths).
- Classes:
  - `line`   — main contours (the hand traces these). stroke 2.6
  - `detail` — interior lines: faces, fingers, folds, ornament. stroke 1.5
  - `hatch`  — shading, cross-hatching, texture. stroke 0.9, opacity .75
  Put the `<style>` block from `lib_v2.py` (STYLE) at the top of every file.
- Fills: `fill="#ffffff"` only to hide what is behind (occlusion). Colour accents sparingly,
  `fill` with one of GOLD #dcb874, ORANGE #e3922f, RUST #c9652f, CLOAK #c98a6a, BLUE #9dbad0
  and `style="mix-blend-mode:multiply"` — at most 1–2 accent areas per scene (e.g. the coin, a cloak).
- DOCUMENT ORDER = DRAWING ORDER: big shapes and the focal figure first, then secondary figures,
  then details, then hatching last.
- Bottom 120 units (y > 780) stay nearly empty — captions sit there.
- Keep the areas where on-screen words are written empty (given per scene in the assignment).
  Frame→art conversion: x_art = (x_frame − 195.6) / 0.9556, y_art = y_frame / 0.9556
  (frame is 1920×1080). Leave ~70 art units of height around each word.
- Draw-time budget: total `line` length ≈ ≤ 3000 × draw-seconds (frame px); detail/hatch draw fast.
  A typical scene can have 150–400 paths; that's fine.

## Drawing craft
- Three line weights as above; contours confident and continuous; interior lines lighter.
- Shading by hatching (parallel strokes following the form), cross-hatch for deep shadow,
  a few ground shadows under feet. Leave plenty of white — hatch only where light falls away.
- People: real anatomy at ~7.5 heads tall, believable poses with weight and gesture, readable
  silhouettes. Faces in profile or three-quarter with eyes, brows, nose, mouth, beard/hair —
  expressive but dignified (no cartoon dots). Hands with fingers. Clothing with drapery folds.
- Composition: one clear focal point, rule of thirds, foreground/midground/background
  (background lighter: fewer lines, hatch only). A standing adult in a mid shot is ~300–380 units.
- Show, don't label: the scene should make sense with the sound off.

## Historical accuracy — 1st-century Judea (c. AD 30)
- Jesus: Jewish man ~30, dark shoulder-length hair, short beard; plain tunic (chiton) with a
  mantle (himation/tallit) with tassels (tzitzit) at the corners; sandals. Calm, authoritative.
  Same design in every scene: centre-parted hair, full short beard, mantle over left shoulder.
- Pharisees: older men, full beards, long robes, broad mantles with long tassels, small leather
  phylactery box on forehead/arm, head covering. Herodians: Greco-Roman style, shorter
  hair/beard, tunic with a fine cloak pinned at shoulder, rings — wealthier, courtly.
- Roman soldiers: galea helmet with cheek guards, mail shirt (lorica hamata), belt (cingulum)
  with apron straps, curved rectangular scutum, pilum or gladius, caligae.
- Temple: Herod's Temple — tall white façade with gold accents, the Royal Stoa colonnade on the
  south, Court of the Gentiles crowded with people, stone paving, steps.
- Denarius of Tiberius: obverse laureate head of Tiberius facing right, legend
  TI CAESAR DIVI AVG F AVGVSTVS around the edge; reverse a seated female figure (Livia as Pax)
  holding a long sceptre and an olive branch, legend PONTIF MAXIM. Small silver coin — when shown
  big, draw the beaded rim, worn relief, hatching for depth. Silver = no fill or BLUE wash, light.

## Helpers
`lib_v2.py` (same folder) — STYLE, circle(), ellipse(), smooth() (Catmull-Rom through points),
tx() (scale/rotate/translate an absolute path), L()/D()/H() element builders, svg(), check_paths().
Render stills to check your work: `python3 render_still.py file.svg out.png` (cairosvg).

Reference: `reference/c11-v2.png` shows the line weights — but aim much HIGHER on figure
quality than that sample (it is still too stiff and icon-like).
