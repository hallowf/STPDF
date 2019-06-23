import os
import shutil
from random import choice
from PIL import Image, ImageDraw, ImageFont


def generate_images(count):
    cv = [i for i in range(251) if i != 0]
    if not os.path.isdir("images"):
        os.mkdir("images")
    if not os.path.isfile("Verdana.ttf"):
        raise FileNotFoundError("Verdana.ttf")
    for i in range(count + 1):
        if i != 0:
            img = Image.new("RGB", (1000, 1000),
                            color=(choice(cv), choice(cv), choice(cv)))
            d = ImageDraw.Draw(img)
            fnt = ImageFont.truetype('Verdana.ttf', 70)
            d.text((270, 450), "Hey there: %i" % i, fill=(255, 255, 255), font=fnt)
            img.save("images/%i.png" % i, dpi=(1000, 1000))
            img.close()
