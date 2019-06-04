

#### Notes

`img.rotate(-rotate,resample=Image.BICUBIC, expand=True)`
This tells it to use the highest quality interpolation algorithm that it has available,
and to expand the image to encompass the full rotated size instead of cropping.
The documentation does not say what color the background will be filled with.
https://stackoverflow.com/a/17822099

##### Themes
https://stackoverflow.com/questions/48256772/dark-theme-for-in-qt-widgets
https://gist.github.com/gph03n1x/7281135

###### The color groups:

The Active group is used for the window that has keyboard focus.
The Inactive group is used for other windows.
The Disabled group is used for widgets (not windows) that are disabled for some reason.

##### Deskewing

This requires the user to have tesseract installed

 * TODO:

    1. check if user has tesseract
    2. block the option remove rotation if the above is false
    3. investigate other ways to remove rotation altough tesseract seems to be the fastest
    4. this probably fails on images that contain little, few or no text at all, the exception should be handle properly

##### Translation
