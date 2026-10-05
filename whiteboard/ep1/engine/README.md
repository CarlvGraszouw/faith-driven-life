# Whiteboard renderer

A hand with a marker draws vector line art stroke by stroke, in time with the narration, then the
video is written to mp4 with the audio.

```
node render.js <timeline.json> <out.mp4>
node render.js test-timeline.json test.mp4                 # the 12-second test
node render.js example-timeline.json ep1-sample.mp4        # the 78-second sample, once the art SVGs exist
node render.js <timeline.json> x --stills 3.2,9.5 --stills-dir stills   # single PNG frames, no video
```

Needs: Node 18+, Google Chrome, ffmpeg (no drawtext or libass needed; all text is drawn in the browser).
Speed on this Mac: about 15-20 frames per second at 1080p (a 78-second video takes about 2.5 minutes).

## How it works

* `page/engine.js` builds one long SVG whiteboard in headless Chrome. `renderAt(t)` sets the
  exact state for time `t`, with no timers or CSS animation, so every frame is repeatable.
* Line art (changed 4 Oct): the hand traces EVERY stroked path in document order, so nothing
  appears without the marker tip on it. Paths with class `detail` are drawn 1.45x faster with
  quicker hops (0.07 s); `line` paths get a 0.15 s lift between them. With `draw` set, the pen
  speeds up to fit (1300-4000 px/s; beyond that the pauses halve and it may reach 5600 px/s).
  The log prints, per scene, the strokes, total pen length in frame px, the drawing span and
  the speed, and warns `OVER BUDGET` when the art cannot finish in its window: simplify the art.
  Paths with several sub-paths are split, so the pen lifts between them. A path's own fill
  (white fills for occlusion) appears as its stroke completes. Solid, non-white shapes without
  a stroke get a quick outline while the fill fades in behind the pen.
* Colour (changed 4 Oct): accent shapes (`class="accent"` or inside `<g id="accent">`) are
  painted by the hand after the line art: the marker scribbles across each shape and the colour
  appears under it (a mask uncovered by the scribble stroke). Tiny accent bits just fade in.
* Dashed strokes are drawn by the pen through a mask (a solid copy of the path uncovers the dashes).
* Parts (new 4 Oct): `"parts": [{"svg": "a.svg", "box": [x,y,w,h], "at": 0.2}, ...]` puts several
  drawings on one board; each starts `at` seconds after the scene's t0 and must finish before
  the next part starts (otherwise it is sped up, with a warning).
* SVGs with no strokes at all (such as the logo) are traced: the pen outlines the colour edges,
  then the original colours fade in.
* Titles: each letter is rendered with the handwriting font at 3x, then revealed through a
  mask of its own centre-line strokes (`page/trace.js`). The pen therefore really writes each
  letter, left to right.
* Hand: the marker tip is placed with `getPointAtLength` on the path being drawn, so it always
  sits on the drawing point. The forearm turns as if swinging from an elbow below the lower-right
  corner (`"follow"`: 0.5 = half the true angle). Moves between paths are eased, with a slight lift (a larger, softer
  shadow). The hand enters from the lower right and leaves when the scene is drawn. The hand is
  always crisp (no motion blur) and drawn above everything, including the captions.
* Camera: each scene gets its own area of one continuous board. Scene changes are a smooth
  pan (smootherstep, slight pull-back). Holds have a very slow push-in.
* `render.js` drives Chrome through the DevTools protocol over a pipe (no dependencies, with a
  private `--user-data-dir` that is deleted afterwards). It takes a PNG screenshot per frame,
  pipes it to ffmpeg (libx264, crf 18, yuv420p, BT.709, 30 fps), then muxes the audio segment
  [start, end] as AAC 192k with `+faststart`.

## Timeline

