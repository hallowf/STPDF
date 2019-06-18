echo "Setting upx path"
cd UPX
UPX_PATH=$PWD
cd ../src
echo "Building GUI"
echo UPX_PATH $UPX_PATH
ls $UPX_PATH
# pyinstaller --upx-dir=$UPX_PATH gui.spec --log-level ERROR
pyinstaller --upx-dir $UPX_PATH gui.spec
7z a STPDF-gui.7z dist > /dev/null
rm -r dist build
echo "Building CLI"
pyinstaller --upx-dir $UPX_PATH cli.spec --log-level ERROR
7z a STPDF-cli.7z dist > /dev/null
rm -r dist build
mkdir dist
cp *.7z dist