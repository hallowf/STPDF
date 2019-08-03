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
import logging
import traceback

from PIL import Image
from stpdf.core.converter import Converter
from pytesseract import image_to_string
from pytesseract.pytesseract import TesseractNotFoundError
from _version import (__version__, __version2__, __releaseDate__,
                      __releaseDate2__, __developer__, __developer2__,
                      __devhome__)


class STPDFCLI(object):
    def __init__(self, source, dest, *args, **kwargs):
        self.source = source
        self.dest = dest
        self.logger = kwargs.get("logger")
        self.settings = kwargs.get("settings")
        self.args = kwargs.get("uargs")
        self.res = kwargs.get("resolution", 90.0)
        self.deskew = kwargs.get("deskew", False)
        self.app_lang = self.settings["lang"]
        if not self.check_tesseract() and self.deskew:
            m = _("Setting deskew to false, tesseract wasn't found on your machine")
            self.logger.warning(m)
            self.deskew = False
        self.print_values()

    def print_values(self):
        s = _("Source")
        d = _("Destination")
        splt = _("Split")
        splt_a = _("Split at")
        dsk = _("Deskew")
        r = _("Resolution")
        dc = _("Do copy")
        mp = _("Make PDF")
        ll = _("Log level")
        l = _("Language")
        sk = _("Skip check")
        v0 = "\n\t%s: %s\n\t%s: %s" % (s, self.source, d, self.dest)
        v1 = "\n\t%s: %s\n\t%s: %s" % (splt, self.settings["split"],
                                       splt_a, self.settings["split_at"])
        v2 = "\n\t%s: %s\n\t%s: %s" % (dsk, self.settings["deskew"],
                                       r, self.settings["res"])
        v3 = "\n\t%s: %s\n\t%s: %s" % (dc, self.settings["d_copy"],
                                       mp, self.settings["m_pdf"])
        v4 = "\n\t%s: %s\n\t%s: %s" % (ll, self.settings["log_level"],
                                       l, self.settings["lang"])
        v5 = "\n\t%s: %s" % (sk, self.settings["skip_check"])
        values = v0 + v1 + v2 + v3 + v4 + v5
        msg = "%s:%s" % (_("Starting converter with values"), values)
        self.logger.info(msg)
        if not self.settings["skip_check"]:
            ans = input("Continue? (Y): ")
            if ans.upper() != "Y":
                self.logger.info(_("Exiting now"))
                sys.exit(1)

    def run_converter(self):
        splt = (self.settings["split"], self.settings["split_at"])
        cvt = Converter(self.source, self.dest,
                        split=splt,
                        deskew=self.deskew,
                        lang=self.app_lang,
                        save_files=self.settings["d_copy"],
                        make_pdf=self.settings["m_pdf"])
        try:
            for line in cvt.process_all():
                self.logger.info(line)
        except Exception as e:
            self.logger.critical("Critical exception:\n" + str(e) + "\n\n" + "Exiting now")
            sys.exit(1)

    def check_tesseract(self):
        img = Image.new('RGB', (60, 30), color='red')
        try:
            text = image_to_string(img)
            img.close()
            return True
        except TesseractNotFoundError:
            img.close()
            return False


# Function to verify correct usage of args
# before providing them to STPDFCLI
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


# Installs language based on lang: str - "en" or "pt"
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


def check_settings(args):
    kv = getattr(args, "kv")
    lv = getattr(args, "lv")
    splt_a = getattr(args, "sa") or 0
    splt = True if splt_a > 0 else False
    settings = {
        "source": getattr(args, "source"),
        "dest": getattr(args, "destination"),
        "split": splt,
        "split_at": splt_a,
        "deskew": getattr(args, "ds"),
        "res": getattr(args, "r"),
        "d_copy": False,
        "m_pdf": True,
        "log_level": "INFO",
        "lang": getattr(args, "l"),
        "skip_check": getattr(args, "sc")
    }
    if kv is not None:
        kv = "%s.pckl" % kv if not kv.endswith(".pckl") else kv
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


def install_logger(l_level):
    l_levels = [
        "INFO",
        "WARNING",
        "CRITICAL",
        "ERROR",
        "DEBUG"
    ]
    n_level = None
    if l_level not in l_levels:
        sys.stdout.write("%s: %s\n" % (_("Invalid log level"), l_level))
        l_level = "INFO"
    n_level = getattr(logging, l_level.upper(), 10)
    # Console logger
    log_format = "%(name)s - %(levelname)s: %(message)s"
    logging.basicConfig(format=log_format, level=n_level)
    logger = logging.getLogger("STPDF-CLI")
    msg = "%s: %s" % (_("Console logger is set with log level"), l_level)
    logger.info(msg)
    return logger


# Assembles argparser and returns parsed args
def assemble_parser():
    parser = argparse.ArgumentParser(description=_('STPDF - easily convert scans to pdf'))
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
                        default=80.0,
                        help=_("Resolution of final rotated image, must be a value like 90.5"))
    parser.add_argument("--ll", "--log-level", type=str,
                        default="INFO",
                        help=_("Sets the console log level"))
    parser.add_argument("--l", "--language", type=str,
                        default="en",
                        help=_("Switch language, language must be 2 letter code EX: en or pt"))
    parser.add_argument("--kv", "--keep-values",
                        type=str,
                        help=_("Save your current input in a file, can't be used with --lv"),
                        action="store")
    parser.add_argument("--lv", "--load-values",
                        type=str,
                        help=_("Load values from settings file, can't be used with --kv"),
                        action="store")
    parser.add_argument("--sc", "--skip-check",
                        help=_("Automatically answers yes when values are verified"),
                        action="store_true")
    parser.add_argument("--dc", "--do-copy",
                        help=_("If True images will be copied to the destination directory, default:False"),
                        default=False,
                        action="store_true")
    parser.add_argument("--mp", "--make-pdf",
                        help=_("If True make a pdf out of the processed images, default:True"),
                        default=True,
                        action="store_true")
    v_text = "\n\t%s: %s,\n\t%s: %s," % (_("Version"), __version__,
                                         _("Full version"), __version2__)
    r_text = "\n\t%s: %s,\n\t%s: %s," % (_("Release date"), __releaseDate__,
                                         _("Developed by"), __developer__)
    home = "\n\t%s: %s" % (_("Project home"), __devhome__)
    all_info = v_text + r_text + home
    parser.add_argument('--version', action='version',
                        version='%(prog)s {vi}'.format(vi=all_info))
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    gettext.install("stpdf_cli")
    args = assemble_parser()
    lang = getattr(args, "l")
    install_lang(lang)
    loggr = install_logger(getattr(args, "ll"))
    settings = None
    try:
        loggr.info(_("Checking settings"))
        settings = check_settings(args)
    except Exception as e:
        sys.stdout.write("\n")
        for it in traceback.format_exception(type(e), e, e.__traceback__):
            loggr.debug(it)
        msg = "%s: %s" % (_("Failed to create settings "), str(e))
        loggr.critical(msg + "\n")
        sys.exit(1)
    msg = "%s: %s" % (_("Settings"), settings)
    loggr.debug(msg)
    has_required = verify_args(args)
    if has_required is True:
        cli = STPDFCLI(args.source, args.destination,
                       logger=loggr, settings=settings,
                       uargs=args)
        cli.run_converter()
        cli.logger.info(_("Finished"))
        sys.exit(0)
    else:
        loggr.critical(has_required + "\n")
        sys.exit(1)
