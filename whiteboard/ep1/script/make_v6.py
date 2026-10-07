"""Build the v6 full script (drawing cues, sections, runtime) and the beat-sheet table
from the plain Studio text, which is the single source of the narration.

usage: python3 make_v6.py            (writes ep1-script-v6.md and beat-table-v6.md)

Each cue is anchored to the exact words that start the sentence where its drawing begins.
Timing is at Studio's measured pace, 3.39 spoken words a second with its pauses (the
published Episode 1). A beat needs at least (draw seconds + 1.5) x 3.39 words.
"""
import re

SRC = 'ep1-v6-studio.txt'
WPS = 3.39           # Studio narrator, words per second with its pauses: published Episode 1 body, 2,031 words in 599.5 s
INTRO_S, OUTRO_S = 12.2, 15.4   # Carl's recorded channel intro and outro, measured from the published captions

# (anchor, beat, status, drawing, draw seconds, what happens, what the listener feels)
# A line starting with '## ' instead is a section heading placed before the next cue.
CUES = [
    '## 1. The coin',
    ("It is most likely a Tuesday", 'a02', 'EXISTING', "the temple courts at Passover, crowds, the money changer, a father and son with a lamb", 12.2,
     "Most likely a Tuesday in Jesus' last week; Passover crowds; men sent with a question sharpened into a trap.", "A real place, and danger in it."),
    ("They find Jesus where He has been", 'a03', 'EXISTING', "Jesus seated, teaching, people listening", 3.1,
     "The men find Jesus teaching, as every day that week; a teacher from Galilee.", "The trap moves toward its target."),
    ("The men with the question push", 'a04', 'EXISTING', 'the Pharisees and a Herodian come to the front; words "Taxes to Caesar?" as the question is asked', 11.5,
     "Pharisees and Herodians, unlikely allies, flatter Him and ask: is it right to pay the imperial tax to Caesar?", "Suspicion: a smile hiding a blade."),
    ("Caesar was what everyone called", 'a05', 'EXISTING', "Roman soldiers along the colonnades of the temple", 10.2,
     "Rome's soldiers on the colonnades at every festival; Caesar's men watching over the feast of freedom.", "Watched; the irony stings."),
    ("Every tax the people paid", 'a06', 'EXISTING', 'Jesus where the road forks: the angry crowd ("YES") on one side, soldiers ("NO") on the other', 9.1,
     "The tax felt like bowing to a foreign king. Yes loses the crowd; no means revolt, with soldiers a short walk away.", "No way out."),
    ("But Jesus sees straight through them", 'a07', 'EXISTING', "a ringed hand puts the coin into Jesus' open palm", 8.6,
     "\"Bring Me a denarius.\" The coin is put in His hand; the whole trap fits in the palm of a hand.", "The turn begins."),
    ("Jesus looks at the coin", 'a08', 'EXISTING', "the coin, large: the head of Tiberius, then the words around it", 7.5,
     "Tiberius' head and the claim \"son of the divine Augustus\": the son of a god.", "The audacity of the claim."),
    ("Then He turns it over", 'a09', 'EXISTING', "the other side of the coin: the seated figure and the words PONTIF MAXIM", 7.1,
     "Highest priest, between his people and heaven. Neither title was Caesar's; both belonged to the man holding the coin, the Son of God, who would give His life that week.", "A shiver of recognition."),
    ("Jesus holds the coin up where", 'a10', 'EXISTING', 'words "Whose image?", Jesus holding the coin up, words "Give back"', 7.0,
     "\"Whose image is this?\" \"Caesar's.\" \"Give back to Caesar what is Caesar's and to God what is God's.\"", "The answer cuts both ways."),
    ("The crowd has nothing to shout about", 'a10b', 'AS IN v5', "the fork from a06 again, gone quiet: the crowd lowering its fists, the soldiers turning back to the colonnade, the questioners standing stiff in front of Jesus", 9.0,
     "Nothing to shout about, no one to arrest; the trappers fail to catch Him out (after Luke 20:26).", "The trap closes on the trappers."),
    ("Astonished by His answer", 'a11', 'EXISTING', "the questioners walking away, amazed", 3.1,
     "Astonished, they fall silent and go away.", "A held breath."),
    '## 2. What belongs to God?',
    ("Caesar's face was on the coin", 'b01', 'EXISTING', "the coin, an arrow, Caesar with his hand held out", 6.4,
     "Caesar's face, Caesar's coin: he can have it back, the easy half.", "Obvious, almost light."),
    ("Jesus had gone on, though", 'p01', 'AS IN v5', 'beside Caesar\'s coin, an empty coin with no face and a large question mark; words "and to God what is God\'s"', 5.5,
     "\"And to God what is God's\" leaves the question: what belonged to God?", "The hook lands on the listener."),
    ("I believe the men who heard Him", 'p02', 'AS IN v5', 'the words "What a Kingdom Actually Was" written like a chapter heading, a small crown above them', 4.7,
     "The men knew the answer at once; we have forgotten what they knew: what a kingdom actually was.", "Curiosity: what did they know?"),
    '## 3. A word that lost its weight',
    ("The Kingdom of God was the first thing", 'c01', 'CHANGED', 'Jesus standing on the shore of the Sea of Galilee, fishermen and villagers around Him; words "The Kingdom of God has come near"', 13.8,
     "John jailed by Herod; Jesus preaches the Kingdom in Galilee anyway. Repent explained. They lived inside a kingdom: Herod ruled Galilee, Rome ruled Herod.", "Danger, and boldness."),
    ("Today the word kingdom has gone soft", 'c02', 'AS IN v5', "a storybook castle on a hill, a king on a throne, a small dragon far off (lighter, storybook style)", 7.0,
     "Today the word has gone soft: castle, throne, dragon, harmless.", "A smile of recognition."),
    ("Most of us also grew up in democracies", 'c05', 'NEW', "a ballot box, with arrows rising from a line of voters to a leader at a podium", 6.0,
     "We grew up in democracies, where power starts with the people and leaders are voted in and out.", "Our own habits, seen."),
    ("We carry that habit into the Bible", 'c06', 'NEW', 'three small pictures in a row: "law" under a parliament with hands raised to vote; "covenant" under two people signing across a table; "kingdom" under a family with suitcases walking to a border post', 9.0,
     "So we hear law, covenant and kingdom through our own world.", "Caught out, gently."),
    ("In the world of the Bible power flowed", 'c07', 'NEW', "a king on a throne, the arrows of his word coming down to the people below; beside it, a man of Jesus' day in the temple courts", 7.5,
     "In the Bible's world power flowed down from the king; a man in the temple courts would recognise none of our pictures.", "The ground shifts."),
    ("Jesus taught His followers a prayer", 'c03', 'CHANGED', 'people of today praying, some in a pew and some at a kitchen table, heads bowed; words "Your Kingdom come, Your will be done"', 9.3,
     "The prayer millions say every week: \"Your Kingdom come\", said quickly, on the way to daily bread.", "Caught in the act."),
    ("The people in those temple courts would have heard", 'c04', 'AS IN v5 (PART)', "on c03's board: an equals sign joining the two halves of the prayer, and under them \"wherever the king's will is done\"", 4.5,
     "Two lines, one request: a kingdom was wherever the king's will was done.", "A small \"oh\"."),
    '## 4. The boundary stone',
    ("In a museum in Istanbul", 'd01', 'NEW', "a carved boundary stone in a museum case with a small label; beside it, a king's stone standing by a dusty road at the edge of his land, a traveller with a staff reading it", 9.0,
     "A boundary stone in Istanbul recorded whose land was whose; out on the roads, kings set up stones at the edges of their land, and every traveller knew what they meant.", "Curiosity; an old object comes alive."),
    ("His officials collected the taxes there", 'd02', 'NEW PART', "on d01's board, beyond the stone: an official taking a share of grain, a soldier keeping watch, a family at peace", 5.0,
     "Beyond the stone: the king's law, his taxes, his soldiers, his protection.", "The line is real."),
    ("Behind that stone stood three things", 'd03', 'NEW', "three drawings joined by a scroll: a crown (the king), a field with its edges marked (the land), a crowd of families (the people); words \"king · land · people\"", 8.0,
     "Three things behind the stone: a king nobody voted for, real land, and a people bound by covenant; loyalty the one condition, treason the one crime.", "Clarity."),
    '## 5. The farmer who forgot his king',
    ("Long before Caesar, a farmer", 'e01', 'AS IN v5', "before dawn, a farmer leads his ox out to his field; a mud-brick house behind him; far off at the end of the field, beside the road, a tall stone", 8.0,
     "In Assyria a farmer leads his ox to a field he thinks of as his own; his father is buried in it.", "Warmth and roots: this is his."),
    ("He has never seen the king", 'e02', 'AS IN v5', "the stone, close: tall and round-topped, the king carved in profile with one hand raised, symbols of his gods above him and lines of writing below; the road runs on into the next kingdom's hills", 7.0,
     "He has never seen the king, who has sent his face: carved on the stone at the end of the field, claiming the land.", "The king is here after all."),
    ("The farmer walks past it every day", 'e02b', 'AS IN v5 (PART)', "on e02's board: the farmer walking past the stone with a hoe over his shoulder, not looking up", 3.5,
     "He walks past it daily and hardly sees it; he is his own man, and the field is his.", "Ease, and a quiet illusion."),
    ("Then one harvest the king's officials", 'e03', 'CHANGED', "the threshing floor: a scribe counts the grain on a tablet while the king's officials load the sacks onto a cart; the farmer stands by", 9.0,
     "At harvest a scribe counts the grain and a share goes to the throne.", "The first jolt."),
    ("Another year the king is building", 'e04', 'AS IN v5', "an official counts the farmer's two sons off a list; the boys walk away with an overseer toward a town whose new wall is going up; the farmer and his wife watch from the door", 9.5,
     "The officials count his sons for the king's wall; that year he harvests alone.", "Cost; an ache."),
    ("And one spring an enemy army", 'e05', 'AS IN v5', "beyond the stone, enemy spears on the far hills; the farmer's family hurrying in at the town gate; the king's soldiers standing on the new wall", 11.0,
     "An enemy army gathers beyond the stone; the family shelters behind the wall the sons built, and the king's soldiers stand on it.", "Fear, then relief: the cost becomes protection."),
    ("Now the farmer understands", 'e06', 'AS IN v5', "from the wall, the farmer looks out at the stone and the carved face on it, his field safe behind the line of soldiers; words \"the king's land\"", 7.3,
     "The field was never his alone; even his father's grave is the king's land. He could forget the king because the king was doing his job.", "The turn: belonging, not loss."),
    ("Most of us live a lot like that farmer", 'e07', 'AS IN v5', "a modern morning: a parent heading out of the door with a bag, children at the breakfast table, a full calendar on the wall", 8.0,
     "We live like the farmer; we take God's patience for absence, yet all that time He has kept watch.", "Seen; and kept."),
    '## 6. The Great King',
    ("The Bible was written in a world like", 'e10', 'NEW', 'a king\'s seal pressed into a clay tablet, a crowd with hands raised to swear; words "I will be your God, and you will be My people"', 9.0,
     "God speaks the covenant words: \"I will be your God, and you will be My people\": tender, and the formal words of a king binding a people.", "Tender and solemn at once."),
    ("In the laws God gave to Israel", 'e11', 'NEW', 'a boundary stone with the words "The land is Mine" carved on it, fields of Israel behind', 5.0,
     "\"The land is Mine\": God sets up His own boundary stone.", "Claimed."),
    ("A psalm, one of the songs", 'e09', 'CHANGED', "hills, a sea, a village and its people, all under one wide sky, with no stone anywhere; words \"The earth is the Lord's\"", 10.8,
     "\"The earth is the Lord's…\" No stone marks the edge of God's land; His Kingdom is wherever His word is obeyed, already in their midst.", "Claimed, gently; the horizon opens."),
    ("The Bible also calls God the King of kings", 'n01', 'NEW', 'a great throne high up; below it smaller kings kneeling, their crowns laid on the steps; words "King of kings"', 9.0,
     "King of kings: high praise to us, an exact title then, for an emperor over lesser kings. God is the Great King.", "Awe."),
    ("God chose that ancient picture of a king", 'n02', 'NEW', "a long line of families walking out of Egypt toward a mountain, a cloud over it; at the mountain's foot, a tablet", 10.0,
     "God came to Israel as the Great King: chose them, rescued them from Egypt, bound them to Himself; even their kings are under His law.", "Rescued, and claimed."),
    '## 7. How the king reached the village',
    ("That farmer in Assyria never once saw", 'm01', 'NEW', 'the farmer at the threshing floor again, an official holding up a sealed decree; then Mount Sinai in smoke; words "God spoke all these words"', 9.0,
     "Four ways the king's will reached the farmer's village. The decree came with the officials; at Sinai God spoke and His commands became law.", "The pattern begins."),
    ("The man who rode in to call", 'm02', 'NEW', 'a herald on horseback at the farmer\'s door with a scroll; beside him a prophet speaking to a crowd; words "This is what the Lord says"', 9.0,
     "The herald who called the sons to the wall spoke for the king; the prophets were God's heralds.", "The King's voice in a man's mouth."),
    ("One day the prophet Nathan", 'm03', 'NEW', "the prophet Nathan, plainly dressed, pointing at King David on his throne; David's hand at his chest; a small lamb drawn in a thought above them; words \"You are the man!\"", 8.0,
     "Nathan's story of the stolen lamb; \"You are the man!\"; the king listens and confesses.", "Tension; the small man stands tall."),
    ("Jesus gave His own followers that same", 'm04', 'NEW', 'Jesus sending out His followers two by two along a road toward a village; words "Whoever listens to you listens to Me"', 8.0,
     "Jesus sends His followers out with His authority.", "Commissioned."),
    ("A king's covenant was written down", 'm05', 'NEW', "two clay tablets side by side; then a priest reading a scroll aloud to men, women, children and foreigners among harvest shelters of branches", 11.0,
     "The written covenant, read aloud again; through Moses, every seven years at the Festival of Tabernacles, to everyone.", "Remembering together."),
    ("And then there was the king's image", 'm06', 'NEW', "the farmer's stone again; beside it a king's statue in a town square and a carved stone at a city gate, people passing", 8.0,
     "The royal image, the way that mattered most: statues and carved stones made the king present where he never went.", "Presence."),
    ("In later centuries kings began to stamp", 'f03', 'AS IN v5', "a market stall; hands passing coins; one coin drawn large with a king's head on it", 7.0,
     "Then coins carried the king's face into every market.", "Recognition: coins."),
    ("All four of those ways ran in one direction", 'm07', 'NEW', "a throne at the top; four arrows coming down labelled \"speaks\", \"sends\", \"writes\", \"His image\"; people below, ears open and hands lifted", 8.0,
     "All four ways come down from the throne, and God comes to His people down the same four; our part is to hear, receive, remember and live as His people.", "The whole picture."),
    '## 8. The first page',
    ("Caesar's face had travelled that way", 'f04', 'CHANGED', 'the temple courts drawn small; in front, a hand holding Caesar\'s coin; words "the Great King over all the earth"', 10.0,
     "Caesar's face in God's house; two kingdoms at once; they sang of the Great King over all the earth.", "The threads join."),
    ("The question of what belonged to God", 'f05', 'AS IN v5', "the empty coin and question mark from p01, drawn again beside Caesar's coin", 3.0,
     "The question still hangs; they learned the answer as boys, on the first page.", "Leaning in for the answer."),
    ("On that first page God speaks", 'g01', 'AS IN v5', 'darkness over deep water, light breaking across it; words "Let there be light"', 7.2,
     "God speaks like a king, and light comes.", "Awe."),
    ("Day by day He fills His world", 'g02', 'AS IN v5 (PART)', "on g01's board: dry land rising from the sea, trees and plants, birds in the sky, animals on the ground", 9.0,
     "Day by day He fills His world; all of it is His.", "Wonder."),
    ("Last of all God does something", 'g03', 'CHANGED', 'a man and a woman standing in the garden, light falling on them; words "in Our image"', 9.4,
     "Last of all, God places His image in His land (Genesis 1:26–27, in two parts).", "The pieces click."),
    ("Caesar could stamp his face on a piece", 'b02', 'EXISTING, MOVED', 'b02: the coin with a human face (IMAGO DEI) and the scroll; words "in the image of God"; on-screen question changed to "Whose face did they carry?"', 8.3,
     "They carried the answer in their own faces: Caesar stamped his face on silver; God stamped His image on them.", "The answer arrives."),
    ("All his life the farmer walked", 'g04', 'AS IN v5', "on the left, the farmer walking past his king's stone; on the right, a man and a woman of today walking out into the world, the same light on them as in g03", 8.0,
     "The farmer never knew he carried a greater King's image. You carry it too: a statue of the Great King that breathes, a coin of a different Kingdom that walks into every room.", "The first \"you\"."),
    ('"Give back to Caesar what is', 'b03', 'EXISTING, MOVED', 'b03: Caesar\'s coin, arrow, "Caesar"; a person, arrow, "God"; the days of the week, every one ticked', 7.2,
     "\"Give back to Caesar…\" The person with God's image belongs to God: every part of you, every day of the week.", "The answer, whole."),
    '## 9. What the image gives you',
    ("The farmer's king counted what", 'h01', 'AS IN v5', "three people side by side: a mother holding a newborn; an old woman in a chair, a hand holding hers; a prisoner sitting in a cell", 10.0,
     "God's image was on you before you handed Him anything: the newborn, the grandmother, the prisoner.", "Tenderness; worth."),
    ("In the ancient world a king's image was handled", 'h02', 'NEW', "a man and a woman of today, each with the faint outline of the coin's royal image over them; his hands at work in a garden, her hand guiding a child's pen", 8.0,
     "A king's image was handled with care; your body, mind and gifts carry the Great King's likeness.", "Dignity, and care."),
    '## 10. The question comes home',
    ("I often think about those men", 'i01', 'AS IN v5', "evening on a road out of Jerusalem; the man who brought the coin has stopped and looks down at Caesar's coin lying in his open palm", 8.0,
     "The man who brought the coin, on the road home: Caesar's face in his palm; then he looks at the hand itself.", "Quiet; the hook goes in."),
    ("Hold out your own hand", 'i02', 'AS IN v5', 'an open hand of today, palm up, drawn large; words "Whose image is this?"', 6.4,
     "THE PEAK: hold out your own hand, and let Jesus ask, \"Whose image is this?\"", "Personal and still."),
    ("This week, whenever money passes", 'j01', 'CHANGED', 'a card tapped to pay at a shop counter; beside it, two open hands lifting up a small ploughed field; words "Your Kingdom come, Your will be done."', 11.4,
     "Let every payment remind you whose image you carry; give back the one field you call your own; pray slowly.", "Resolve."),
    ("The next episode is called", 'k01', 'CHANGED', 'on j01\'s board, the words "Next: The Treaty of the Great King"; it finishes over the first seconds of the outro', 4.0,
     "The next episode is called The Treaty of the Great King.", "Anticipation."),
]


