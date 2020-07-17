import sys
import os
import json
from PIL import Image

def print_help():
    print("Usage: python pypacker.py <PATH_TO_IMAGE_FOLDER> <OPTIONAL PARAMS>\n")
    print("Availiable parameters:")
    print("\t--help: open this dialogue")
    print("\t--output <PATH_TO_DIR>: set folder to output to, must be an existing directory")
    print("\t--filename <NAME>: set filename of output (ex. filename.png, filename.json)")
    print("\t--border <INT>: set space between each sprite.")
    print("\t--notrim: if used, transparent padding will not be trimmed. Can be useful if the script is too slow.")

try:
    path = sys.argv[1]
except:
    print_help()
    exit()
outpath = ""
filename = "result.png"
images = []
border = 0
trim = True

try:
    if not os.path.isdir(path):
        if path == "--help" or path == "-h":
            print_help()
        else:
            print("Invalid image folder path!")
        exit()
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--output" or arg == "-o":
            outpath = sys.argv[i + 1]
            i += 1
            if not os.path.isdir(outpath):
                print("Invalid output folder path!")
                exit()
            if outpath[-1] != "/":
                if os.name == "nt":
                    if outpath[-1] != "\\":
                        outpath += "\\"
                else:
                    outpath += "/"
        elif arg == "--filename" or arg == "-f":
            filename = sys.argv[i + 1]
            i += 1
        elif arg == "--border" or arg == "-b":
            try:
                border = int(sys.argv[i + 1])
                i += 1
            except:
                print("Invalid border parameter!")
                exit()
        elif arg == "--notrim" or arg == "-nt":
            trim = False
        else:
            raise ValueError
        i += 1
except:
    print("Invalid parameters! Use --help for usage info!")
    exit()

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
                result[name] = {"x" : n.x, "y" : n.y, "width" : n.width - border, "height" : n.height - border}
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
            if trim:
                images.append((trimmed(i), name))
            else:
                images.append((i, name))

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
        try:
            canvas.get_result().save(outpath + filename + ".png")
            print("Saved sprite sheet at", outpath + filename + ".png!")
            with open(outpath + filename + ".json", "w") as json_file:
                json_file.write(canvas.get_json())
            print("Saved json file at", outpath + filename + ".json!")
            break
        except:
            print("ERROR: Could not save sprite sheet/json! Please ensure all parameters are valid and try again!")
            exit()
