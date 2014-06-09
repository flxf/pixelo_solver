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