def words(s):
    return len(re.findall(r"[A-Za-z0-9'’]+", s))


def mmss(t):
    t = int(round(t))
    return f"{t // 60}:{t % 60:02d}"


text = open(SRC, encoding='utf-8').read()
title, body = text.split('\n', 1)
paras = [p.strip() for p in re.split(r'\n\s*\n', body) if p.strip()]
flat = '\n\n'.join(paras)

# locate every anchor once, in order
marks, pos = [], 0
for c in CUES:
    if isinstance(c, str):
        continue
    i = flat.find(c[0], pos)
    assert i >= 0, f'anchor not found after the previous cue: {c[0]!r}'
    assert i == 0 or flat[i - 1] in '\n ' and (i < 2 or flat[i - 2] in '\n.?!"'), f'anchor does not start a sentence: {c[0]!r}'
    marks.append((i, c))
    pos = i
# narration of each beat = text from its anchor to the next anchor
segs = []
for k, (i, c) in enumerate(marks):
    j = marks[k + 1][0] if k + 1 < len(marks) else len(flat)
    segs.append((c, flat[i:j].strip()))

# ---------- full script ----------
out = ["# A Faith Driven Life — Episode 1: What a Kingdom Actually Was", "",
       "*Narration script v6. The spoken text is exactly `ep1-v6-studio.txt`, the plain text Carl pastes into Studio; this copy adds section headings and drawing cues (lines in [square brackets], never read aloud). "
       "Each drawing starts as the narrator reaches its cue. Beat ids match `beat-sheet.md`. Scripture is NIV (2011), with Carl's capitals for God. "
       "Timed at Studio's measured pace, 3.39 words a second (203 a minute); word counts and runtime are at the end.*", "", "---", "",
       "## Opening (channel intro, Carl's recorded audio)", "",
       '[DRAWING a01 · existing title card: brandmark, "A Faith Driven Life", "Episode 1 · What a Kingdom Actually Was"]', ""]
