"""Flags the AI-script patterns Carl banned, plus stock AI phrases. Usage: python3 ai_check.py file [file...]"""
import re
import sys

NEG = r"(?:not|n't|never|no longer|nothing)"
PATTERNS = [
    ("not X but Y", rf"\b{NEG}\b[^.!?;]{{0,80}}?[,;—–-]\s*but\b"),
    ("not X. It/He is Y", rf"\b(?:is|was|are|were|did|does|do)\s?{NEG}\b[^.!?]{{0,90}}[.!?]\s+(?:It|He|She|They|This|That|We|You|God|Jesus)\s+(?:is|was|are|were|did|does|do|has|had)\b"),
    ("Not A. Not B.", r"(?:^|[.!?]\s+)Not\s[^.!?]{1,60}\.\s+Not\s"),
    ("sentence starting 'Not ...'", r"(?:^|[.!?]\s+)Not (?:a|an|the|as|because|just|merely|only|simply)\b"),
    ("rather than", r"\brather than\b"),
    ("instead of X, Y", r"(?:^|[.!?]\s+)Instead of\b"),
    ("isn't about X. It's about Y", r"\b(?:is|was)\s?(?:not|n't) about\b"),
    ("more than / less X than Y framing", r"\bis more than (?:a|an|just)\b"),
]
STOCK = [
    "here's the thing", "here is the thing", "perhaps the most", "most striking", "this changes everything",
    "let that sink in", "unpack", "profound", "journey", "delve", "tapestry", "at its core", "game-changer",
    "powerful reminder", "in a world where", "the truth is", "make no mistake", "it's worth noting",
    "here's where it gets", "here is where", "something extraordinary", "never read the same way",
    "buckle up", "dive into", "deep dive", "landscape", "navigate", "testament to", "stands as",
    "it is important to note", "in conclusion", "ultimately,", "crucially", "imagine this",
]


def check(path):
    text = open(path, encoding="utf-8").read()
    flat = re.sub(r"\s+", " ", text)
    hits = []
    for name, rx in PATTERNS:
        for m in re.finditer(rx, flat, flags=re.IGNORECASE):
            start = max(0, m.start() - 40)
            hits.append((name, flat[start:m.end() + 40].strip()))
    low = flat.lower()
    for phrase in STOCK:
        i = low.find(phrase)
        while i != -1:
            hits.append((f"stock phrase '{phrase}'", flat[max(0, i - 40):i + len(phrase) + 40].strip()))
            i = low.find(phrase, i + 1)
    words = len(re.findall(r"\b[\w'’]+\b", text))
    return words, hits


if __name__ == "__main__":
    total = 0
    for p in sys.argv[1:]:
        words, hits = check(p)
        total += len(hits)
        print(f"== {p.split('/')[-1]}: {words} words, ~{words / 218:.1f} min at 218 wpm (+0.45 min intro/outro), {len(hits)} flagged")
        for name, ctx in hits:
            print(f"   [{name}] …{ctx}…")
    sys.exit(1 if total else 0)
