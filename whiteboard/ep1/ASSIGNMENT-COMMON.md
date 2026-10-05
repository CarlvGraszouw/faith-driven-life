# Common brief for art agents (Episode 1, first 2 minutes, v2 art)

You are a brilliant illustrator redrawing scenes for a narrated whiteboard video
("A Faith Driven Life — Episode 1: What a Kingdom Actually Was"). The owner's verdict on v1:
lines too thick, detail missing, depictions bad. v2 must look like a top whiteboard-animation
studio drew it: rich, accurate, expressive, telling the story. READ `STYLE-V2.md` FIRST and follow
it exactly (format rules are hard requirements — the renderer animates each path).

Working dir: /home/user/faith-driven-life/whiteboard/ep1  (lib_v2.py, render_still.py, STYLE-V2.md)
Write each scene as a Python generator `art-v2/gen/<scene>.py` that writes `art-v2/<batch>/<file>.svg`
via lib_v2.write() (it validates the format). Keep filenames exactly as listed.

Context in Google Drive (load tools via ToolSearch "select:mcp__Google_Drive__download_file_content,mcp__Google_Drive__search_files";
download returns base64 — save and `base64 -d` with Bash; never print big files into your context):
- SCENE-PLAN.md (narration per scene + intent): fileId 1fh8pT5mDoVI-v-iGWDLuR3P04tvufW_D — read only your scenes' sections (grep).
- Original v1 SVGs for composition reference: folder A = parentId '1zdBVhPL0wqMzXHyMLEk3ilzyS1RDDNRY',
  folder B = parentId '1O--RPnRysLS7NwzBGIIOCod-bqNqepAG' (search_files with query parentId = '...').
  v1 used <use> of a kit you don't have — that's fine; just look at the paths for layout. Do NOT copy v1 figures.
- Multi-part scenes: part a is drawn first, then b is drawn ON THE SAME BOARD at the given time, etc.
  Later parts add to the picture; plan the whole composition so all parts fit together and the
  regions reserved for on-screen words stay empty.

Process per scene (iterate — quality is the whole point):
1. Read the narration for the scene; decide what single image best tells that moment.
2. Write the generator, render: `python3 render_still.py art-v2/<batch>/<file>.svg /tmp/<file>.png`
   (for multi-part scenes also render a composite of all parts: concatenate bodies into one temp svg).
3. LOOK at the PNG with the Read tool. Critique like a demanding art director: anatomy, faces,
   hands, drapery, perspective, historical accuracy, composition, readability at 1080p, empty word
   zones, nothing cramped or childish. Zoom crops to check faces/hands (render at 3840 wide and crop with PIL).
4. Improve. Minimum 3 rounds per scene; stop only when it's genuinely excellent.

Jesus (same everywhere): Jewish man about 30, dark centre-parted hair to the shoulders, full short
beard, calm direct gaze; cream tunic, mantle over the left shoulder with tassels at its corners,
sandals. Give his mantle the CLOAK accent (#c98a6a, multiply) so he's easy to find in crowds.
Coins: silver (no fill or very light BLUE), the one gold accent goes elsewhere.

Final reply (under 200 words): files written, path counts per file, which stills you checked,
and anything you're unsure about. Do not git commit.
