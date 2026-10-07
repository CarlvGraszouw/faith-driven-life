"""Storytelling rhythm check for the podcast scripts (Carl, 4 Oct: "too many AI statements;
short sentences of 3, 4 or 5 words in rapid succession").

  python3 rhythm_check.py <script.txt> [--all]

Flags, with the sentence text:
  SHORT-RUN  two or more sentences in a row under 10 words
  SHORT      any sentence under 8 words (allowed rarely: at most 1 per 400 words, never in a run)
  CLOSER     a short sentence (under 12 words) that ends a paragraph: the slogan/summary ending
  SUMMARY    a sentence that sums up instead of telling ("That matters...", "This is why...")
  SIGNPOST   the narrator announcing what comes next ("So let us...", "Now think of...")
  MAXIM      aphorism patterns ("X, and it is.", "the A that B and the C that D")
Exit code 0 only when the totals are within the limits printed at the end.
"""
import re, sys

SUMMARY = [
    r"^(that|this|it) (matters|changes|means|is why|is how|is what|leads|gives|tells|shows|explains)\b",
    r"^(that|this) (difference|picture|word|question|truth|idea|is the)\b",
    r"\bmatters (most|more|deeply)?\b.*\.$",
    r"^each of (those|these|them)\b", r"^all of (this|that)\b", r"^in other words\b", r"^the point is\b",
    r"^simply put\b", r"^in short\b", r"\bthe answer is\b", r"^(and )?that is (why|the|what|how)\b",
    r"^this is (why|the|what|how)\b", r"\bis no accident\b", r"\bit is no wonder\b",
]
SIGNPOST = [
    r"^so let us\b", r"^let us\b", r"^now (think|listen|picture|imagine|consider|look|notice|hold)\b",
    r"^(hold|keep|picture|imagine|notice|consider|remember) (those|that|this|these|it|the)\b",
    r"\bkeep (that|this) (word|picture|in mind)\b", r"\bwe will (need|come back|return|see)\b",
    r"^that leads (us )?to\b", r"^which brings us\b", r"^here is\b", r"^so hold\b",
]
MAXIM = [
    r", and it is\.$", r"\bthe (\w+) that (\w+) and the (\w+) that (\w+)\b",
    r"^(you are|we are) the\b.*\bthat\b", r"\bstrong enough to matter\b", r"\bno one can take\b",
    r"\bbefore you had done anything\b", r"\bmore than (just|a|an)\b",
]

def sentences(par):
    par = re.sub(r"\s+", " ", par.strip())
    parts = re.split(r'(?<=[.!?])["”’]?\s+(?=["“‘]?[A-Z])', par)
    return [p.strip() for p in parts if p.strip()]

def words(s): return len(re.findall(r"[A-Za-z0-9'’]+", s))

def main():
    path = sys.argv[1]
    text = open(path, encoding="utf-8").read()
    lines = text.split("\n", 1)
    body = lines[1] if lines[0].startswith("Episode") and len(lines) > 1 else text
    paras = [p for p in re.split(r"\n\s*\n", body) if p.strip()]
    W = words(body)
    flags = []
    n_short = 0; n_sent = 0; lens = []
    for pi, par in enumerate(paras):
        ss = sentences(par)
        opened = 0  # quotation marks seen so far in this paragraph: odd means we are inside a quote
        for si, s in enumerate(ss):
            inside = opened % 2 == 1
            opened += s.count('"') + s.count('“') + s.count('”')
            n_sent += 1
            w = words(s); lens.append(w)
            low = s.lower().strip('"“”‘’ ')
            quote = inside or s.lstrip().startswith(('"', '“'))
            if w < 8 and not quote: n_short += 1; flags.append(("SHORT", s))
            if w > 38 and not quote: flags.append(("LONG", s))
            if si > 0 and w < 10 and words(ss[si - 1]) < 10 and not quote:
                flags.append(("SHORT-RUN", ss[si - 1] + " | " + s))
            if si == len(ss) - 1 and w < 12 and len(ss) > 1 and not quote and not low.startswith("the next episode"):
                flags.append(("CLOSER", s))
            for pat in SUMMARY:
                if not quote and re.search(pat, low): flags.append(("SUMMARY", s)); break
            for pat in SIGNPOST:
                if not quote and re.search(pat, low): flags.append(("SIGNPOST", s)); break
            for pat in MAXIM:
                if not quote and re.search(pat, low): flags.append(("MAXIM", s)); break
    show = "--all" in sys.argv
    kinds = {}
    for k, s in flags:
        kinds[k] = kinds.get(k, 0) + 1
        print(f"{k:9s} {s}")
    avg = sum(lens) / max(1, len(lens))
    limit_short = max(1, W // 400)
    ok = (kinds.get("SHORT-RUN", 0) == 0 and n_short <= limit_short and kinds.get("SUMMARY", 0) == 0
          and kinds.get("SIGNPOST", 0) == 0 and kinds.get("MAXIM", 0) == 0 and kinds.get("CLOSER", 0) <= 2)
    print(f"\n{W} words, {n_sent} sentences, average {avg:.1f} words per sentence")
    print(f"short sentences (<8 words, not quotes): {n_short} (limit {limit_short})")
    print(f"LONG (over 38 words, hard to follow by ear; for the reviewer): {kinds.get('LONG', 0)}")
    for k in ["SHORT-RUN", "CLOSER", "SUMMARY", "SIGNPOST", "MAXIM"]:
        lim = {"CLOSER": 2}.get(k, 0)
        print(f"{k}: {kinds.get(k, 0)} (limit {lim})")
    print("RESULT:", "PASS" if ok else "FIX")
    sys.exit(0 if ok else 1)

main()
