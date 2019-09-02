import os
import sys
from PIL import Image
from random import choice


image_paths = []
rotations = [i * i for i in range(12)]
names = ["pdf%i.pdf" % i for i in range(20)]


def image_generator(do_break=False):
    print("running generator")
    for img_p in image_paths:
        print("processing image %s" % img_p)
        with open(img_p, "rb") as fp:
            with Image.open(fp) as img:
                try:
                    img.verify()
                except Exception as e:
                    print("invalid image continuing")
                    print("Exception: %s" % str(e))
                    continue
            with open(img_p, "rb") as fp:
                with Image.open(fp) as img:
                    # Did i do this in the core module?
                    img.load()
                    img = resize_image(img)
                    yield img


def gather_images(img_dir):
    print("gathering images")
    for root, __, files in os.walk(img_dir, topdown=False):
        for file in files:
            source_path = os.path.join(root, file)
            image_paths.append(source_path)
    return image_paths


def resize_image(img):
    size = (img.size[0] / 3, img.size[1] / 3)
    img.thumbnail(size, Image.ANTIALIAS)
    return img

def process_image(img):
    img = img.rotate(choice(rotations), resample=Image.BICUBIC, expand=True)
    return img


def run_main(imgs_dir):
    image_paths = gather_images(imgs_dir)
    if len(image_paths) < 3:
        print("not enough images")
    else:
        print("starting")
        first_img = None
        for img in image_generator():
            first_img = img
            break
        image_paths.pop(0)
        print("Images to process: %i" % len(image_paths))
        name = choice(names)
        for name in names:
            if os.path.isfile(name):
                name = choice(name)
        if os.path.isfile(name):
            print("can't create a name")
        else:
            first_img.save(name, "PDF", resolution=90, save_all=True,
                           append_images=image_generator())


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("need path argument (location of images)")
    elif not os.path.isdir(os.path.abspath(sys.argv[1])):
        print("Provided path does not exists")
    else:
        run_main(sys.argv[1])