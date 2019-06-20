# <STPDF convert scans to pdf>
# Copyright (C) <2019>  <Alexandre Cortegaça>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import sys
import argparse
import gettext
import pickle
import locale

from PIL import Image
from stpdf.converter import Converter
from pytesseract import image_to_string
from pytesseract.pytesseract import TesseractNotFoundError


class STPDFCLI(object):
    def __init__(self, source, dest, split=(False, 0), *args, **kwargs):
        self.source = source
        self.dest = dest
        self.settings = kwargs.get("settings", None)
        split, split_at = split
        self.split = split
        self.split_at = split_at
        self.res = kwargs.get("resolution", 90.0)
        self.deskew = kwargs.get("deskew", False)
        m = _("Setting deskew to false, tesseract wasn't found on your machine")
        if not self.check_tesseract() and self.deskew:
            print(m)
            self.deskew = False

    def run_converter(self):
        s = _("Split")
        sa = _("Split at")
        d = _("Deskew")
        r = _("Resolution")
        v1 = "\n\t%s: %s\n\t%s: %s" % (s, self.split, sa, self.split_at)
        v2 = "\n\t%s: %s\n\t: %s" % (d, self.deskew, r, self.res)
        msg = "%s:%s" % (_("Starting converter with values"), values)
        print(msg)
        cvt = Converter(self.source, self.dest,
                        split=self.split,
                        deskew=self.deskew,
                        lang=self.app_lang)
        try:
            for line in cvt.preprocess_all():
                print(line)
            for line in cvt.make_pdf():
                print(line)
        except Exception as e:
            raise e

    def check_tesseract(self):
        img = Image.new('RGB', (60, 30), color='red')
        try:
            text = image_to_string(img)
            img.close()
            return True
        except TesseractNotFoundError:
            img.close()
            return False


def verify_args(args):
    kv = getattr(args, "kv", None)
    lv = getattr(args, "lv", None)
    if kv is not None and lv is not None:
        return _("Can't use --keep-values with --load-values")
    if lv is None:
        if not os.path.isdir(args.source) or not os.path.isdir(args.destination):
            msd = _("Missing source or destination")
            s = _("Source")
            d = _("Destination")
            msg = "%s\n\t%s: %s\n\t%s: %s" % (msd, s, d, args.source,
                                            args.destination)
            return msg
    s = getattr(args, "s", None)
    if s is not None:
        try:
            if int(s) <= 2:
                return "%s: %s" % (_("Split at value too low"), s)
        except ValueError as e:
            return "%s: %s" % (_("Split at must be a number"), s)
    r = getattr(args, "r", None)
    if r is not None:
        if r > 100.0:
            return _("Max resolution is 100.0")
    return True


def install_lang(lang):
    available_langs = [
        "en",
        "pt",
        "es"
    ]
    if lang in available_langs and lang != "en":
        modl = "%s_cli" % lang
        current_locale, encoding = locale.getdefaultlocale()
        cl = current_locale.split("_")
        if lang != cl[0]:
            current_locale = "%s_%s" % (lang, lang.upper())
        lang = gettext.translation(modl,
                                    "locale",
                                    [current_locale])
        lang.install()


def make_settings(args):
    kv = getattr(args, "kv")
    splt_a = getattr(args, "sa") or 0
    splt = True if splt_a > 0 else False
    settings = {
        "source": getattr(args, "source"),
        "dest": getattr(args, "destination"),
        "split": splt,
        "split_at": splt_a,
        "deskew": getattr(args, "ds", False),
        "res": getattr(args, "r", ),
    }

    if kv is not None:
        if not kv.endswith(".pckl"):
            kv = "%s.pckl" % kv
        if not os.path.isfile(kv):
            pickle.dump(settings, open(kv, "wb"))
        else:
            raise FileExistsError(kv)
    elif lv is not None:
        lv = "%s.pckl" % lv if not lv.endswith(".pckl") else lv
        if not os.path.isfile(lv):
            raise FileNotFoundError(lv)
        else:
            settings = pickle.load(open(lv, "rb"))
    return settings


if __name__ == "__main__":
    gettext.install("stpdf_cli")
    parser = argparse.ArgumentParser(description=_('Capture training data, press ctrl+q to stop recording'))
    parser.add_argument("source",
                        nargs="?",
                        type=str,
                        default=os.getcwd(),
                        help=_('Scan images location'))
    parser.add_argument("destination",
                        nargs="?",
                        type=str,
                        default="STPDF_Output",
                        help=_('Destination of modified files'))
    parser.add_argument("--sa", "--split-at", type=int,
                        help=_("Number of images per pdf"))
    parser.add_argument("--ds", "--deskew",
                        help=_('Removes image rotation, requires tesseract'),
                        action="store_true")
    parser.add_argument("--r", "--resolution", type=float,
                        help=_("Resolution of final rotated image, must be a value like 90.5"))
    parser.add_argument("--ll", "--log-level", type=str,
                        help=_("Sets the console log level"))
    parser.add_argument("--l", "--language", type=str,
                        help=_("Switch language, language must be 2 letter code EX: en or pt"))
    parser.add_argument("--kv", "--keep-values",
                        type=str,
                        help=_("Save your current input in a file, can't be used with --lv"),
                        action="store")
    parser.add_argument("--lv", "--load-values",
                        type=str,
                        help=_("Load values from settings file, can't be used with --kv"),
                        action="store")
    args = parser.parse_args()
    lang = getattr(args, "l", "en")
    install_lang(lang)
    settings = None
    try:
        settings = make_settings(args)
    except Exception as e:
        print("Failed to create settings", e)
        raise e
        sys.exit(1)
    has_required = verify_args(args)
    if has_required is True:
        cli = STPDFCLI(args.source, args.destination,
                       split=split_tup, deskew=deskew, resolution=res, settings=settings)
        cli.run_converter()
    else:
        print(has_required)