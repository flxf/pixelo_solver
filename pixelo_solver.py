import math
import sys

from PIL import Image
from array import array

ANSWER = (53, 131)
DIGIT_WIDTH = 18
DIGIT_HEIGHT = 16

def get_pixel(obj, c, r):
  return obj[c, r]

def norm2(pixel_a, pixel_b):
  return math.sqrt(sum((pixel_a[i] - pixel_b[i]) ** 2 for i in range(0, 3)))

def img_distance(img_a, pos_a, img_b, pos_b, width, height):
  err = 0
  pixels = 0

  for c in range(0, width):
    for r in range(0, height):
      pixel_a = get_pixel(img_a, pos_a[0] + c, pos_a[1] + r)
      pixel_b = get_pixel(img_b, pos_b[0] + c, pos_b[1] + r)

      # Treat transparent pixels as white
      if pixel_b[3] == 0:
        nm = norm2(pixel_a, (255, 255, 255))
      else:
        nm = norm2(pixel_a, pixel_b)

      pixels += 1
      err += nm

  return err / pixels

def img_subequal(img_a, pos_a, img_b, pos_b, width, height):
  for c in range(0, width):
    for r in range(0, height):
      pixel_a = get_pixel(img_a, pos_a[0] + c, pos_a[1] + r)
      pixel_b = get_pixel(img_b, pos_b[0] + c, pos_b[1] + r)

      # TODO: This is a hack for how our algorithm works
      # Ignore transparent pixels
      if pixel_b[3] == 0:
        continue

      if pixel_a != pixel_b:
        return False
  return True

def img_indexof(haystack, hsize, needle, nsize):
  h_width, h_height = hsize
  n_width, n_height = nsize

  for c in range(0, h_width - n_width + 1):
    for r in range(0, h_height - n_height + 1):
      if img_subequal(haystack, (c, r), needle, (0, 0), n_width, n_height):
        return (c, r)
  return (-1, -1)

def digit_crop(screen, left, top):
  return screen.crop((left, top, left + DIGIT_WIDTH, top + DIGIT_HEIGHT))

def luminance(pixel):
  return 0.2126 * (pixel[0] / 255.0) + 0.7152 * (pixel[1] / 255.0) + 0.0722 * (pixel[2] / 255.0)

def enhance_digit(crop):
  for r in range(0, DIGIT_HEIGHT):
    mn = crop[0, r]
    for c in range(1, DIGIT_WIDTH):
      if luminance(crop[c, r]) < luminance(mn):
        mn = crop[c, r]

    for c in range(0, DIGIT_WIDTH):
      if abs(luminance(crop[c, r]) - luminance(mn)) < 0.1:
        crop[c, r] = (0, 0, 0, 255)
      else:
        crop[c, r] = (255, 255, 255, 255)

    #print mn

def load_templates():
  templates = [ None ]
  for x in range(1, 10):
    im = Image.open("numbers/%d.png" % (x))
    templates.append({
      "size": im.size,
      "pix": im.load()
    })

  return templates

def template_analysis(haystack, hsize, templates):
  h_width, h_height = hsize

  for x in range(1, 10):
    template = templates[x]
    tsize = template["size"]
    left = (h_width - tsize[0]) / 2
    print x, img_distance(haystack, (left, 0), template["pix"], (0, 0), tsize[0], tsize[1])

if __name__ == "__main__":
  OFFSET_HEIGHT = 20

  GRID_SIDE = 30

  LEFT_FROM_ANCHOR = 11
  #TOP_FROM_ANCHOR = 73
  TOP_FROM_ANCHOR = -20

  # TODO: Convert Image object into a fast pixelaccess object with size and width
  screen = Image.open("example_screen2.png")
  screen = screen.convert("RGBA")
  screen_pix = screen.load()

  anchor = Image.open("pixelo_anchor_3.png")
  anchor_pix = anchor.load()

  templates = load_templates()

  apos = img_indexof(screen_pix, screen.size, anchor_pix, anchor.size)
  bpos = (apos[0] + LEFT_FROM_ANCHOR, apos[1] + TOP_FROM_ANCHOR)
  cpos = (apos[0] + LEFT_FROM_ANCHOR + 2 * GRID_SIDE - 1, apos[1] + TOP_FROM_ANCHOR)

  ## This is a 9
  crop = digit_crop(screen, cpos[0], cpos[1])
  crop_pix = crop.load()
  crop.show()
  enhance_digit(crop_pix)
  template_analysis(crop_pix, crop.size, templates)

  hc = Image.open("mc.png")
  hc_pix = hc.load()
  enhance_digit(hc_pix)

  template_analysis(hc_pix, hc.size, templates)
