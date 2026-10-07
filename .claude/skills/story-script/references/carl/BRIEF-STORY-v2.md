# Brief v2: retell ONE episode of "A Faith Driven Life" as a real story (4 Oct)

SP = /private/tmp/claude-503/-Users-carlvongraszouw/2323af85-6268-490e-a673-a4882148b1ef/scratchpad

## Why there is a v2
The author listened to Episode 1 (now on YouTube) and said: "The story line must be reviewed. Too many AI statements. Short sentences of 3, 4 or 5 words in rapid succession. We need to improve on how the story is told."
A narrator voice reads the script at about 190 words a minute and pauses at every full stop and paragraph break, so runs of short sentences sound clipped and robotic. Neat summary lines and "let us now" signposts sound like a machine explaining instead of a person telling a story.

## Your inputs
- **Your CURRENT script, the content floor:** SP/scripts/story/epN.txt. Every point, scene, example, explanation, quotation and Scripture in it must survive. Never cut content; the author says "longer is better".
- **All rules in SP/scripts/story/BRIEF-STORY.md still apply:**
  - the banned negation contrasts and stock phrases;
  - the book corrections;
  - no spoken chapter and verse;
  - explain every unfamiliar word for a newcomer;
  - the shape: first line, open inside a scene, link to the previous episode, return to the opening scene, two or three sentences for the listener's week, then "The next episode is called …".
- **References if you need them:** the book section is SP/scripts/src/epN-src.md and the older script is SP/scripts/epN.txt.

## The new voice: a person telling a story by the fire
1. **Rhythm.**
   - Most sentences run 12 to 28 words. They flow the way people speak when they tell a story, joined with "and", "so", "when", "while", "because", "until", "by the time".
   - Now and then let a long narrative sentence carry a whole movement of the scene.
   - A sentence under 8 words is rare: at most one per 400 words, never two short sentences in a row, and never as the last line of a paragraph.
   - Never break one thought into several short sentences.
2. **No "AI statements".** Delete or rewrite every sentence that does any of these:
   - **Sums up or comments instead of telling.** "That matters for how we hear the Bible." "Each of those pictures is true." "It sounds tender, and it is." "The direction of power matters most of all." "This is why…" "That is what…"
   - **Announces the next step.** "So let us step into their world." "Now think of a farmer…" "Keep that word in mind." "So hold two scenes side by side." "That leads to a second question." "We will need it again."
   - **Is an aphorism or slogan.** "You are the statue that breathes and the coin that walks." "Love strong enough to matter." Neat balanced pairs, and triplets used for rhythm.
   - **Tells the listener what to feel or conclude.** Let the scene and the characters carry the meaning. When a teaching point must be stated, put it inside the flow of a sentence that is still telling the story, or in a character's mouth, or tie it to a concrete thing the listener can see.
3. **Storytelling craft.**
   - Move through time and place with the scene itself: "By the time the messenger had read the last line, the small king's nobles…" Avoid narrator signposts.
   - Give scenes small concrete details (heat, dust, the weight of a clay tablet, the sound of a crowd) and let people act and speak.
   - Explanations for newcomers ride along inside the sentence: "Moses, the old leader who had brought their parents out of slavery in Egypt forty years earlier, …".
   - Comparisons from modern life (a lease, a home loan, an uncle who paid your school fees) stay. Tell them as a small story in one or two flowing sentences, then return to the scene without a moral tag line.
   - Speak to the listener as "you" only where it is natural and warm, never preachy.
4. **Example of the change** (from Episode 1).
   - Before: "Three things stood behind that stone. The first was the king himself. Nobody elected him. His authority came down to him through his family line, and inside his borders his word was final."
   - After: "Behind that stone stood three things, and the first was the king himself, a man nobody had ever voted for, whose right to rule had come down to him from his father and grandfather, so that inside his borders his word settled every argument."
   - Before: "That matters for how we hear the Bible. Our democratic habits can quietly cast us as God's negotiating partners."
   - After: "When the last line had been read, nobody in that hall asked the small king what he thought of the terms; he pressed his seal into the clay while his nobles watched, and when the Bible says that God made a covenant with His people, it has that kind of moment in mind, a long way from the table where people today sit down as equals and bargain."

## Checks before you finish (all must pass)
1. `python3 SP/review/rhythm_check.py SP/scripts/story-v2/epN.txt` must report RESULT: PASS. Rewrite the flagged sentences properly; never dodge the patterns with tricks such as fake quotes or semicolons.
2. `python3 SP/review/ai_check.py SP/scripts/story-v2/epN.txt` must report 0 flagged.
3. Content: go through the CURRENT script paragraph by paragraph and tick every point in your new version. Your word count must be at least the current script's word count.
4. Accuracy: every quotation is unchanged in meaning and checked with `bash SP/review/verse.sh "DEU 6:4"`. No book error comes back.
5. Read it aloud in your head at a brisk pace, as a newcomer who has never opened a Bible. Can you follow it without rewinding? Does it sound like a person telling you a story?
6. Capitals for God (Carl, 4 Oct): every pronoun and title for God or Jesus is capitalised: He, Him, His, Himself; Me, My, Us, Our when God speaks; You, Your when someone speaks to Him; King, Lord, Father when they mean God. This applies inside Bible quotes too. Human kings, parable characters and "you" said to the listener stay lowercase. The full rule is in SP/scripts/story/DEITY-CAPS.md.

## Files to write
- SP/scripts/story-v2/epN.txt: the script.
- SP/scripts/story-v2/epN-notes.txt: copy SP/scripts/story/epN-notes.txt. Only adjust the description if your story changed what happens. The description must also obey the voice rules.

## Your final reply (under 200 words)
Give the word count (old vs new) and the rhythm_check and ai_check results. Confirm that no content was dropped, or list anything you could not keep. Name the two or three places where the storytelling improved most.
