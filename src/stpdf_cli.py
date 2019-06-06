import os,sys,argparse,gettext,pickle

from PIL import Image
from stpdf.converter import Converter
from pytesseract import image_to_string
from pytesseract.pytesseract import TesseractNotFoundError


class STPDFCLI(object):
    
    def __init__(self,source,dest,split=(False,0), *args, **kwargs):
        self.source = source
        self.dest = dest
        self.split = split
        self.split_at = split_at
        self.res = kwargs.get("resolution")
        self.deskew = kwargs.get("deskew")
        if not self.check_tesseract() and self.deskew:
            print(_("Setting deskew to false, tesseract wasn't found on your machine"))
            self.deskew = False

    def run_converter(self):
        values = "\n\tSplit: %s\n\tSplit at: %s\n\tDeskew: %s\n\tResolution: %s" % (do_split, split_at,
                deskew, res)
        msg = "%s:%s" % (_("Starting converter with values"),values)
        print(msg)
        cvt = Converter(self.source,self.dest,split=self.split,deskew=self.deskew)
        try:
            for line in cvt.verify_copy_size():
                print(line)
            for line in cvt.make_pdf():
                print(line)


    def check_tesseract(self):
        img = Image.new('RGB', (60, 30), color = 'red')
        try:
            text = image_to_string(img)
            return True
        except TesseractNotFoundError:
            return False

def verify_args(args):
    if not os.path.isdir(args.source) or not os.path.isdir(args.destination):
        msg = "Missing source or destination\n\tSource: %s\n\tDestination: %s" % (args.source,
                args.destination)
        return msg
    s = getattr(args, "s", None)
    if s != None:
        if int(s) <= 2:
            return "%s: %s" % (_("Split at value too low"),s)
    r = getattr(args, "r", None)
    if r != None:
        if r > 100.0:
            return _("Max resolution is 100")
    return True


def install_lang_and_settings():
    available_langs = [
        "en",
        "pt"
    ]
    if os.path.isfile("cli_values.pckl"):
        settings = pickle.loads(open("cli_values.pckl" ,"rb"))
        lang = settings["lang"]
        if lang in available_langs and lang != "en":
            modl = "%s_cli" % lang
            lang = gettext.translation(modl, localedir="locale")
            lang.install()
    else:
        settings = {
            "lang": "en",
            "keep_vals": False
        }
        pickle.dumps(settings, open("cli_values.pckl", "wb"))




if __name__ == "__main__":
    gettext.install("stpdf_cli")
    parser = argparse.ArgumentParser(description=_('Capture training data, press ctrl+q to stop recording'))
    parser.add_argument("source", type=str, help=_('Scan images location'))
    parser.add_argument("destination", type=str, help=_('Destination of modified files'))
    parser.add_argument("--s", "--split-at", type=int,
    help=_("Number of images per pdf"))
    parser.add_argument("--d", "--deskew", help=_('An identifier for training data file'), action="store_true")
    parser.add_argument("--r", "--resolution", type=float, help=_("Resolution of final rotated image, must be a value like 90.0"))
    args = parser.parse_args()
    has_required = verify_args(args)
    if has_required == True:
        split_at = getattr(args, "s") or 0
        do_split = True if split_at else False
        split_tup = (do_split,split_at)
        deskew = getattr(args, "d")
        res = getattr(args, "r", 90.0)
        cli = STPDFCLI(args.source,args.destination,split=split_tup,deskew=deskew, resolution=res)
    else:
        print(has_required)

    

        
