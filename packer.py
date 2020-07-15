import sys
import os
from PIL import Image

path = sys.argv[1]
images = []

with os.scandir(path) as it:
    for entry in it:
        if entry.is_file:
            i = Image.open(entry.path)
            images.append(i)
            print("Found image:", entry.path)

images.sort(key=lambda i : i.height, reverse=True)
min_width = images[-1].width
min_height = images[-1].height

class CanvasNode():
    def __init__(self, x, y, w, h, image=None):
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.image = image

    @property
    def area(self):
        return self.width * self.height

    def __str__(self):
        return f'[{self.x}, {self.y}, {self.area}]'

class Canvas():
    def __init__(self, w, h):
        self.width = w
        self.height = h
        self.nodes = []
        self.nodes.append(CanvasNode(0, 0, w, h))

    def defragment(self):
        for n in self.nodes:
            if (n.area == 0):
                self.nodes.remove(n)

        ''' This code doesn't work right now...
        can_coalesce = True
        while can_coalesce:
            can_coalesce = False
            for i in range(len(self.nodes) - 1, 0, -1):
                n = self.nodes[i]
                for j in range(len(self.nodes) - 1, 0, -1):
                    on = self.nodes[j]
                    if n != on and n.image == None and on.image == None:
                        if abs(n.x - on.x) < min_width and n.x + n.width == on.x + on.width:
                            newnode = CanvasNode(max(n.x, on.x), min(n.y, on.y), min(n.width, on.width), n.height + on.height)
                            self.nodes.remove(n)
                            self.nodes.remove(on)
                            self.nodes.append(newnode)
                            can_coalesce = True
                            break
        '''
        self.nodes.sort(key=lambda a : a.area)

    def add_image(self, image):
        for n in self.nodes:
            if n.image == None and n.width >= image.width and n.height >= image.height:
                newnode = CanvasNode(n.x, n.y, image.width, image.height, image)
                left = CanvasNode(n.x + image.width, n.y, n.width - image.width, image.height)
                bot = CanvasNode(n.x, n.y + image.height, n.width, n.height - image.height)
                self.nodes.remove(n) # this should be okay bc returning anyways
                self.nodes.extend([newnode, left, bot])
                self.defragment()
                return True
        return False

    def get_result(self):
        result = Image.new("RGBA", (self.width, self.height))
        for n in self.nodes:
            if n.image != None:
                result.paste(n.image, (n.x, n.y))
        return result

    def __str__(self):
        res = ""
        for n in self.nodes:
            res += str(n)
        return res;

canvas_size = 128
success = False

while (not success):
    success = True
    canvas = Canvas(canvas_size, canvas_size);
    for img in images:
        if not canvas.add_image(img):
            success = False
            canvas_size *= 2
            break
    if success:
        canvas.get_result().save("result.png")
        print("Sprite sheet successfully generated!")
        break