```jsonc
{
  "width": 1920, "height": 1080, "fps": 30,
  "audio": "episode.mp3", "start": 0, "end": 78,          // seconds in the mp3
  "board": { "color": "#fbfaf7", "vignette": 0.07 },
  "ink": "#1f1f1f",
  "hand": { "kit": "../ep1/kit/kit.svg", "symbol": "hand-marker" },
  "kits": ["../ep1/kit/kit.svg"],                         // optional; kits named in <use href> are found automatically
  "scenes": [
    { "id": "temple", "t0": 12.14, "t1": 21.78,           // scene starts when the narrator starts that part
      "svg": "../ep1/art/02-temple.svg",                  // 1600x900 viewBox; "art" also works
      "box": [96, 0, 1728, 972],                          // where the art sits in the 1920x1080 frame (default: whole frame)
      "draw": 8.0,                                        // seconds to draw (sets the pen speed)
      "camera": "pan-in",                                 // pan-in (default) | hold (same area, no pan) | zoom (follows the pen, then pulls back)
      "zoomLevel": 1.35, "dir": "right",                  // dir: right | left | down | up
      "accentFade": 1.0, "artAt": 4.0,                    // optional: accent fade seconds; start art at t0+artAt
      "text": [ { "str": "A Faith Driven Life", "font": "Caveat", "weight": 700, "size": 120,
                  "at": [960, 630], "align": "center", "draw": 1.8, "t": 0.3 } ] }
  ],
  "captions": [ { "t0": 0.29, "t1": 2.24, "text": "Welcome to A Faith Driven Life." }, "../ep1/captions.json" ],
  "safeBottom": 860,                                      // art boxes stay above this line (px); false = off; per scene too
  "options": { "penSpeed": 2200, "pathPause": 0.15, "letterPause": 0.06 }
}
```

* Relative paths resolve from the timeline file's folder.
* Items in a scene are drawn in order (the art first, then the text). Use `t` (text) or `artAt`
  (art) to start an item at a set time after `t0`. Without `draw`, the pen moves at a steady
  2200 px/s. Between paths it pauses 0.15 s to lift, glide (eased) and land; between letter
  strokes the pause is 0.06 s. A `draw` value overrides the speed, and the pauses shrink if they
  would take more than half of it. If a scene's drawing would run into the
  next scene, it is sped up and a warning is printed. The pen speed is printed for every scene:
  about 1500-3500 px/s looks calm.
* Captions: centred sentences on a soft white band, at most two lines each. Long sentences are
  split into timed parts by character count, preferring to break after punctuation.
* Fonts: Caveat and Inter are bundled in `fonts/`, so rendering works offline. Captions use
  Avenir Next. Any installed macOS font (for example "Noteworthy" or "Bradley Hand") also
  works in `font`.

## The hand

* **Kit symbol (default):** `"hand": { "kit": "../ep1/kit/kit.svg", "symbol": "hand-marker" }`.
  The tip is read from `kit/style-guide.md`, then from the symbol's `<desc>` ("Marker TIP at
  (0,0)"), then from an element with id `tip`. You can also give it directly:
  `"tip": [x, y]` in the symbol's own units. Optional settings: `"scale"` (default 1.15 for an
  1100-unit symbol) and `"angle"` (degrees).
* **PNG hand:** `"hand": { "image": "hand.png", "tip": [212, 38], "scale": 0.6, "angle": 0 }`.
  The tip is the marker tip's pixel in the PNG.
* If neither is found, a vector black marker is used (tip at the anchor, `"angle"` sets the tilt).

## Files

* `render.js`: the CLI. `lib/cdp.js`: Chrome launcher and DevTools-over-pipe client.
* `page/index.html`, `page/engine.js`: the renderer. `page/trace.js`: centre-line tracer for
  letters and logo edges.
* `test-timeline.json`, `test-assets/`: the 12-second test (placeholder kit and teacher
  scene). `test-dense-timeline.json` draws `test-assets/dense.svg` (165 paths) in 6 s. `test-assets/temple.svg` is a denser stress-test scene.
* `example-timeline.json`: the 78-second Episode 1 sample. Its scene SVGs go in `../ep1/art/`.
