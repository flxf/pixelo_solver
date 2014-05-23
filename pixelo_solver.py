import math
import sys

from PIL import Image
from array import array

ANSWER = (53, 131)
DIGIT_WIDTH = 18
DIGIT_HEIGHT = 16

BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)

class FasterImage:
  def __init__(self, image):
    self.image = image
    self.image_pix = image.load()

  def size(self):
    return self.image.size

  def getpixel(self, c, r):
    return self.image_pix[c, r]

  def putpixel(self, c, r, v):
    self.image_pix[c, r] = v

  def crop(self, limits):
    c = self.image.crop(limits)
    return FasterImage(c)

  def show(self):
    self.image.show()

def norm2(pixel_a, pixel_b):
  return math.sqrt(sum((pixel_a[i] - pixel_b[i]) ** 2 for i in range(0, 3)))

def img_distance(img_a, pos_a, img_b, pos_b, width, height):
  err = 0
  pixels = 0

  for c in range(0, width):
    for r in range(0, height):
      pixel_a = img_a.getpixel(pos_a[0] + c, pos_a[1] + r)
      pixel_b = img_b.getpixel(pos_b[0] + c, pos_b[1] + r)

      # Treat transparent pixels as white
      if pixel_b[3] == 0:
        nm = norm2(pixel_a, WHITE)
      else:
        nm = norm2(pixel_a, pixel_b)

      pixels += 1
      err += nm

  return err / pixels

def img_subequal(img_a, pos_a, img_b, pos_b, width, height):
  for c in range(0, width):
    for r in range(0, height):
      pixel_a = img_a.getpixel(pos_a[0] + c, pos_a[1] + r)
      pixel_b = img_b.getpixel(pos_b[0] + c, pos_b[1] + r)

      # TODO: This is a hack for how our algorithm works
      # Ignore transparent pixels
      if pixel_b[3] == 0:
        continue

      if pixel_a != pixel_b:
        return False
  return True

def img_indexof(haystack, needle):
  h_width, h_height = haystack.size()
  n_width, n_height = needle.size()

  for c in range(0, h_width - n_width + 1):
    for r in range(0, h_height - n_height + 1):
      if img_subequal(haystack, (c, r), needle, (0, 0), n_width, n_height):
        return (c, r)
  return (-1, -1)

def digit_crop(screen, left, top):
  return screen.crop((left, top, left + DIGIT_WIDTH, top + DIGIT_HEIGHT))

def luminance(pixel):
  r, g, b, a = [ component / 255.0 for component in pixel ]
  #return 0.2126 * (pixel[0] / 255.0) + 0.7152 * (pixel[1] / 255.0) + 0.0722 * (pixel[2] / 255.0)
  return 0.2126 * r + 0.7152 * g + 0.0722 * b

def enhance_digit(crop):
  for r in range(0, DIGIT_HEIGHT):
    darkest = min([ luminance(crop.getpixel(c, r)) for c in range(0, DIGIT_WIDTH) ])

    for c in range(0, DIGIT_WIDTH):
      if abs(luminance(crop.getpixel(c, r)) - darkest) < 0.1:
        crop.putpixel(c, r, BLACK)
      else:
        crop.putpixel(c, r, WHITE)

def load_templates():
  templates = [ None ] + [ FasterImage(Image.open("numbers/%d.png" % (x))) for x in range(1, 10) ]
  return templates

def template_analysis(haystack, templates):
  h_width, h_height = haystack.size()

  distances = []

  for x in range(1, 10):
    template = templates[x]
    tsize = template.size()
    left = (h_width - tsize[0]) / 2
    #print x, img_distance(haystack, (left, 0), template, (0, 0), tsize[0], tsize[1])

if __name__ == "__main__":
  OFFSET_HEIGHT = 20

  GRID_SIDE = 30

  LEFT_FROM_ANCHOR = 11
  TOP_FROM_ANCHOR = -20

  # TODO: Convert Image object into a fast pixelaccess object with size and width
  screen = FasterImage(Image.open("example_screen2.png").convert("RGBA"))
  anchor = FasterImage(Image.open("pixelo_anchor_3.png"))

  templates = load_templates()

  #apos = img_indexof(screen_pix, screen.size, anchor_pix, anchor.size)
  apos = img_indexof(screen, anchor)
  print apos
  #bpos = (apos[0] + LEFT_FROM_ANCHOR, apos[1] + TOP_FROM_ANCHOR)
  #cpos = (apos[0] + LEFT_FROM_ANCHOR + 2 * GRID_SIDE - 1, apos[1] + TOP_FROM_ANCHOR)

  ### This is a 9
  #crop = digit_crop(screen, cpos[0], cpos[1])
  #crop_pix = crop.load()
  #enhance_digit(crop_pix)
  #template_analysis(crop_pix, crop.size, templates)

  hc = FasterImage(Image.open("hc.png"))
  enhance_digit(hc)
  hc.show()
  template_analysis(hc, templates)