sections, cur = [], None
heads = {}
pending = None
for c in CUES:
    if isinstance(c, str):
        pending = c[3:]
    else:
        heads[c[1]] = pending
        pending = None
for c, seg in segs:
    h = heads.get(c[1])
    if h:
        out += ["---", "", f"## {h}", ""]
        cur = [h, 0]
        sections.append(cur)
    out += [f"[DRAWING {c[1]} · {c[2].lower()}: {c[3]}]", "", seg, ""]
    cur[1] += words(seg)
out += ["---", "", "## Closing (channel outro, Carl's recorded audio)", "", '[DRAWING k02 · existing end card: brandmark, "A Faith Driven Life"]', "", "---", ""]

total = sum(s[1] for s in sections)
out += ["## Word count and runtime", "",
        f"Counted on the narration only. Runtime at Studio's measured pace, {WPS} words a second with its pauses (203 a minute, from the published Episode 1's captions). Carl's checker assumes 218 words a minute, which would make the story {mmss(total / 218 * 60)}.", "",
        "| Section | Words | Runtime | Starts at |", "|---|---:|---:|---:|",
        f"| Opening (channel intro, Carl's recorded audio) | — | {mmss(INTRO_S)} | 0:00 |"]
t = INTRO_S
for h, w in sections:
    out.append(f"| {h} | {w} | {mmss(w / WPS)} | {mmss(t)} |")
    t += w / WPS
