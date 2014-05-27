import math
import sys

from PIL import Image
from array import array

LEFT_FROM_ANCHOR = 11
TOP_FROM_ANCHOR = -20

ROW_HEIGHT = 18

DIGIT_WIDTH = 18
DIGIT_HEIGHT = 16

BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)

MAX_NUMBERS = 14

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
  if pixel_a == pixel_b:
    return 0
  return 1
  #return math.sqrt(sum((pixel_a[i] - pixel_b[i]) ** 2 for i in range(0, 3)))

def img_distance(img_a, pos_a, img_b, pos_b, width, height):
  err = 0

  for c in range(0, width):
    for r in range(0, height):
      pixel_a = img_a.getpixel(pos_a[0] + c, pos_a[1] + r)
      pixel_b = img_b.getpixel(pos_b[0] + c, pos_b[1] + r)

      # Treat transparent pixels as white
      if pixel_b[3] == 0:
        nm = norm2(pixel_a, WHITE)
      else:
        nm = norm2(pixel_a, BLACK)

      err += nm

  return err

def img_within(img_a, pos_a, img_b, pos_b, width, height, threshold):
  err = 0

  for c in range(0, width):
    for r in range(0, height):
      pixel_a = img_a.getpixel(pos_a[0] + c, pos_a[1] + r)
      pixel_b = img_b.getpixel(pos_b[0] + c, pos_b[1] + r)

      # Treat transparent pixels as white
      if pixel_b[3] == 0:
        nm = norm2(pixel_a, WHITE)
      else:
        nm = norm2(pixel_a, BLACK)

      err += nm

      if (err > threshold):
        return False

  return True

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
  templates = [ FasterImage(Image.open("numbers/%d.png" % (x))) for x in range(0, MAX_NUMBERS) ]
  return templates

def template_analysis1(haystack, templates):
  h_width, h_height = haystack.size()

  distances = []

  for x in range(0, MAX_NUMBERS):
    template = templates[x]
    tsize = template.size()
    left = (h_width - tsize[0]) / 2
    distances.append((img_distance(haystack, (left, 0), template, (0, 0), tsize[0], tsize[1]), x))

  min_distance, digit = min(distances)
  if min_distance <= 12:
    return digit
  return None

def template_analysis2(haystack, templates):
  h_width, h_height = haystack.size()

  for x in range(1, MAX_NUMBERS):
    template = templates[x]
    tsize = template.size()
    left = (h_width - tsize[0]) / 2

    if img_within(haystack, (left, 0), template, (0, 0), tsize[0], tsize[1], 12):
      return x

  return None

def sliding_window(screen, start_col, start_row):
  #start_col, start_row = start_pos
  iter_col = start_col

  answers = [ 0 ] * 15

  while iter_col < start_col + 450:
    crop = digit_crop(screen, iter_col, start_row)
    enhance_digit(crop)
    answer = template_analysis2(crop, templates)

    if answer != None:
      space_num = (iter_col - start_col) / 29
      answers[space_num] = answer

      screen.putpixel(iter_col, start_row, (255, 0, 0, 255))
      iter_col += GRID_SIDE

    iter_col += 1

  return answers

if __name__ == "__main__":
  OFFSET_HEIGHT = 20

  GRID_SIDE = 25

  FULL_RUN = True

  templates = load_templates()

  if FULL_RUN:
    # TODO: Convert Image object into a fast pixelaccess object with size and width
    screen = FasterImage(Image.open("example_screen2.png").convert("RGBA"))
    anchor = FasterImage(Image.open("pixelo_anchor_3.png"))

    anchor_pos = img_indexof(screen, anchor)
    tophints_start = (anchor_pos[0], anchor_pos[1] + TOP_FROM_ANCHOR)

    for i in range(0, 8):
      print sliding_window(screen, tophints_start[0], tophints_start[1] - i * 18)

    screen.show()
  else:
    #screen = FasterImage(Image.open("example_screen2.png").convert("RGBA"))
    #anchor = FasterImage(Image.open("pixelo_anchor_3.png"))

    #position = (359, 219)
    #crop = digit_crop(screen, position[0], position[1])
    #enhance_digit(crop)
    #crop.show()

    #template_analysis(crop, templates)

    hc = FasterImage(Image.open("vision_tests/hc.png"))
    enhance_digit(hc)
    hc.show()
    print template_analysis(hc, templates)
