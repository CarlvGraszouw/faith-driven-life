"""Make the clean read-aloud recording script from a full script (drawing cues, notes and tables removed).
usage: python3 make_readaloud.py ep1-script-v5.md ep1-recording-script.md"""
import re, sys
src, out = sys.argv[1], sys.argv[2]
text = open(src).read().split('## Word count and runtime')[0]
# short pauses after the lines that should land (performance marks, not read aloud)
PAUSE_AFTER = [
    "Then they turned and went away.",
    "He could forget the king only because the king was doing his job.",
    "No stone marks the edge of God's land.",
    "What belongs to God is you, every part of you, on every day of the week.",
    "Whose image is this?\n",
    '"Your kingdom come. Your will be done."',
]
lines, suggestions = [], []
for line in text.splitlines():
    if line.startswith('[DRAWING') or line.startswith('*Narration') or line.strip() == '---':
        continue
    if line.startswith('>'):
        suggestions.append(line.lstrip('> ').replace('**Suggested for Carl:** ', ''))
        continue
    if line.startswith('# '):
        continue
    if line.startswith('## '):
        title = line[3:].strip()
        title = re.sub(r"\s*\((channel (intro|outro)), Carl's copy\)", r" (\1)", title)
        lines.append(f"\n### {title}\n")
        continue
    lines.append(line)
body = re.sub(r'\n{3,}', '\n\n', '\n'.join(lines)).strip() + '\n'
for p in PAUSE_AFTER:
    if p.endswith('\n'):
        body = body.replace(p, p.rstrip('\n') + '\n\n*(pause)*\n', 1)
    else:
        body = body.replace(p, p + '\n\n*(pause)*', 1)
words = len(re.findall(r"[A-Za-z0-9’'\-]+", re.sub(r'\*\(pause\)\*|###[^\n]*', '', body)))
head = ("# What a Kingdom Actually Was\n\n"
        "**A Faith Driven Life · Episode 1 · recording script**\n\n"
        f"Read at an easy audiobook pace, about 150 words a minute (roughly {round(words / 150)} minutes). "
        "*(pause)* marks a two-second rest so a line can land. Section headings are for you, not for reading aloud. "
        "Scripture is quoted from the NIV.\n\n---\n")
tail = ''
if suggestions:
    tail = "\n---\n\n### Suggestions for the intro and outro (your call)\n\n" + '\n'.join(f"- {s[:1].upper() + s[1:]}" for s in suggestions) + '\n'
open(out, 'w').write(head + '\n' + body + tail)
print(out, words, 'words')
