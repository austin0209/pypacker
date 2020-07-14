import sys
import os
from PIL import Image

class CanvasNode():
    def __init__(self, x, y, w, h, image=None):
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.image = image

class Canvas():
    def __init__(self, w, h):
        self.width = w
        self.height = h
        nodes = []
        nodes.append(CanvasNode(0, 0, w, h))

    def add_image(self, image):
        

path = sys.argv[1]

images = []
canvas = Image.new("RGB", (1280, 720));

with os.scandir(path) as it:
    for entry in it:
        if entry.is_file:
            i = Image.open(entry.path))
            images.append(i)
            print("Found image: ", entry.path)

off = 0
for i in range(0, len(images)):
    canvas.paste(images[i], (off, 0))
    off += images[i].width

canvas.save("test.png")
