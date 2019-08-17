import os
import sys
import string
from random import choice
from PIL import Image
import timeit
from memory_profiler import profile
from pytesseract import image_to_osd, Output


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

if __name__ == "__main__":
    test_img_with()
    # test_img_comp()
    # PIL_rotate()
    # SCI_rotate()
    # current_method()
    # print("image_set took:, "timeit.timeit("image_set()", globals=globals(), number=10))
    # print("image_list took:",timeit.timeit("image_list()", globals=globals(), number=10))
    # print("PIL_open took:", timeit.timeit("PIL_open()", globals=globals(), number=1))
