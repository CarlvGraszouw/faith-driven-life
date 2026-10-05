"""Test fixtures for the engine (run from anywhere):
  v2-format.svg     - synthetic scene in the exact STYLE-V2 format (paths only; line/detail/hatch; accent)
  v2-fat-style.svg  - same paths, fat widths in its own <style> (proves per-file widths on one board)
  placeholder-c11.svg - reference/c11-v2.svg minus its background <rect> (stand-in for missing art)"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
EP1 = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, EP1)
from lib_v2 import L, D, H, svg, circle, ellipse, smooth, hatch_lines, check_paths, STYLE, CLOAK, GOLD

b = ''
# coin with a white occlusion fill, beaded rim (detail), relief (line), hatched shadow side
b += L(circle(560, 400, 230), fill='#ffffff')
b += D(circle(560, 400, 205))
b += ''.join(D(circle(560 + 218 * __import__('math').cos(a / 10), 400 + 218 * __import__('math').sin(a / 10), 4)) for a in range(0, 63, 3))
b += L(smooth([(470, 520), (480, 430), (520, 360), (590, 320), (640, 350), (650, 420), (620, 470), (600, 540)]))
b += D(smooth([(560, 380), (585, 395), (600, 420)]) + ' ' + smooth([(530, 440), (560, 455), (590, 450)]))
b += H(hatch_lines(640, 300, 700, 360, 14, dx=-6, dy=10))
# cloak-coloured accent shape (stroked line + multiply fill), sits over the coin edge
b += L('M 900 250 C 960 220 1050 230 1100 270 L 1160 560 C 1080 600 960 600 880 560 Z', fill=CLOAK, accent=True)
b += D('M 930 300 C 960 380 970 470 960 560 M 1010 290 C 1030 380 1040 470 1040 580 M 1080 300 C 1100 380 1110 470 1120 570')
b += H(hatch_lines(1105, 330, 1150, 540, 9, dx=5, dy=4))
# ground shadow, cross-hatch
b += H(hatch_lines(380, 660, 760, 660, 6, dy=8))
b += H(hatch_lines(420, 650, 470, 700, 12, dx=28))
txt = svg(b, 'engine test fixture: v2 format')
print('v2-format line/detail/hatch =', check_paths(txt))
open(os.path.join(HERE, 'v2-format.svg'), 'w').write(txt)
fat = txt.replace('stroke-width:2.6', 'stroke-width:9').replace('stroke-width:1.5', 'stroke-width:5').replace('stroke-width:0.9', 'stroke-width:3')
open(os.path.join(HERE, 'v2-fat-style.svg'), 'w').write(fat)
ref = open(os.path.join(EP1, 'reference', 'c11-v2.svg')).read()
ref = re.sub(r'\s*<rect width="1600" height="900" fill="#fff"/>', '', ref)
open(os.path.join(HERE, 'placeholder-c11.svg'), 'w').write(ref.replace('<!-- c11 v2:', '<!-- PLACEHOLDER (reference c11-v2, background rect removed):', 1))
print('wrote fixtures to', HERE)
