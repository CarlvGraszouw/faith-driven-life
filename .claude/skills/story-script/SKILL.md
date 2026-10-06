---
name: story-script
description: Write narration scripts for A Faith Driven Life whiteboard/YouTube episodes that read like an audiobook — a real story told aloud, in the author's voice — and that give every drawing enough narration time to finish. Use when writing, rewriting or editing any episode script, show narration, or the drawing beat sheet that goes with it.
---

# Story scripts that read like an audiobook

An episode is a story told aloud by one voice, over drawings that appear as it is told.
It is not an article read out, and not a lecture with a story pasted on top. The listener
should feel carried along, and at the end they should feel one thing deeply and know what to do.

Default AI drafting fails here in predictable ways: it summarises instead of telling,
explains instead of showing, decorates with detail that means nothing ("a coin worn smooth
by a thousand fingers"), stacks clever devices, and writes for the eye. This skill exists to
stop that. Follow the pipeline in order; do not skip to drafting.

## Pipeline

1. **Story bible** (`script/story-bible.md`) — before any prose:
   - The *one meaning*: the single truth the listener must feel at the end, in one sentence.
   - The *dramatic question* that pulls them from the first minute to the last.
   - The *spine*: the story that carries the teaching (a real scene from Scripture or history,
     or a character we follow). Teaching rides inside scenes; it never replaces them.
   - The author's voice: read the author's own book (The King's Rule, in Drive) and note how
     he speaks — sentence length, warmth, directness, favourite turns of phrase, how he
     addresses the listener. Quote 5–10 short lines that sound like him. Write in that voice.
   - Facts and scripture the story may use, each with its source.
2. **Beat sheet** (`script/beat-sheet.md`) — one row per drawing:
   `beat | what happens in the story | what the listener feels | the drawing | min seconds`.
   - Each beat must *move* the story or *deepen* the meaning. If it does neither, cut it.
   - **Timing:** a drawing needs its draw time plus about 1.5 s to breathe. At ~2.5 spoken
     words per second, a beat needs at least `(draw seconds + 1.5) × 2.5` words. When a beat is
     short, expand the *story* (let the moment play out, a line of dialogue, what is at stake),
     never pad with description.
3. **Draft** (`script/epN-script-vX.md`) — beat by beat, with `[DRAWING: …]` cues. Follow
   `references/craft.md`.
4. **Edit passes** — run as separate agents, each with only the draft and its checklist from
   `references/editors.md`: the *story editor*, the *ear editor*, the *accuracy editor* and the
   *cold listener*. The writer revises against all four. Repeat until the cold listener reports
   no place where attention drops.
5. **Hand-off** — final script with section headings and drawing cues, plus a word count and
   estimated runtime per section, and the updated beat sheet for the artists.

## Non-negotiables

- Every concrete detail must carry meaning for this story. Texture for its own sake is cut.
- Scenes, not summaries: put the listener *in* a moment, with people, stakes and a turn.
- One voice, the author's, warm and plain. No performance, no cleverness for its own sake.
- Written for the ear: it must be easy to read aloud in one take and easy to follow on one hearing.
- Scripture quoted accurately with references; history never overclaimed.

See `references/craft.md` for the rules with before/after examples, and `references/editors.md`
for the four editor checklists.
