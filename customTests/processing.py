import os
import sys
import time
import string
import psutil
from io import StringIO
from random import choice
from PIL import Image
import timeit
# from skimage.transform import rotate
# import numpy as np
# from skimage import io
from memory_profiler import profile
from pytesseract import image_to_osd, Output


def image_list():
    images = []
    for i in range(100000):
        images.append(i)
    [image for image in images]


def image_set():
    images = set()
    for i in range(100000):
        images.add(i)
    [image for image in images]


def PIL_rotate():
    rotations = [i for i in range(361) if i != 0]
    for root, __, files in os.walk("images", topdown=False):
        for file in files:
            source_path = os.path.join(root, file)
            img = Image.open(source_path)
            c = choice(rotations)
            img = img.rotate(c, resample=Image.BICUBIC, expand=True)
            img.save(source_path)
            img.close()


def SCI_rotate():
    rotations = [i for i in range(361) if i != 0]
    for root, __, files in os.walk("images", topdown=False):
        for file in files:
            source_path = os.path.join(root, file)
            img = io.imread(source_path)
            c = choice(rotations)
            img = rotate(img, c, order=3)
            io.imsave(source_path, img)


# BUG: this is crashing with images generated trough PIL:
# raise TesseractError(status_code, get_errors(error_string))
# pytesseract.pytesseract.TesseractError: 
# (1, 'Tesseract Open Source OCR Engine v5.0.0.20190526 with Leptonica Too few characters.
# Skipping this page Warning. Invalid resolution 0 dpi. Using 70 instead. Too few characters.
# Skipping this page Error during processing.')
def current_method():
    images = []
    for root, __, files in os.walk("images", topdown=False):
        for file in files:
            source_path = os.path.join(root, file)
            img = Image.open(source_path)
            rotate = image_to_osd(img, output_type=Output.DICT)["rotate"]
            img = img.rotate(-rotate, resample=Image.BICUBIC, expand=True)
            img.close()
            images.append(img)
    a = [img for img in images]
    images = []


def make_pdf(handles):
    letters = string.ascii_lowercase
    name = "".join(choice(letters) for i in range(10)) + ".pdf"
    print("making pdf: %s" % name)
    first = handles.pop(0)
    sys.exit()
    first.save(name, "PDF", resolution=90.0, save_all=True,
               append_images=handles)


def test_img_with():
    images = []
    for root, __, files in os.walk("images", topdown=False):
        for file in files:
            source_path = os.path.join(root, file)
            with open(source_path, "rb") as fp:
                with Image.open(fp) as img:
                    try:
                        img.verify()
                    except Exception as e:
                        print(e)
                        print("skipping image %s" % source_path)
                        continue
                with Image.open(fp) as img:
                    img.load()
                    images.append(img)
    print(len(images))
    print("opening all images")
    make_pdf(images)
    print("done")


def test_img_comp():
    images = []
    for root, __, files in os.walk("images", topdown=False):
        for file in files:
            source_path = os.path.join(root, file)
            print("appending image: %s" % source_path)
            images.append(source_path)
    print("opening all images")
    images = [Image.open(img) for img in images]
    make_pdf(images)
    print("done")


class FillMemoryIncrementalyUntilCrash(object):

    def __init__(self):
        self.path_depths = [2,3,4,5,6]
        self.path_names = ["home", "etc", "opt", "root", "dev", "var", "usr"]
        self.proc = psutil.Process(os.getpid())
        self.paths = []

    # creates a random probably non-existent "system" path
    def create_path(self, path_depth=None):
        desired_depth = path_depth or choice(self.path_depths)
        new_path = "/".join(choice(self.path_names) for i in range(desired_depth))
        # print("Created path is: /%s" % new_path)
        return "/%s" % new_path

    # to fill with bytes until it crashes
    def fill_memory(self, increment=2):
        avail_choices = [increment, choice(self.path_depths)]
        print("Increment is %i" % increment)
        print("Mem usage in bytes: %i" % self.proc.memory_info().rss)
        for i in range(increment):
            # Raise error when occupying more than 1 GB of memory
            if self.proc.memory_info().rss >= 1073741824:
                raise MemoryError("Exceeding 1GB limit")
            new_path = self.create_path(choice(avail_choices)).encode()
            # print("Adding %i bytes to memory" % sys.getsizeof(new_path))
            self.paths.append(new_path)
        if increment == 1:
            increment += increment
        else:
            increment += int(increment / 2)
        self.fill_memory(increment)


if __name__ == "__main__":
    # try:
    #     FillMemoryIncrementalyUntilCrash().fill_memory()
    # except Exception as e:
    #     raise e
    #     print(e)
    test_img_with()
    # test_img_comp()
    # PIL_rotate()
    # SCI_rotate()
    # current_method()
    # print("image_set took:, "timeit.timeit("image_set()", globals=globals(), number=10))
    # print("image_list took:",timeit.timeit("image_list()", globals=globals(), number=10))
    # print("PIL_open took:", timeit.timeit("PIL_open()", globals=globals(), number=1))
