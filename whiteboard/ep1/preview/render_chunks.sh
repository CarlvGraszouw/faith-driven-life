#!/usr/bin/env bash
# Render a timeline in frame-aligned chunks (two at a time), each with a watchdog and one retry,
# then join them losslessly. A single long render can stall in headless Chrome; chunks avoid that.
#   usage: preview/render_chunks.sh <timeline.json> <out.mp4> <end-seconds> [chunk-seconds]
# Chunk boundaries are multiples of chunk-seconds (default 32 s = 960 frames at 30 fps), so the
# frames are exactly the ones a single render would produce.
set -euo pipefail
TL=$(realpath "$1"); OUT=$(realpath -m "$2"); END=$3; STEP=${4:-32}
ENGINE=$(cd "$(dirname "$0")/../engine" && pwd)
WORK=$(mktemp -d); trap 'rm -rf "$WORK"' EXIT

starts=(); t=0
while awk "BEGIN{exit !($t < $END)}"; do starts+=("$t"); t=$(awk "BEGIN{print $t + $STEP}"); done

render_one() {  # $1 = chunk index
  local i=$1 from=${starts[$1]} to
  to=$(awk "BEGIN{t=$from + $STEP; print (t < $END ? t : $END)}")
  for attempt in 1 2; do
    if (cd "$ENGINE" && timeout 900 node render.js "$TL" "$WORK/part-$i.mp4" --from "$from" --to "$to" > "$WORK/part-$i.log" 2>&1); then
      echo "chunk $i ($from-$to s) done"; return 0
    fi
    echo "chunk $i ($from-$to s) failed (attempt $attempt): $(tail -c 300 "$WORK/part-$i.log" | tr '\r' '\n' | tail -2)"
  done
  return 1
}

n=${#starts[@]}
for ((i = 0; i < n; i += 2)); do
  render_one "$i" & p1=$!
  if ((i + 1 < n)); then render_one $((i + 1)) & p2=$!; wait "$p2"; fi
  wait "$p1"
done

: > "$WORK/list.txt"
for ((i = 0; i < n; i++)); do echo "file '$WORK/part-$i.mp4'" >> "$WORK/list.txt"; done
ffmpeg -y -hide_banner -loglevel error -f concat -safe 0 -i "$WORK/list.txt" -c copy -movflags +faststart "$OUT"
echo "wrote $OUT ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT") s)"
