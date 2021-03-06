import math
import sys

from PIL import Image
from array import array
from faster_image import FasterImage

LEFT_FROM_ANCHOR = 11
TOP_FROM_ANCHOR = -20

# TODO: Naming difference between "logical" widths (rows) and "pixel" widths
ROW_HEIGHT = 18

DIGIT_WIDTH = 18
DIGIT_HEIGHT = 16

BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)

MAX_NUMBERS = 16
MAX_CLUES = 8

GRID_WIDTH = 25

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

def sliding_window(screen, start_col, start_row, templates, clue_type = "column"):
  iter_col = start_col

  answers = None

  if clue_type == "column":
    answers = [ 0 ] * 15
    slide_distance = 450
  else:
    answers = []
    slide_distance = 450

  while iter_col < start_col + slide_distance:
    crop = digit_crop(screen, iter_col, start_row)
    enhance_digit(crop)
    answer = template_analysis2(crop, templates)

    if answer != None:
      # This is wrong. We do this because our vision isn't general enough
      if clue_type == "column":
        space_num = (iter_col - start_col) / 29
        answers[space_num] = answer
      else:
        answers.append(answer)

      screen.putpixel(iter_col, start_row, (255, 0, 0, 255))
      iter_col += 18 # TODO: Constant

    iter_col += 1

  return answers

def do_vision(screen):
  def trim_clue(clue):
    idx = len(clue) - 1
    for i in range(0, len(clue)):
      if clue[i] != 0:
        idx = i
        break

    return clue[idx:]

  templates = load_templates()

  anchor = FasterImage(Image.open("pixelo_anchor_3.png"))
  anchor_pos = img_indexof(screen, anchor)
  if anchor_pos == (-1, -1):
    return {}

  tophints_start = (anchor_pos[0], anchor_pos[1] + TOP_FROM_ANCHOR)

  # Identify column clues
  column_clues_scanlines = []
  for i in range(0, MAX_CLUES):
    scanline = sliding_window(screen, tophints_start[0], tophints_start[1] - i * 18, templates)
    column_clues_scanlines.append(scanline)

  column_clues = []
  for i in range(0, 15):
    column_clue = [ column_clues_scanlines[j][i] for j in range(0, MAX_CLUES) ]
    column_clue.reverse()
    column_clues.append(trim_clue(column_clue))

  row_clues = []
  for i in range(0, 15):
    row_clue = sliding_window(screen, anchor_pos[0] - 150, anchor_pos[1] + 12 + 30 * i, templates, "row")
    row_clues.append(row_clue)

  return {
    "columns": column_clues,
    "rows": row_clues
  }

if __name__ == "__main__":
  FULL_RUN = True


  if FULL_RUN:
    screen = FasterImage(Image.open("example_screen2.png").convert("RGBA"))
    clues = do_vision(screen)
  else:
    templates = load_templates()
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
