# Brief: rewrite ONE episode of "A Faith Driven Life" as a story

The author approved Episode 1 in this style: "this is the way they all need to be written." Your job is to rewrite one episode the same way.

Paths (SP = /private/tmp/claude-503/-Users-carlvongraszouw/2323af85-6268-490e-a673-a4882148b1ef/scratchpad):
- THE MODEL. Read it twice before you write: SP/scripts/story/ep1.txt
- Your OLD script. This is the content floor: SP/scripts/epN.txt
- Your BOOK section. This is the source of truth: SP/scripts/src/epN-src.md
- Bible lookup (World English Bible): bash SP/review/verse.sh "MAT 22:21". Book codes: GEN EXO LEV NUM DEU JOS 1SA 2SA 1KI ISA JER EZE DAN MAT MAR LUK JOH ACT ROM 1CO 2CO GAL EPH PHI COL HEB JAM 1PE 1JO REV.
- Banned-pattern checker: python3 SP/review/ai_check.py <file>

## Why the old scripts failed
The author said the old Episode 1 read "fact, fact, fact, one after another." It was hard to follow, read too fast, and was hard to understand for someone who isn't a Christian. The old scripts crammed whole chapters into about 1,180 words and read every chapter and verse aloud.

## What the author wants
1. **Read like a story.** One main scene carries the episode, told so the listener stands inside it. Two to four supporting scenes or pictures should come from the book: its stories, images and examples. Every teaching point grows out of a scene, and each point is explained once, in plain words. Link the scenes so the listener never loses the thread. Use bridges like the model's: "That farmer in Assyria never saw his king. So how did the king's will reach his village?"
2. **Cut no content.** Every point, image, example and Scripture in the OLD script must appear in the new one. You may add more from the BOOK section where it helps the story. Longer is better, according to the author. Aim for 1,900 to 2,400 words of spoken text. Ep1 is 2,030.
3. **Write for a newcomer** who has never read the Bible and hears this once, with no rewind. Explain every unfamiliar name, place, word or custom the first time it comes up, in a short phrase, as the model does. For example: "Passover, the great spring festival of the Jewish people"; "Israel, the ancient Jewish nation"; "a covenant, a solemn agreement"; "to repent means to turn around and change direction"; "Mount Sinai in the desert, after God had brought Israel out of Egypt". Introduce titles like "the Great King" before using them. A listener can't hear a capital letter, so say "God" or "Jesus" wherever "the King" could mean an earthly king.
4. **No spoken chapter and verse.** Introduce Scripture naturally: "Jesus put it like this", "the first page of the Bible says", "in the laws God gave to Israel", "the prophet Isaiah wrote". Quote Scripture exactly as the OLD script or the BOOK quotes it, which is NIV-style wording. Check every quote's meaning with verse.sh. Never invent or loosen a quote; if unsure, describe the passage in plain words.
5. **Keep the corrections.** The old scripts already fixed the book's errors. Never bring back any item in "Book errors" below, even if the book section says it.
6. **Match the model's voice.** Warm, plain and unhurried. Use short-to-medium sentences, present tense inside scenes, and "you" when speaking to the listener. Every paragraph is a breath, and the voice engine pauses at each paragraph break.

## Banned. Zero tolerance; the author spots AI writing instantly
- Any contrast built as negation then correction. That includes "not X but Y", "it wasn't X, it was Y", "he didn't do this, he did that", "X is not A. It is B.", "Not A. Not B. C.", sentences starting "Not", "rather than", "instead of", "isn't about X, it's about Y" and "more than just". State what IS true. If the book makes a contrast, give each side its own plain statement, as the model does: "To our ears that sounds like high praise… In the ancient world it was an exact title."
- Stock phrases: here's the thing, here is where, then comes the, perhaps the most, most striking, this changes everything, let that sink in, unpack, profound, journey, delve, tapestry, at its core, powerful reminder, in a world where, the truth is, make no mistake, something extraordinary, dive into, landscape, navigate, testament to, ultimately, crucially, imagine this, a dignity no one can take away, and that matters, this is the key.
- At most two rhetorical questions in the whole episode; questions inside a scene's dialogue don't count. Also banned: one-word dramatic sentences, short punchy slogan endings, lists of three used as a rhythm habit, hype and cliffhangers.
- At most three dashes. No headings, bullets, brackets, parentheses, italics or markdown. Write numbers and dates in words, and avoid abbreviations.

