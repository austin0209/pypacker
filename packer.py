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
        self.nodes = []
        self.nodes.append(CanvasNode(0, 0, w, h))

    def defragment(self):
        # TODO: coalesce nodes here!
        for n in self.nodes:
            if (n.get_area() == 0):
                n.remove(n)

    def add_image(self, image):
        for n in self.nodes:
            if n.image == None and n.width >= image.width and n.height >= image.height:
                newnode = CanvasNode(n.x, n.y, image.width, image.height, image)
                left = CanvasNode(n.x + image.width, n.y, n.width - image.width, image.height)
                bot = CanvasNode(n.x, n.y + image.height, n.width, n.height - image.height)
                self.nodes.remove(n) # this should be okay bc returning anyways
                self.nodes.extend([newnode, left, bot])
                self.defragment()
                self.nodes.sort(key=lambda a : a.y * self.width + a.x, reverse=True)
                return
        assert(False)

    def get_result(self):
        result = Image.new("RGBA", (self.width, self.height))
        for n in self.nodes:
            if n.image != None:
                result.paste(n.image, (n.x, n.y))
        return result

path = sys.argv[1]

canvas = Canvas(1280, 720);
images = []
result = Image.new("RGBA", (1280, 720));

with os.scandir(path) as it:
    for entry in it:
        if entry.is_file:
            i = Image.open(entry.path)
            images.append(i)
            print("Found image: ", entry.path)

for img in sorted(images, key=lambda i : i.width * i.height, reverse=True):
    canvas.add_image(img)

canvas.get_result().save("result.png")
