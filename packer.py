import sys
import os
import json
from PIL import Image

path = sys.argv[1]
images = []
border = 2

def trimmed(img):
    temp = Image.new("RGBA", (img.width, img.height))
    temp.paste(img, (0, 0))

    def get_left():
        for x in range(0, img.width):
            for y in range(0, img.height):
                pix = temp.getchannel("A").getpixel((x, y))
                if pix != 0:
                    return x

    def get_right():
        for x in range(img.width - 1, -1, -1):
            for y in range(0, img.height):
                pix = temp.getchannel("A").getpixel((x, y))
                if pix != 0:
                    return x + 1

    def get_top():
        for y in range(0, img.height):
            for x in range(0, img.width):
                pix = temp.getchannel("A").getpixel((x, y))
                if pix != 0:
                    return y

    def get_bot():
        for y in range(img.height - 1, -1, -1):
            for x in range(0, img.width):
                pix = temp.getchannel("A").getpixel((x, y))
                if pix != 0:
                    return y + 1

    cropped = img.crop((get_left(), get_top(), get_right(), get_bot()))
    temp2 = Image.new("RGBA", (cropped.width + border, cropped.height + border))
    temp2.paste(cropped, (0, 0))
    return temp2


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
        self.nodes.append(CanvasNode(border, border, w - border, h - border))
        self.nodes.append(CanvasNode(0, 0, w, border))
        self.nodes.append(CanvasNode(0, 0, border, h))
        self.defragment()

    def defragment(self):
        for n in self.nodes:
            if (n.area == 0):
                self.nodes.remove(n)

        self.nodes.sort(key=lambda a : a.area)

    def add_image(self, image):
        for n in self.nodes:
            if n.image == None and n.width >= image[0].width and n.height >= image[0].height:
                newnode = CanvasNode(n.x, n.y, image[0].width, image[0].height, image)
                left = CanvasNode(n.x + image[0].width, n.y, n.width - image[0].width, image[0].height)
                bot = CanvasNode(n.x, n.y + image[0].height, n.width, n.height - image[0].height)
                self.nodes.remove(n) # this should be okay bc returning anyways
                self.nodes.extend([newnode, left, bot])
                self.defragment()
                return True
        return False

    def get_result(self):
        result = Image.new("RGBA", (self.width, self.height))
        for n in self.nodes:
            if n.image != None:
                result.paste(n.image[0], (n.x, n.y))
        return result

    def get_json(self):
        result = {}
        for n in self.nodes:
            if n.image != None:
                name = n.image[1]
                result[name] = {"x" : n.x, "y" : n.y, "width" : n.width, "height" : n.height}
        return json.dumps(result, indent=4);

    def __str__(self):
        res = ""
        for n in self.nodes:
            res += str(n)
        return res;


with os.scandir(path) as it:
    for entry in it:
        if entry.is_file:
            i = Image.open(entry.path)
            print("Found image:", entry.path)
            unix_path = entry.path.replace('\\','/')
            name = unix_path.split('/')[-1].split('.')[0]
            images.append((trimmed(i), name))

images.sort(key=lambda i : i[0].height, reverse=True)

canvas_size = 1
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
        with open("result.json", "w") as json_file:
            json_file.write(canvas.get_json())
        print("Sprite sheet and json file successfully generated!")
        break
