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

    def get_area(self):
        return self.width * self.height

class Canvas():
    def __init__(self, w, h):
        self.width = w
        self.height = h
        nodes = []
        nodes.append(CanvasNode(0, 0, w, h))

    def add_image(self, image):
        for CanvasNode n in nodes:
            if n.image == None && n.width >= image.width && n.height >= image.height:
                newnode = CanvasNode(n.x, n.y, image.width, image.height, image)
                left = CanvasNode(n.x + image.width, n.y, n.width - image.width, image.height)
                bot = CanvasNode(n.x, n.y + image.height, n.width, n.height - image.height)

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
