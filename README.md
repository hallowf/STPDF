

#### Notes

`img.rotate(-rotate,resample=Image.BICUBIC, expand=True)`
This tells it to use the highest quality interpolation algorithm that it has available,
and to expand the image to encompass the full rotated size instead of cropping.
The documentation does not say what color the background will be filled with.
https://stackoverflow.com/a/17822099

##### Themes

  * TODO:

    1. almost everything \*(the base functions for loading are verifying themes are done)
    2. this wasn't finished neither tested
    3. find a fix for this:

```
# TODO: Investigate how to call lighter/darker trough a variable
 # something like ()[var]() but that won't work if var is None or something wrong
 qplt = QtGui.QPalette()
 qplt.setColor(QtGui.QPalette.Highlight,
     QtGui.QColor(*tv["highlight"]).lighter())

class Potato:

   func1(self):
       do_something()

   func2(self):
       do_other_thing()

potato = Potato()

method_to_run = 'func1'
getattr(potato, method_to_run)()
```

https://stackoverflow.com/questions/48256772/dark-theme-for-in-qt-widgets
https://gist.github.com/gph03n1x/7281135

###### The color groups:

The Active group is used for the window that has keyboard focus.
The Inactive group is used for other windows.
The Disabled group is used for widgets (not windows) that are disabled for some reason.

##### Deskewing

This requires the user to have tesseract installed

Tessseract is not easily available for windows [however](https://github.com/UB-Mannheim/tesseract/wiki)

>The Mannheim University Library (UB Mannheim) uses Tesseract to perform OCR of historical German newspapers (Allgemeine Preußische Staatszeitung, Deutscher Reichsanzeiger). The latest results with OCR from more than 360,000 scans are available online.
>Normally we run Tesseract on Debian GNU Linux, but there was also the need for a Windows version. That's why we have built a Tesseract installer for Windows.

 * TODO:

    1. check if user has tesseract
    2. block the option remove rotation if the above is false
    3. investigate other ways to remove rotation altough tesseract seems to be the fastest
    4. this probably fails on images that contain little, few or no text at all, the exception should be handle properly
    5. Install tesseract for the user?

##### Translation

`pygettext.py -d base -o locales/base.pot file.py`
this will generate a "base" pot in the locales folder, which can then be edited and generate the appropiate compiled translations
