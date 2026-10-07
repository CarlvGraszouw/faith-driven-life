# Editor checklists

Run each editor as a separate agent that sees only the draft, the story bible and its own
checklist. Each returns a numbered list of notes, each quoting the exact sentence and saying
what to do. No rewrites of whole sections — notes only.

## Story editor
- Is there one meaning, and does the ending land it?
- Is the dramatic question set in the first 30 seconds and kept alive to the end?
- Does every beat either move the story or deepen the meaning? Name the beats that do neither.
- Does every section contain at least one real scene (people, place, stakes, a turn)?
- Where does it turn into a lecture? Quote the line where telling replaces showing.
- Where is the emotional peak? Is it earned by what came before?
- Are plants paid off (the coin's image and words → the image the listener carries)?

## Author's ear (Carl's own review brief)
Use `carl/REVIEW-v2.md` as the checklist and `carl/BRIEF-STORY-v2.md` as the standard.
- **Read it aloud in your head at Studio's brisk pace, twice.**
- **Flag AI voice the checker misses:**
  - commentary instead of telling;
  - abstract nouns doing the work;
  - tidy reveals;
  - morals tacked onto paragraph ends;
  - neat pairs and triplets used for rhythm.
- **Flag what is hard to follow by ear:**
  - stacked appositives;
  - two explanations in one sentence;
  - long lists;
  - unmarked jumps in time or place.
- **Flag remaining choppiness and monotony**, as well as any newcomer gaps.
- **Check capitals for God** against `carl/DEITY-CAPS.md`.
- **Report the results** of `checks/rhythm_check.py` and `checks/ai_check.py`.
- **Notes only.** Each note quotes the exact sentence and proposes a rewrite that keeps the
  checks green.

## Ear editor
- Mark every sentence that cannot be read aloud in one easy breath.
- Mark nested clauses, dash asides, parentheses, unclear pronouns, lists of more than three.
- Flag every pattern from "Patterns that make it sound like AI" in craft.md.
- Flag every decorative detail that does not change meaning or feeling.
- Is the rhythm flowing (mostly 12–28 words, almost no short sentences, never two in a row)?
- Are transitions audible to a listener who cannot see headings?
- Does it sound like the author's voice lines in the story bible? Quote lines that do not.

## Content and accuracy editor
- **Content floor.**
  - Go through the current published script paragraph by paragraph.
  - List every point, scene, example, explanation, quote or Scripture that is missing or
    weakened.
- **Scripture.**
  - Every quotation is word for word in the NIV, with Carl's capitals for God.
  - The reference is correct, and kept in the notes.
- **History.** Every claim is supportable and nothing is overclaimed; name the source.
- **Names, places, dates and titles** are correct (Tiberius, Augustus, denarius…).
- **The book errors** listed in `carl/BRIEF-STORY.md` have not come back.
- **Theology** is consistent with the author's book.

## Cold listener
You hear this once and never see the text. Report:
- What you felt in each section, in a few words.
- The moment you leaned in most.
- Every moment your attention drifted — quote the sentence just before it.
- Anything you did not understand on one hearing.
- What you will remember tomorrow.
- Whether the ending made you want to do something, and what.
