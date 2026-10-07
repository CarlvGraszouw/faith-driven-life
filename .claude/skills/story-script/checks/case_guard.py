"""Check that a corrected file differs from the original ONLY in upper/lower case, and list each change.
    python3 case_guard.py <original> <corrected>
Exit 0 when only case changed. Used for Carl's rule (4 Oct): every pronoun and title for God and Jesus
is capitalised (He, Him, His, Himself, Me, My, Mine, You, Your, Yours, King, Father...)."""
import re, sys
a = open(sys.argv[1], encoding="utf-8").read(); b = open(sys.argv[2], encoding="utf-8").read()
if a.lower() != b.lower() or len(a) != len(b):
    print("FAIL: more than letter case changed"); sys.exit(1)
n = 0
for m in re.finditer(r"[A-Za-z’']+", b):
    w0 = a[m.start():m.end()]
    if w0 != m.group():
        n += 1
        ctx = b[max(0, m.start() - 50):m.end() + 30].replace("\n", " ")
        print(f"{w0:>9} -> {m.group():<9} …{ctx}…")
print(f"{n} words changed, nothing else"); sys.exit(0)
