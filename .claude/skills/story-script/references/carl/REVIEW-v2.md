# Review brief: listen to one retold episode as the author would

The author of the podcast "A Faith Driven Life" heard Episode 1 and said: "Too many AI statements. Short sentences of 3, 4 or 5 words in rapid succession. We need to improve on how the story is told." Episode N has now been retold to the rules in SP/scripts/story/BRIEF-STORY-v2.md; read that file first. A narrator voice will read it at about 190 words a minute to listeners who may never have opened a Bible.

## Inputs
- **New script:** SP/scripts/story-v2/epN.txt.
- **Previous version, the content floor:** SP/scripts/story/epN.txt.
- **Bible lookup (World English Bible):** `bash SP/review/verse.sh "DEU 6:4-5"`.
- **Checks:** `python3 SP/review/rhythm_check.py SP/scripts/story-v2/epN.txt` and `python3 SP/review/ai_check.py SP/scripts/story-v2/epN.txt`.

## Read it aloud in your head at a brisk pace, twice, and report
1. **AI voice that the checker cannot catch.** Look for:
   - sentences that comment on the story instead of telling it ("What sets him apart is…", "runs on a different logic", "a quiet truth", "in a very real sense");
   - abstract nouns doing the work ("the logic of the Kingdom", "a posture of trust");
   - tidy reveals;
   - morals tacked on to the end of a paragraph;
   - neat pairs and triplets used for rhythm;
   - "we have heard together" style self-reference;
   - preachy "you must" lines;
   - anything that sounds like an essay or a sermon outline instead of a person telling a story.
2. **Hard to follow by ear.** Look for:
   - sentences that stack appositives or clauses so the listener loses the subject;
   - a sentence with more than one explanation of a new word;
   - long lists;
   - any place the narrator jumps in time or place without carrying the listener.
3. **Choppiness that remains:** short sentences back to back, or a paragraph ending on a punchline.
4. **Newcomer gaps:** an unfamiliar name, word or custom that is not explained the first time.
5. **Content:** go through the previous version paragraph by paragraph and list any point, scene, example, quote or Scripture that is missing or weakened.
6. **Accuracy:**
   - Is any quote changed in meaning? Check it with verse.sh.
   - Has a book error listed in SP/scripts/story/BRIEF-STORY.md come back?
   - Is anything claimed that Scripture or history does not support?

## Output
Do NOT edit the script. Reply with a numbered fix list, most important first, at most 40 items. For each item give:
- the exact sentence as it now stands (quoted);
- what is wrong, in five to ten words;
- a proposed rewrite that keeps the content and obeys BRIEF-STORY-v2.

End with an overall verdict in two sentences: does this sound like a person telling a story, and is it ready once the fixes are made? Include the rhythm_check and ai_check results.