out += [f"| Closing (channel outro, Carl's recorded audio) | — | {mmss(OUTRO_S)} | {mmss(t)} |",
        f"| **Story total (narration only)** | **{total}** | **{mmss(total / WPS)}** | |",
        f"| **Episode with intro and outro** | | **{mmss(INTRO_S + total / WPS + OUTRO_S)}** | |", ""]
open('ep1-script-v6.md', 'w', encoding='utf-8').write('\n'.join(out))

# ---------- beat table ----------
rows = ["| # | Beat | Status | What happens in the story | What the listener feels | The drawing | Draw s | Min words | Script words | Starts at |",
        "|---|---|---|---|---|---|---:|---:|---:|---:|",
        f"| 1 | a01 | **EXISTING** | Channel intro (Carl's recorded audio). | Settled, expectant. | Title card: brandmark, \"A Faith Driven Life\", \"Episode 1 · What a Kingdom Actually Was\". | 9.3 | — | (audio {INTRO_S:.0f} s) | 0:00 |"]
t, short = INTRO_S, []
n = 1
for c, seg in segs:
    h = heads.get(c[1])
    if h:
        rows.append(f"| | **{h}** | | | | | | | | |")
    n += 1
    w = words(seg)
    minw = round((c[4] + 1.5) * WPS)
    flag = '' if w >= minw else ' ⚠'
    if flag:
        short.append((c[1], w, minw))
    rows.append(f"| {n} | {c[1]} | **{c[2]}** | {c[5]} | {c[6]} | {c[3][0].upper() + c[3][1:]}. | {c[4]:.1f} | {minw} | {w}{flag} | {mmss(t)} |")
    t += w / WPS
