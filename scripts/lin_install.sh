#!/usr/bin/env sh
echo "Setting upx path"
cd UPX || return
export UPX_PATH=$PWD
cd ../src || return
# echo "Setting QT path"
# # export QT_QPA_PLATFORM_PLUGIN_PATH="/home/travis/virtualenv/python3.7.1/lib/python3.7/site-packages/PyQt5/"
# export QT_QPA_PLATFORM_PLUGIN_PATH="/home/travis/virtualenv/python3.7.1/"
# echo "Contents of QT path"
# ls $QT_QPA_PLATFORM_PLUGIN_PATH
echo "Building GUI"
pyinstaller --upx-dir=$UPX_PATH gui.spec
7z a STPDF-gui.7z dist/STPDF > /dev/null
rm -r dist build
echo "Building CLI"
pyinstaller --upx-dir $UPX_PATH cli.spec --log-level ERROR
7z a STPDF-cli.7z dist/STPDF-cli > /dev/null
rm -r dist build
mkdir dist
cp ./*.7z dist