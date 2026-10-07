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
by a thousand fingers"), stacks clever devices, chops thoughts into short punchy sentences,
and writes for the eye. This skill exists to stop that. Follow the pipeline in order; do not
skip to drafting.

## Carl's rules come first

Carl's own briefs are in `references/carl/` (copied from his Drive). Read all four before
writing. Where they disagree with anything else in this skill, they win.

- **How the episode is voiced.** Carl pastes plain text into Spotify Studio, and its narrator
  voice reads at about 200–218 words a minute. It pauses at every full stop and paragraph
  break, so runs of short sentences sound clipped and robotic. This is why the rhythm rule
  below exists.
- **Rhythm (`BRIEF-STORY-v2.md`).**
  - Most sentences run 12–28 words, joined the way people talk ("and", "so", "when", "because").
  - A sentence under 8 words is rare: at most 1 per 400 words, never two in a row, and never
    the last line of a paragraph.
- **No AI statements.** No summary lines, signposts, slogans or "not X but Y" contrasts.
  The stock phrases are listed in `BRIEF-STORY.md`.
- **Never cut content.**
  - Every point, scene, explanation and Scripture in the current published script must
    survive. Longer is better, and episodes run 12–17 minutes.
  - The only exceptions are details Carl himself has rejected.
- **Capitals for God everywhere, including inside Bible quotes (`DEITY-CAPS.md`).**
  - He, Him, His, plus Me, My, Us and Our when God speaks.
  - You and Your when someone speaks to Him.
  - King, Great King, Lord, the Kingdom (of God).
- **For the newcomer.**
  - Explain every unfamiliar word inside the sentence, the first time it appears.
  - Speak no chapter and verse aloud.
  - Quote Scripture in NIV-style wording.
- **The shape.**
  - First line: `Episode N — Title`.
  - Open inside a scene, and return to that scene at the end.
  - Then give two or three sentences for the listener's week.
  - Close with "The next episode is called …".
- **What the spoken text never contains.**
  - Headings, brackets, digits or more than three dashes.
  - More than two rhetorical questions; questions in dialogue don't count.
- **The checks must pass** (in `checks/`):
  - `python3 checks/rhythm_check.py <script.txt>` must print `RESULT: PASS`.
  - `python3 checks/ai_check.py <script.txt>` must print `0 flagged`.
  - After a capitals-only correction, `python3 checks/case_guard.py <before> <after>` must
    report that nothing else changed.

## Pipeline

1. **Story bible** (`script/story-bible.md`). Write it before any prose. It covers:
   - The *one meaning*: the single truth the listener must feel at the end, in one sentence.
   - The *dramatic question* that pulls them from the first minute to the last.
   - The *spine*: the story that carries the teaching. It is a real scene from Scripture or
     history, or a character we follow. Teaching rides inside scenes; it never replaces them.
   - The author's voice. Read the author's own book (The King's Rule, in Drive) and note how
     he speaks: sentence length, warmth, directness, favourite turns of phrase, how he
     addresses the listener. Quote 5–10 short lines that sound like him, and write in that voice.
   - The facts and Scripture the story may use, each with its source.
   - The **content floor**: every point of the current published script, ticked off later.
2. **Beat sheet** (`script/beat-sheet.md`), one row per drawing:
   `beat | what happens in the story | what the listener feels | the drawing | min seconds`.
   - Each beat must *move* the story or *deepen* the meaning. If it does neither, cut it.
   - **Timing.** A drawing needs its draw time plus about 1.5 s to breathe. At Studio's
     ~3.4 spoken words per second, a beat needs at least `(draw seconds + 1.5) × 3.4` words.
     When a beat is short, expand the *story*: let the moment play out, add a line of dialogue,
     say what is at stake. Never pad with description.
3. **Draft** (`script/epN-script-vX.md`), beat by beat, with `[DRAWING: …]` cues.
   - Follow `references/craft.md`.
   - Run the checks above after every pass.
4. **Edit passes.** Run them as separate agents, each with only the draft and its checklist
   from `references/editors.md`:
   - the *author's ear*, from `references/carl/REVIEW-v2.md`;
   - the *story editor*;
   - the *content and accuracy editor*;
   - the *cold listener*.

   The writer revises against all of them, keeping the checks green. Repeat until the cold
   listener reports no place where attention drops.
5. **Hand-off.**
   - **The Studio text** (`script/epN-vX-studio.txt`): the plain text Carl pastes into Studio.
     It has the title line and the spoken paragraphs only, with no headings or cues.
   - **The full script** with section headings and drawing cues, plus a word count and the
     estimated runtime per section.
   - **The updated beat sheet** for the artists.
   - **Show notes for Spotify**, in the format in `references/carl/BRIEF-STORY.md`.

## Non-negotiables

- Every concrete detail must carry meaning for this story. Texture for its own sake is cut.
- Scenes, not summaries: put the listener *in* a moment, with people, stakes and a turn.
- One voice, the author's, warm and plain. No performance, no cleverness for its own sake.
- Written for the ear. It must be easy to follow on one hearing at Studio's pace, and the
  sentences flow rather than chop.
- Scripture is quoted accurately with references kept in the notes, and history is never
  overclaimed.

See `references/craft.md` for the rules with before/after examples, and `references/editors.md`
for the editor checklists.
