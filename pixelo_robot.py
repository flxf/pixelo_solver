import os
import pixelo_vision
import subprocess
import tempfile
import time

from pymouse import PyMouse
from pykeyboard import PyKeyboard

from PIL import Image
from faster_image import FasterImage

CLUE_TMPFILE = "tmp/clues.non"

def format_clues(clues):
  lines = []

  width = len(clues["columns"])
  height = len(clues["rows"])

  lines.append("width %d" % (width))
  lines.append("height %d" % (height))

  lines.append("rows")
  for row in clues["rows"]:
    lines.append(",".join([ str(d) for d in row ]))

  lines.append("columns")
  for column in clues["columns"]:
    lines.append(",".join([ str(d) for d in column ]))

  return "\n".join(lines)

def parse_pbnsolution(solution):
  lines = solution.split("\n")
  lines = lines[1:-1] # First line says "UNIQUE BLAH". Last line is blank
  return lines

def play_solution(solution):
  k = PyKeyboard()

  for row in solution:
    for c in row:
      if c == 'X':
        k.tap_key("space")
      elif c == '.':
        pass
      else:
        raise Exception

      k.tap_key("rightarrow")

    k.tap_key("downarrow")
    for _ in range(0, len(row)):
      k.tap_key("leftarrow")

if __name__ == "__main__":

  #f = tempfile.NamedTemporaryFile() # TODO: File not being created
  #os.system("screencapture %s" % (f.name))

  screenfile = "tmp/screen.png"
  os.system("screencapture %s" % (screenfile))

  print "screen captured..."

  screen = FasterImage(Image.open(screenfile).convert("RGBA"))
  clues = pixelo_vision.do_vision(screen)

  print "vision completed..."

  formatted_clues = format_clues(clues)
  with open(CLUE_TMPFILE, "w") as f:
    f.write(formatted_clues)

  # TODO: ./pbnsolve is not very robust
  pbnsolver_output = subprocess.check_output(["./pbnsolve", CLUE_TMPFILE])
  print pbnsolver_output

  pbnsolution = parse_pbnsolution(pbnsolver_output)

  print "problem solved..."

  play_solution(pbnsolution)

  print "complete!"
