"""Build the v6 full script (drawing cues, sections, runtime) and the beat-sheet table
from the plain Studio text, which is the single source of the narration.

usage: python3 make_v6.py            (writes ep1-script-v6.md and beat-table-v6.md)

Each cue is anchored to the exact words that start the sentence where its drawing begins.
Timing is at Studio's pace, about 3.4 spoken words a second, pauses included (the v1
recording). A beat needs at least (draw seconds + 1.5) x 3.4 words.
"""
import re

SRC = 'ep1-v6-studio.txt'
WPS = 3.4            # Studio narrator, words per second, pauses included
INTRO_S, OUTRO_S = 12.1, 17.0   # Carl's recorded channel intro and outro (v1 timeline)

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
    ("Caesar was the Roman emperor", 'a05', 'EXISTING', "Roman soldiers along the colonnades of the temple", 10.2,
     "Rome's soldiers on the colonnades at every festival; Caesar's men watching over the feast of freedom.", "Watched; the irony stings."),
    ("Every tax the people paid", 'a06', 'EXISTING', 'Jesus where the road forks: the angry crowd ("YES") on one side, soldiers ("NO") on the other', 9.1,
     "The tax felt like bowing to a foreign king. Yes loses the crowd; no means revolt, with soldiers a short walk away.", "No way out."),
    ("But Jesus sees straight through them", 'a07', 'EXISTING', "a ringed hand puts the coin into Jesus' open palm", 8.6,
     "\"Bring Me a denarius.\" The coin is put in His hand; the whole trap fits in the palm of a hand.", "The turn begins."),
    ("Jesus looks at the coin", 'a08', 'EXISTING', "the coin, large: the head of Tiberius, then the words around it", 7.5,
     "Tiberius' head and the claim \"son of the divine Augustus\": the son of a god.", "The audacity of the claim."),
    ("Then He turns it over", 'a09', 'EXISTING', "the other side of the coin: the seated figure and the words PONTIF MAXIM", 7.1,
     "Highest priest, between his people and heaven. Neither title belonged to Caesar; both belonged to the man holding the coin.", "A shiver of recognition."),
    ("Jesus holds the coin up where", 'a10', 'EXISTING', 'words "Whose image?", Jesus holding the coin up, words "Give back"', 7.0,
     "\"Whose image is this?\" \"Caesar's.\" \"Give back to Caesar what is Caesar's and to God what is God's.\"", "The answer cuts both ways."),
    ("The crowd has nothing to shout about", 'a10b', 'NEW', "the fork from a06 again, gone quiet: the crowd lowering its fists, the soldiers turning back to the colonnade, the questioners standing stiff in front of Jesus", 9.0,
     "Nothing to shout about, no one to arrest; the trappers fail to catch Him out (after Luke 20:26).", "The trap closes on the trappers."),
    ("Astonished by His answer", 'a11', 'EXISTING', "the questioners walking away, amazed", 3.1,
     "Astonished, they fall silent and go away.", "A held breath."),
    '## 2. What belongs to God?',
    ("Caesar's face was on the coin", 'b01', 'EXISTING', "the coin, an arrow, Caesar with his hand held out", 6.4,
     "Caesar's face, Caesar's coin: he can have it back, the easy half.", "Obvious, almost light."),
    ("Jesus had gone on, though", 'p01', 'NEW', 'beside Caesar\'s coin, an empty coin with no face and a large question mark; words "and to God what is God\'s"', 5.5,
     "\"And to God what is God's\" leaves the question: what belonged to God?", "The hook lands on the listener."),
    ("I believe the men who heard Him", 'p02', 'NEW', 'the words "What a Kingdom Actually Was" written like a chapter heading, a small crown above them', 4.7,
     "The men knew the answer at once; we have forgotten what they knew: what a kingdom actually was.", "Curiosity: what did they know?"),
    '## 3. A word that lost its weight',
    ("The Kingdom of God was the first thing", 'c01', 'NEW', 'Jesus standing on the shore of the Sea of Galilee, fishermen and villagers around Him; words "The Kingdom of God has come near"', 13.8,
     "John jailed by Herod; Jesus preaches the Kingdom in Galilee anyway. Repent explained. They lived inside a kingdom: Herod ruled Galilee, Rome ruled Herod.", "Danger, and boldness."),
    ("For most of us a kingdom is much harder", 'c05', 'NEW', "two halves: on the left a ballot box with arrows rising from a crowd of voters to a leader; on the right a throne with arrows coming down from the king to the people", 7.0,
     "Democracy: power starts with the people. In the Bible's world it flowed down from the king; his decree became the way things were.", "Our habits, seen from outside."),
    ("Today the word kingdom has gone soft", 'c02', 'NEW', "a storybook castle on a hill, a king on a throne, a small dragon far off (lighter, storybook style)", 7.0,
     "Today the word has gone soft: castle, throne, dragon, harmless.", "A smile of recognition."),
    ("We hear the word law", 'c06', 'NEW', 'three small pictures in a row: "law" under a parliament with a raised hand voting; "covenant" under two people signing across a table; "kingdom" under a family with suitcases walking to a border post', 9.0,
     "Law, covenant and kingdom all heard through our world; a man in the temple courts would recognise none of those pictures.", "Caught out, gently."),
    ("Many of us pray for that Kingdom", 'c03', 'NEW', 'a man and a woman in a church pew, heads bowed; words "Your Kingdom come, Your will be done"', 9.3,
     "We pray \"Your Kingdom come\" every Sunday, quickly, on the way to daily bread.", "Caught in the act."),
    ("Those two lines ask for one thing", 'c04', 'NEW PART', "on c03's board: an equals sign joining the two halves of the prayer, and under them \"wherever the king's will is done\"", 4.5,
     "Two lines, one request: a kingdom was wherever the king's will was done.", "A small \"oh\"."),
    '## 4. The boundary stone',
    ("In a museum in Istanbul", 'd01', 'NEW', "a weathered boundary stone in a museum case with a small label; beside it, the same stone standing by a dusty road, a traveller with a staff reading it", 9.0,
     "A boundary stone in Istanbul once stood at the edge of a king's land; every traveller knew what it meant.", "Curiosity; an old object comes alive."),
    ("From that stone onward the king", 'd02', 'NEW PART', "on d01's board, beyond the stone: an official taking a share of grain, a soldier keeping watch, a family at peace", 5.0,
     "Beyond the stone: the king's law, his taxes, his soldiers, his protection.", "The line is real."),
    ("Behind that stone stood three things", 'd03', 'NEW', "three drawings joined by a scroll: a crown (the king), a field with its edges marked (the land), a crowd of families (the people); words \"king · land · people\"", 8.0,
     "Three things behind the stone: a king nobody voted for, real land, and a people bound by covenant; loyalty the one condition, treason the one crime.", "Clarity."),
    '## 5. The farmer who forgot his king',
    ("Long before Caesar, in Assyria", 'e01', 'CHANGED', "before dawn, a farmer leads his ox out to his field; a mud-brick house behind him; far off at the end of the field, beside the road, a tall stone", 8.0,
     "In Assyria a farmer leads his ox to a field he thinks of as his own; his father is buried in it.", "Warmth and roots: this is his."),
    ("He has never seen the king", 'e02', 'NEW', "the stone, close: tall and round-topped, the king carved in profile with one hand raised, symbols of his gods above him and lines of writing below; the road runs on into the next kingdom's hills", 7.0,
     "He has never seen the king, who has sent his face: carved on the stone at the end of the field, claiming the land.", "The king is here after all."),
    ("The farmer walks past it every day", 'e02b', 'NEW PART', "on e02's board: the farmer walking past the stone with a hoe over his shoulder, not looking up", 3.5,
     "He walks past it daily and hardly sees it; he is his own man, and the field is his.", "Ease, and a quiet illusion."),
    ("Then one harvest the king's officials", 'e03', 'CHANGED', "the threshing floor: a scribe counts the grain on a tablet while the king's officials load sacks onto a cart; the farmer stands by", 9.0,
     "At harvest a scribe counts the grain and a share goes to the throne.", "The first jolt."),
    ("Another year the king is building", 'e04', 'CHANGED', "an official counts the farmer's two sons off a list; the boys walk away with an overseer toward a town whose new wall is going up; the farmer and his wife watch from the door", 9.5,
     "The officials count his sons for the king's wall; that year he harvests alone.", "Cost; an ache."),
    ("And one spring an enemy army", 'e05', 'CHANGED', "beyond the stone, enemy spears on the far hills; the farmer's family hurrying in at the town gate; the king's soldiers standing on the new wall", 11.0,
     "An enemy army gathers beyond the stone; the family shelters behind the wall the sons built, and the king's soldiers stand on it.", "Fear, then relief: the cost becomes protection."),
    ("Now the farmer understands", 'e06', 'CHANGED', "from the wall, the farmer looks out at the stone and the carved face on it, his field safe behind the line of soldiers; words \"the king's land\"", 7.3,
     "The field was never his alone; even his father's grave is the king's land. He could forget the king because the king was doing his job.", "The turn: belonging, not loss."),
    ("Most of us live a lot like that farmer", 'e07', 'SAME BOARD', "a modern morning: a parent heading out of the door with a bag, children at the breakfast table, a full calendar on the wall", 8.0,
     "We live like the farmer; we take God's patience for absence, yet all that time He has kept watch.", "Seen; and kept."),
    '## 6. The Great King',
    ("The Bible was written in the farmer's world", 'e10', 'NEW', 'a king\'s seal pressed into a clay tablet, a crowd with hands raised to swear; words "I will be your God, and you will be My people"', 9.0,
     "God speaks the covenant words: \"I will be your God, and you will be My people\": tender, and the formal words of a king binding a people.", "Tender and solemn at once."),
    ("In the laws God gave to Israel", 'e11', 'NEW', 'a boundary stone with the words "The land is Mine" carved on it, fields of Israel behind', 5.0,
     "\"The land is Mine\": God sets up His own boundary stone.", "Claimed."),
    ("A psalm, one of the songs", 'e09', 'CHANGED', "hills, a sea, a village and its people, all under one wide sky, with no stone anywhere; words \"The earth is the Lord's\"", 10.8,
     "\"The earth is the Lord's…\" No stone marks the edge of God's land; His Kingdom is wherever His word is obeyed, already in their midst.", "Claimed, gently; the horizon opens."),
    ("The Bible also calls God the King of kings", 'n01', 'NEW', 'a great throne high up; below it smaller kings kneeling, their crowns laid on the steps; words "King of kings"', 9.0,
     "King of kings: high praise to us, an exact title then, for an emperor over lesser kings. God is the Great King.", "Awe."),
    ("God chose to make Himself known", 'n02', 'NEW', "a long line of families walking out of Egypt toward a mountain, a cloud over it; at the mountain's foot, a tablet", 10.0,
     "God came to Israel as the Great King: chose them, rescued them from Egypt, bound them to Himself; even their kings are under His law.", "Rescued, and claimed."),
    '## 7. How the king reached the village',
    ("That farmer in Assyria never once saw", 'm01', 'NEW', 'the farmer\'s village small at the edge of the board, four paths leading to it; on the first path a king speaking and a scribe writing; then Mount Sinai in smoke; words "God spoke all these words"', 9.0,
     "Four ways the king's will reached the village. The first, the decree: at Sinai God spoke and His commands became law.", "The pattern begins."),
    ("The second was the messenger", 'm02', 'NEW', 'a herald on horseback at the village gate reading from a scroll, villagers listening; words "Thus says the Lord"', 9.0,
     "The herald speaks for the king; the prophets were God's heralds.", "The King's voice in a man's mouth."),
    ("One day the prophet Nathan", 'm03', 'NEW', "the prophet Nathan, plainly dressed, pointing at King David on his throne; David's hand at his chest", 8.0,
     "Nathan, an ordinary man, confronts King David, and the king has to listen.", "Tension; the small man stands tall."),
    ("Jesus carried this forward", 'm04', 'NEW', 'Jesus sending out His followers two by two along a road; words "Whoever listens to you listens to Me"', 8.0,
     "Jesus sends His followers out with His authority.", "Commissioned."),
    ("The third was the written covenant", 'm05', 'NEW', "two clay tablets side by side; then a priest reading a scroll aloud to men, women, children and foreigners among harvest shelters of branches", 11.0,
     "The written covenant, read aloud every seven years at the Feast of Tabernacles to everyone.", "Remembering together."),
    ("The fourth was the royal image", 'm06', 'NEW', "a king's statue in a town square, and a carved stone at a city gate like the farmer's stone, people passing", 8.0,
     "The royal image: statues and carved stones made the king present where he never went.", "Presence."),
    ("In later centuries kings found a way", 'f03', 'SAME BOARD', "a market stall; hands passing coins; one coin drawn large with a king's head on it", 7.0,
     "Then coins carried the king's face into every market.", "Recognition: coins."),
    ("All four of those ways ran in one direction", 'm07', 'NEW', "a throne at the top; four arrows coming down labelled \"speaks\", \"sends\", \"writes\", \"His image\"; people below, ears open and hands lifted", 8.0,
     "All four ways come down from the throne; our part is to hear, receive, remember and live as what we are.", "The whole picture."),
    '## 8. The first page',
    ("Caesar's face had travelled that way", 'f04', 'SAME BOARD', 'the temple courts drawn small; in front, a hand holding Caesar\'s coin; words "the Great King over all the earth"', 10.0,
     "Caesar's face in God's house; two kingdoms at once; they sang of the Great King over all the earth.", "The threads join."),
    ("The question of what belonged to God", 'f05', 'NEW', "the empty coin and question mark from p01, drawn again beside Caesar's coin", 3.0,
     "The question still hangs; they learned the answer as boys, on the first page.", "Leaning in for the answer."),
    ("On that first page God speaks", 'g01', 'SAME BOARD', 'darkness over deep water, light breaking across it; words "Let there be light"', 7.2,
     "God speaks like a king, and light comes.", "Awe."),
    ("Day by day He fills His world", 'g02', 'NEW PART', "on g01's board: dry land rising from the sea, trees and plants, birds in the sky, animals on the ground", 9.0,
     "Day by day He fills His world; all of it is His.", "Wonder."),
    ("Last of all God does something", 'g03', 'SAME BOARD', 'a man and a woman standing in the garden, light falling on them; words "in Our image"', 9.4,
     "Last of all, God places His image in His land (Genesis 1:26–27, in two parts).", "The pieces click."),
    ("So the men in the temple courts carried", 'b02', 'EXISTING, MOVED', 'b02: the coin with a human face (IMAGO DEI) and the scroll; words "in the image of God"; on-screen question changed to "Whose face did they carry?"', 8.3,
     "They carried the answer in their own faces: Caesar stamped his face on silver; God stamped His image on them.", "The answer arrives."),
    ("All his life the farmer in Assyria", 'g04', 'CHANGED', "on the left, the farmer walking past his king's stone; on the right, a man and a woman of today walking out into the world, the same light on them as in g03", 8.0,
     "The farmer never knew he carried a greater King's image. You carry it too, like a statue that breathes or a coin that walks.", "The first \"you\"."),
    ('"Give back to Caesar what is', 'b03', 'EXISTING, MOVED', 'b03: Caesar\'s coin, arrow, "Caesar"; a person, arrow, "God"; the days of the week, every one ticked', 7.2,
     "\"Give back to Caesar…\" The person with God's image belongs to God: every part of you, every day of the week.", "The answer, whole."),
    '## 9. What the image gives you',
    ("The farmer's king counted what", 'h01', 'SAME BOARD', "three people side by side: a mother holding a newborn; an old woman in a chair, a hand holding hers; a prisoner sitting in a cell", 10.0,
     "God's image was on you before you handed Him anything: the newborn, the grandmother, the prisoner.", "Tenderness; worth."),
    ("In the ancient world a king's image was handled", 'h02', 'NEW', "a man and a woman of today, each with the faint outline of the coin's royal image over them; his hands at work in a garden, her hand guiding a child's pen", 8.0,
     "A king's image was handled with care; your body, mind and gifts carry the Great King's likeness.", "Dignity, and care."),
    '## 10. The question comes home',
    ("I often think about those men", 'i01', 'CHANGED', "evening on a road out of Jerusalem; the man who brought the coin has stopped and looks down at Caesar's coin lying in his open palm", 8.0,
     "The man who brought the coin, on the road home: Caesar's face in his palm; then he looks at the hand itself.", "Quiet; the hook goes in."),
    ("Hold out your own hand", 'i02', 'SAME BOARD', 'an open hand of today, palm up, drawn large; words "Whose image is this?"', 6.4,
     "THE PEAK: hold out your own hand, and let Jesus ask, \"Whose image is this?\"", "Personal and still."),
    ("This week, every time you pay", 'j01', 'CHANGED', 'a card tapped to pay at a shop counter; beside it, two open hands lifting up a small ploughed field; words "Your Kingdom come, Your will be done."', 11.4,
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
       "Timed at Studio's pace, about 3.4 words a second; word counts and runtime are at the end.*", "", "---", "",
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
        f"Counted on the narration only. Runtime at Studio's pace, about {WPS} words a second with its pauses (the v1 recording); Carl's checker estimates 218 words a minute, which would make it about {mmss(total / 218 * 60)}.", "",
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
open('beat-table-v6.md', 'w', encoding='utf-8').write('\n'.join(rows) + '\n')

new = sum(1 for c, _ in segs if c[2] in ('NEW', 'NEW PART', 'CHANGED', 'SAME BOARD'))
print(f"{len(segs) + 2} beats ({new} to draw); story {total} words, {mmss(total / WPS)} at {WPS} w/s; episode {mmss(INTRO_S + total / WPS + OUTRO_S)}")
for b, w, m in short:
    print(f"  SHORT beat {b}: {w} words, needs {m}")
