import sys
import os
from PIL import Image

class VirtualImage():
    def __init__(self, w, h):
        self.width = w;
        self.height = h;

path = sys.argv[1]

images = []
virt-images = []
canvas = Image.new("RGB", (1280, 720));

with os.scandir(path) as it:
    for entry in it:
        if entry.is_file:
            images.append(Image.open(entry.path))

            print(entry.path)

off = 0
for i in range(0, len(images)):
    canvas.paste(images[i], (off, 0))
    off += images[i].width

canvas.save("test.png")
