import math
import sys

from PIL import Image
from array import array

ANSWER = (53, 131)

def get_pixel(obj, c, r):
  #pixel_a = img_a[pos_a[0] + c, pos_a[1] + r][:3]
  #pixel_b = img_b.getpixel((pos_b[0] + c, pos_b[1] + r))
  #start = obj["height"] * 4 * r + c * 4
  #return (obj["arr"])[start:start+4]
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
      #print nm
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

  #img_subequal(h, ANSWER, n, (0, 0), n_width, n_height)

  for r in range(0, h_height - n_height + 1):
    for c in range(0, h_width - n_width + 1):
      if img_subequal(haystack, (c, r), needle, (0, 0), n_width, n_height):
        return (c, r)
  return (-1, -1)

def digit_crop(screen, left, top):
  return screen.crop((left, top, left + DIGIT_WIDTH, top + DIGIT_HEIGHT))

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
    #print "TEMPLATE ANALYSIS START:", x
    print x, img_distance(haystack, (left, 0), template["pix"], (0, 0), tsize[0], tsize[1])

if __name__ == "__main__":
  DIGIT_WIDTH = 18
  DIGIT_HEIGHT = 16

  OFFSET_HEIGHT = 20

  GRID_SIDE = 30

  LEFT_FROM_ANCHOR = 306
  #TOP_FROM_ANCHOR = 73
  TOP_FROM_ANCHOR = 90

  # TODO: Convert Image object into a fast pixelaccess object with size and width
  screen = Image.open("example_screen2.png")
  screen = screen.convert("RGBA")
  screen_pix = screen.load()

  anchor = Image.open("pixelo_anchor.png")
  anchor_pix = anchor.load()

  templates = load_templates()

  apos = img_indexof(screen_pix, screen.size, anchor_pix, anchor.size)
  bpos = (apos[0] + LEFT_FROM_ANCHOR, apos[1] + TOP_FROM_ANCHOR)
  cpos = (apos[0] + LEFT_FROM_ANCHOR + GRID_SIDE, apos[1] + TOP_FROM_ANCHOR)

  # This is a 3
  crop = digit_crop(screen, bpos[0], bpos[1])
  crop_pix = crop.load()
  crop.show()
  template_analysis(crop_pix, crop.size, templates)

  # This is a 5
  #porc = digit_crop(screen, cpos[0], cpos[1])
  #porc_pix = porc.load()
  #template_analysis(porc_pix, porc.size, templates)

  print "=============================================="

  hc = Image.open("mc.png")
  hc_pix = hc.load()
  template_analysis(hc_pix, hc.size, templates)
