"""Render an art SVG to PNG on the board colour, 1920 wide.  usage: render_still.py in.svg out.png [width]"""
import sys, cairosvg, io
from PIL import Image
w = int(sys.argv[3]) if len(sys.argv) > 3 else 1920
png = cairosvg.svg2png(url=sys.argv[1], output_width=w)
im = Image.open(io.BytesIO(png)).convert("RGBA")
bg = Image.new("RGBA", im.size, "#fbfaf7"); bg.alpha_composite(im); bg.convert("RGB").save(sys.argv[2])
