import sys
import os
import json
from PIL import Image

def print_help():
    print("usage:  python pypacker.py <path to image folder> [optional params]")
    print("availiable parameters:")
    print("\t{-h --help}:\n\t\topen this dialogue")
    print("\t{-o --output} <path to directory>:\n\t\tset folder to output to, must be an existing directory.\n\t\tdefault: current working directory.")
    print("\t{-f --filename} <name>:\n\t\tset filename of outputs (filename.png, filename.json). do not include the file extension here.\n\t\tdefault: \"result\".")
    print("\t{-b --border} <integer value>:\n\t\tset space between each sprite.\n\t\tdefault: 0")
    print("\t{-nt --notrim}:\n\t\tif used, transparent padding will not be trimmed. can be useful if the script is too slow.")

try:
    path = sys.argv[1]
except:
    print_help()
    exit()
outpath = ""
filename = "result"
images = []
border = 0
trim = True
max_size = 256

if not os.path.isdir(path):
    if path == "--help" or path == "-h":
        print_help()
    else:
        print("Invalid image folder path!")
    exit()

try:
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

    trimRectWidth = get_left()
    trimRectHeight = get_top()
    cropped = img.crop((get_left(), get_top(), get_right(), get_bot()))
    temp2 = Image.new("RGBA", (cropped.width + border, cropped.height + border))
    temp2.paste(cropped, (0, 0))
    return (temp2, trimRectWidth, trimRectHeight)


class CanvasNode():
    def __init__(self, x, y, w, h, idata=None):
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.idata = idata

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

    def add_image(self, idata):
        image = idata[0]
        for n in self.nodes:
            if n.idata == None and n.width >= image.width and n.height >= image.height:
                newnode = CanvasNode(n.x, n.y, image.width, image.height, idata)
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
            if n.idata != None:
                result.paste(n.idata[0], (n.x, n.y))
        return result

    def get_json(self):
        result = {}
        result["METADATA"] = {"name" : filename, "size" : canvas_size}
        result["sprites"] = []
        for n in self.nodes:
            if n.idata != None:
                result["sprites"].append({"name" : n.idata[1],"x" : n.x, \
                        "y" : n.y, "width" : n.width - border, "height" : n.height - border, \
                        "trimRect" : {"width" : n.idata[2], "height" : n.idata[3]}})
        return json.dumps(result, indent=4);

    def __str__(self):
        res = ""
        for n in self.nodes:
            res += str(n)
        return res;


def add_images_from_dir(dir_path):
    with os.scandir(dir_path) as it:
        print("Scanning", dir_path)
        for entry in it:
            if os.path.isdir(entry.path):
                add_images_from_dir(entry.path)
            elif entry.is_file:
                unix_path = entry.path.replace('\\','/')
                name = unix_path.split('/')[-1].split('.')[0]
                try:
                    i = Image.open(entry.path)
                    print("Found image:", entry.path)
                    if trim:
                        t = trimmed(i)
                        images.append((t[0], name, t[1], t[2]))
                    else:
                        images.append((i, name, 0, 0))
                except:
                    print("Ignoring non-image file:", entry.path)

def save_result(canvas, suffix=""):
    try:
        canvas.get_result().save(outpath + filename + suffix + ".png")
        print("Saved sprite sheet at", outpath + filename + suffix  + ".png!")
        with open(outpath + filename + suffix + ".json", "w") as json_file:
            json_file.write(canvas.get_json())
        print("Saved json file at", outpath + filename + suffix + ".json!")
    except:
        print("ERROR: Could not save sprite sheet/json! Please ensure all parameters are valid and try again!")

add_images_from_dir(path)
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
        save_result(canvas)
        exit()
