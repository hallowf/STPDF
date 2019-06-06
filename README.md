# STPDF Convert scans to PDF's


## Please visit our [docs](https://hallowf.github.io/STPDF/) for more info



#### Notes

`img.rotate(-rotate,resample=Image.BICUBIC, expand=True)`
This tells it to use the highest quality interpolation algorithm that it has available,
and to expand the image to encompass the full rotated size instead of cropping.
The documentation does not say what color the background will be filled with.
https://stackoverflow.com/a/17822099

##### Themes


**It seems that most of these values hadn't changes because the theme fusion wasn't set in the whole app**
  * TODO:

    1. Most is tested there are still some stuff not being used below is a list of all possible objects that can have it's color changed
      * Active
      * All <- I'm not even going to try this
      * AlternateBase <- no idea
      * Background <- changes background of window
      * Base <- changes background of QTextEdit and QComboBox but not window
      * BrightText
      * Button <- changes color of button background
      * ButtonText <- change the color of the button text but just QPushButton
      * ColorGroup
      * ColorRole
      * Current
      * Dark
      * Disabled
      * Foreground <- changes QLabel color
      * Highlight <- changes the highlight for QComboBox items and menu items
      * HighlightedText
      * Inactive
      * Light
      * Link
      * LinkVisited
      * Mid
      * Midlight
      * NColorGroups
      * NColorRoles
      * NoRole
      * Normal
      * PlaceholderText
      * Shadow
      * Text <- This seems to change most of the text, changes text from QComboBox, menu QAction, and QTextEdit
      * ToolTipBase <- seems to make no changes to TipSlider however it could be that i'm setting this the wrong way
      * ToolTipText <- same as above
      * Window <- seems to have no effect?
      * WindowText <- same as above

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
