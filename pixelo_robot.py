import os
import tempfile
import pixelo_vision

from pymouse import PyMouse
from pykeyboard import PyKeyboard

from PIL import Image
from faster_image import FasterImage

if __name__ == "__main__":
  m = PyMouse()
  k = PyKeyboard()

  #f = tempfile.NamedTemporaryFile() # TODO: File not being created
  #os.system("screencapture %s" % (f.name))

  screenfile = "tmp/screen.png"
  os.system("screencapture %s" % (screenfile))

  screen = FasterImage(Image.open(screenfile).convert("RGBA"))
  clues = pixelo_vision.do_vision(screen)
  print clues

  #k.type_string("Hello world")
