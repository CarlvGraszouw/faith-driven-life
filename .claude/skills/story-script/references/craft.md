# Craft rules — writing for the ear

## 1. Open inside a moment
Within the first three sentences the listener is somewhere, with someone, and something is at
stake. No throat-clearing ("Today we're going to look at…").

## 2. One question pulls the whole episode
Set the dramatic question early, keep it alive, delay the answer, pay it off at the end.
Plant what you will need later (the coin's *image* and *words*) and pay it off (the image the
listener carries).

## 3. Scenes carry the teaching
Rhythm: let a scene play → step back briefly to say what it means → into the next scene.
Roughly 70 % scene, 30 % reflection. A point that has no scene gets one: an ancient farmer, a
herald at a city gate, Nathan in David's hall. Lists ("the first… the second…") are told as a
sequence of scenes, not announced as points.

## 4. Every detail must mean something
Keep a detail only if the story needs it. The coin matters for its *face* and its *claim*
("son of the divine Augustus"), so linger there. Its wear, the heat, the dust, the smell of
the market are cut unless they change what the listener understands or feels.
- Cut: "a little silver disc worth a day's wages, worn smooth by a thousand fingers."
- Keep: "On it was a man's face, and around the face, a claim: *son of the divine Augustus*."

## 5. Sentences for the ear
- **Flowing sentences.** Most sentences run 12–28 words, joined the way people speak when they
  tell a story ("and", "so", "when", "while", "because", "until").
  - Studio's narrator pauses at every full stop, so short sentences in a row sound robotic.
  - Keep sentences under 8 words to at most 1 per 400 words: never two in a row, and never
    the last line of a paragraph.
- **Don't chop one thought** into several sentences. "He has never seen the king. The king has
  never come this far. He sent his face." becomes "He has never seen the king, who has never
  come this far from his palace, and so the king has sent his face instead."
- **Easy to follow.**
  - Keep the subject and verb early, and avoid stacking appositives.
  - Keep sentences under about 38 words.
  - Vary the length within the 12–28 range.
- No nested clauses, parentheses, or asides set off with dashes.
- Every "he/they/it" must be unmistakable on one hearing.
- **Speak numbers, names and references naturally.** Say "in the laws God gave to Israel"
  rather than "Lev 25:23", and write numbers in words.
- **Repeats.** Repeat a key line on purpose as a refrain ("Whose image is this?"); never repeat
  by accident.
- **Move with the scene itself, not with signposts.** "Remember that coin?", "Now think of…",
  "Let us…" and "That leads to…" all fail Carl's checker. Carry the listener with time and
  place: "Long before Caesar, in Assyria, a farmer gets up before dawn…".

## 6. Dialogue
- Use plain, real lines with no adverbs on speech tags.
- Put the speech tag inside a full sentence, so it never stands alone as a short one: write
  `Jesus holds the coin up where they can all see it and asks them, "Whose image is this?"`,
  not `"Whose image is this?" He asked.`

## 7. The listener
Address "you" sparingly and sincerely, mostly at the turns and at the end. Never lecture the
listener; invite them.

## 8. Endings
Land the meaning in an image, not a summary. One clear invitation for the week.

## 9. Patterns that make it sound like AI — cut on sight
- "It's not X. It's Y." and any "not X, but Y" framing.
- Triplets used for rhythm again and again ("the king, the land, the people" once is fine).
- Stock openers and hinges: "Picture this", "Here's the thing", "Now here's where it gets
  interesting", "Let that sink in", "And that changes everything", "In a world where".
- Stacks of rhetorical questions.
- Ending every section on a neat aphorism.
- Explaining a metaphor right after it lands.
- Words: profound, tapestry, delve, journey, unpack, resonate, navigate, landscape, testament,
  realm, multifaceted.
- Decorative sensory filler (see rule 4).
- A list announced as a list ("Three things, really. First…").
- **Lines that fail Carl's checker** (`checks/rhythm_check.py`):
  - **Summary lines:** "That matters…", "This is why…", "It gives…", "the answer is…".
  - **Signposts:** "Remember that…", "Keep that in mind", "We will see…".
  - **Slogans:** "X, and it is.", "You are the statue that breathes and the coin that walks"
    as a standalone line. Fold such a line into a sentence that is still telling the story:
    "You carry that image too, like a statue that breathes or a coin that walks…".
- **Banned contrasts and stock phrases** (`checks/ai_check.py`):
  - "never… , but", "rather than", "Instead of", "is more than a", "isn't about";
  - "stands as", "ultimately".
  - The full list is in `carl/BRIEF-STORY.md`.

## Before / after (from the Episode 1 v2 draft)

| v2 draft | Why it fails | Direction |
|---|---|---|
| "Someone presses a denarius into His hand, a little silver disc worth a day's wages, worn smooth by a thousand fingers." | Decorative trivia; distracts from the image and the claim. | Go straight to the face and the words on it. |
| "Three things, really. First, the king himself." | A lecture outline read aloud. | Show a kingdom through a person living in one. |
| "So let's step into their world, starting at the edge of a road." | Announces a scene instead of being in it. | Begin the scene: the stone, the road, the traveller. |
| "It's tender, and it's meant to be, but it's also the formal language of covenant." | Explains the feeling instead of letting the words do it. | Let the covenant words stand, then one plain line of meaning. |