rows.append(f"| {n + 1} | k02 | **EXISTING** | Channel outro (Carl's recorded audio). | Warmth. | End card (brandmark, \"A Faith Driven Life\"). | 6.0 | — | (audio {OUTRO_S:.0f} s) | {mmss(t)} |")
n_exist = sum(1 for c, _ in segs if c[2].startswith('EXISTING')) + 2   # + a01, k02
n_parts = sum(1 for c, _ in segs if 'PART' in c[2])
n_draw = len(segs) - n_exist + 2
HEAD = f"""# Beat sheet — Episode 1: What a Kingdom Actually Was (v6)

> **v6** goes with `ep1-v6-studio.txt` (the text Carl pastes into Studio) and `ep1-script-v6.md` (the same text with section headings and drawing cues). The script now follows Carl's own rules (`.claude/skills/story-script/references/carl/`), brings back everything from the published Episode 1, and is timed at Studio's measured pace. The v5 sheet is kept as `beat-sheet-v5.md`.

One row per drawing, in narration order. **This file is generated by `make_v6.py`** from the script and the cue list in that file: to move a drawing or change its description, edit `CUES` there and run `python3 make_v6.py`. The script words for a beat are the words from its cue to the next cue.

**Timing rule.**
- A drawing needs its draw time plus about 1.5 s to breathe.
- Studio's narrator reads at {WPS} words a second, pauses included. That is 203 a minute, measured from the published Episode 1's captions: 2,031 words in 599.5 s.
- So a beat needs at least `(draw s + 1.5) × {WPS}` words.
- Every beat meets it except k01. That is the closing title, which finishes over the first seconds of Carl's outro.
- Where a beat has more words than it needs, the drawing finishes and holds (slow push-in) while the story goes on.

**Draw times.**
- **Existing art:** the natural times from `node render.js ../preview/ep1-2min.json --plan`.
- **New art:** estimates by type. Wide and crowd scenes 10–12 s, full scenes with two to four figures 7–9 s, simpler scenes 5–7 s, coins 3–5 s, and handwritten words about 0.12 s a character.
- Artists should keep new scenes inside these budgets, or the narration for that beat must grow.

**Totals.**
- **Drawings:** {len(segs) + 2} beats.
  - {n_exist} use existing art: 13 in place and 2 moved.
  - {n_draw} are to be drawn: {n_draw - n_parts} boards plus {n_parts} parts added to a board already on screen (c04, d02, e02b, g02).
- **Length:** the story is {total:,} words, {mmss(total / WPS)} at Studio's pace. With Carl's recorded intro ({INTRO_S:.0f} s) and outro ({OUTRO_S:.0f} s) the episode runs about {mmss(INTRO_S + total / WPS + OUTRO_S)}.

**Status key:**
- **EXISTING** = art-v2, already drawn.
- **EXISTING, MOVED** = already drawn, at a new place in the timeline.
- **AS IN v5** = specified in the v5 sheet, not drawn yet, unchanged.
- **CHANGED** = specified in v5 and changed here.
- **NEW** = new in v6.
- **NEW PART** = new in v6, added to a board already on screen.

## What changed since the v5 sheet

**Added (18).** These carry the content of the published Episode 1 that v5 had dropped:
- **The habits we bring to the word kingdom:**
  - c05, the ballot box;
  - c06, the three words we mishear (law, covenant, kingdom);
  - c07, power coming down from the throne.
- **The boundary stone:**
  - d01, the stone, in the museum and by the road;
  - d02, life beyond the stone, as a part on d01's board;
  - d03, king, land and people.
- **The covenant:**
  - e10, "I will be your God and you will be My people";
  - e11, "The land is Mine".
- **The Great King:**
  - n01, King of kings;
  - n02, Israel brought out of Egypt to the mountain.
- **The four ways the king's will reached the village, each met by the farmer:**
  - m01, the decree, with the officials at the threshing floor and Sinai;
  - m02, the herald and the prophets;
  - m03, Nathan and David;
  - m04, Jesus sending out His followers;
  - m05, the written covenant read aloud;
  - m06, the royal image;
  - m07, all four ways coming down from the throne.
- **h02:** the image handled with care.

**Changed (8):**
- **c01:** a capital K in the drawn words.
- **c03:** people praying, some in a pew and some at a kitchen table, with capitals in the words.
- **e03:** the sacks go onto carts, as narrated.
- **e09:** the words read "The earth is the Lord's".
- **f04:** the words read "the Great King over all the earth".
- **g03:** the words read "in Our image".
- **j01:** the words read "Your Kingdom come, Your will be done."
- **k01:** only the next title, written on j01's board. Carl's brief asks for one plain sentence here, with no teaser scene.

**Capitals for God on screen.** Every drawn word and caption follows Carl's rule (DEITY-CAPS): He, His, Me, Our, You, Your, Kingdom, Great King. b02's question changes to "Whose face did they carry?" (Carl to approve, as in v5).

"""
NOTES = f"""

## Notes for the timeline

- **Multi-part scenes.** Set each part's `at` to the words it illustrates. Write on-screen words as the narrator says them, not before.
- **Shared boards.**
  - p01 sits beside b01's coin, and f05 repeats that pair.
  - c04 goes on c03's board, d02 on d01's, e02b on e02's, g02 on g01's and k01 on j01's.
- **a10b reuses a06.** Draw the same fork and the same people a moment later, with the anger gone.
- **One farm throughout.** e01–e06 are one family, one farm and one stone, and they come back in the four ways:
  - the threshing floor in m01;
  - the farmer's door in m02;
  - the stone in m06 and g04.

  Keep the farmer, his wife, the two sons, the house, the field and the stone the same everywhere.
- **The king is never drawn as a person in the farmer's story.** He appears only as the face carved on the stone.
- **The stone (e01, e02, e02b, e05, e06, m06, g04).**
  - A tall round-topped stele, with the king carved in profile in a long fringed robe and a tall royal headdress, right hand raised.
  - Symbols of his gods above his head, and lines of cuneiform below.
  - Model it on Assyrian royal stelae. The narration now names Assyria.
- **Dress.**
  - Farmers wear knee-length belted tunics and sandals, with full beards.
  - Officials and scribes wear long fringed robes; the scribe holds a clay tablet and stylus.
  - Soldiers wear pointed helmets and carry spears and round shields.
- **God is never drawn.** In g03 the man and the woman stand in light, and the words "in Our image" carry the moment. Jesus is drawn as in art-v2 (`gen/jesus.py`).
- **i01 → i02 is the peak.** Give i02 its full hold, and do not start j01's drawing until the question "Whose image is this?" has been asked and has rested.
- **If time must be cut,** the beats that can lose a sentence with least damage are c02 (the castle) and c07. Do not cut a10b, e02–e06, f05, i01 or i02.
- **a01 and k02** are Carl's recorded channel intro and outro ({INTRO_S:.1f} s and {OUTRO_S:.1f} s in the published episode). Studio voices only the story.
"""
open('beat-sheet.md', 'w', encoding='utf-8').write(HEAD + '\n'.join(rows) + NOTES)

new = sum(1 for c, _ in segs if not c[2].startswith('EXISTING'))
print(f"{len(segs) + 2} beats ({new} to draw); story {total} words, {mmss(total / WPS)} at {WPS} w/s; episode {mmss(INTRO_S + total / WPS + OUTRO_S)}")
for b, w, m in short:
    print(f"  SHORT beat {b}: {w} words, needs {m}")