## Shape
- First line: `Episode N — Title`, using the exact title from the old script. Then a blank line, then the spoken text.
- Open inside a scene from the book. Within the first two paragraphs, add one plain sentence that links back to the previous episode.
- End by returning to the opening scene. Then give two or three sentences of application for the listener's week, as the model does. Then ONE plain sentence: "The next episode is called <next title>." Episode 7 instead closes the series in two or three warm sentences, with no "next episode".
- Episode titles: 1 What a Kingdom Actually Was · 2 The Treaty of the Great King · 3 The Kingdom We Can No Longer See · 4 The Return of the King · 5 The Rules of the King · 6 The King's Economy · 7 Living as the Kingdom Now.

## Book errors that must stay fixed
- **Jubilee and debts:** debts were cancelled every seventh year (Deuteronomy 15:1–2). The Jubilee, every fiftieth year, returned land and freed bond-servants (Leviticus 25).
- **Ch 2, Kline and the treaty:**
  - credit George Mendenhall's earlier work;
  - "dozens" of Hittite treaties survive, not "hundreds";
  - don't give the year 1943;
  - Kline's doctorate was in Assyriology and Egyptology;
  - Deuteronomy follows the treaty form in its overall structure. Kline's outline is 1:1–5, 1:6–4:49, 5–26, 27–30, 31–34. Speak it as sections of the book, never with numbers;
  - the two tablets as duplicate copies is what "many scholars think";
  - present the Hittite parallel as Kline's argument.
- **Ch 3:** Scripture says of the Sinai generation that "they soon forgot his works." Coins came later, about 600 BC; earlier, the king's image was on statues and stone monuments.
- **Ch 4–5:**
  - 1 Samuel 8 does not mention God's grief.
  - Kingship was provided for (Deuteronomy 17) and promised to David (2 Samuel 7). The sin was wanting a king "like all the nations".
  - The people's "yes" at Sinai was real (Exodus 24:7).
- **Ch 7:** include John 18:36, "my kingdom is not of this world", and John the Baptist announcing the Kingdom first. Avoid the "fifteen words" claim.
- **Ch 8:**
  - Jesus fulfils and deepens the law (Matthew 5:17).
  - The Sermon on the Mount is never called a covenant; the new covenant is made at the Last Supper.
  - The law always reached the heart (Exodus 20:17).
  - "Hate your enemy" was a common teaching, not the law of Sinai.
- **Ch 9:** keep "the Great King" for the Father, "God, in the person of his Son". Sinai's covenant was sealed in blood (Exodus 24:8); not every covenant was.
- **Ch 10:** "treason voids the protection" needs the New Covenant assurance (Romans 8:1; John 10:28). "You cannot lobby the throne" needs Hebrews 4:16, "approach God's throne of grace with confidence".
- **Ch 12:**
  - Scripture never says "Saul becomes Paul"; Acts 13:9 says "Saul, who was also called Paul".
  - The wedding supper (Revelation 19) is not the Bible's final image; that is Revelation 21–22.
  - "Royal Scribe" is not in Scripture; names are written in "the Lamb's book of life".
- **Ch 14:** the accuser is answered by Christ's blood (Romans 8:33–34; Revelation 12:11; Zechariah 3). His charges are not thrown out for lack of witnesses.
- **Ch 15:** quote Deuteronomy 15:15 itself, never the book's paraphrase "You were slaves, and I redeemed you…".
- **Ch 16:** Scripture calls royal forced labour a heavy yoke (1 Samuel 8; 1 Kings 12). Never present it as a model.
- **Ch 17:** Matthew 25 is about "the least of these", the needy. For every person bearing God's image, use Genesis 9:6 and James 3:9.

## Before you finish
1. Run ai_check.py on your file until it reports 0 flagged. If it flags a sentence, rewrite it so the contrast is gone; don't just dodge the regex.
2. Go through the OLD script paragraph by paragraph and confirm each point is in the new one.
3. Check every quote with verse.sh.
4. Read it once as a newcomer and explain anything a newcomer would trip on.

## Files to write
- SP/scripts/story/epN.txt: the script.
- SP/scripts/story/epN-notes.txt: show notes for Spotify. The first line is the episode title line. Then 2–4 plain sentences describing the episode, a blank line, and "Bible passages in this episode:" followed by the references in order, separated by " · ". Then a blank line and "From the book The King's Rule."

## Your final reply (under 250 words)
Give the word count and the ai_check result. List any old-script points you could not fit and why; the target is none. List anything in the book section you were unsure about.
