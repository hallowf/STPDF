import os
import sys
from random import choice
import time
from PIL import Image
import timeit
from skimage.transform import rotate
import numpy as np
from skimage import io
from memory_profiler import profile
from pytesseract import image_to_osd, Output


@profile
def image_list():
    images = []
    for i in range(100000):
        images.append(i)
    [image for image in images]


@profile
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


if __name__ == "__main__":
    PIL_rotate()
    # SCI_rotate()
    # current_method()
    # print("image_set took:, "timeit.timeit("image_set()", globals=globals(), number=10))
    # print("image_list took:",timeit.timeit("image_list()", globals=globals(), number=10))
    # print("PIL_open took:", timeit.timeit("PIL_open()", globals=globals(), number=1))
