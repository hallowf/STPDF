REM "Setting path again because why not"
SET PATH=%PATH%;C:\Python37\scripts
REM "Setting upx path"
mkdir cd UPX\ && SET UPX_PATH=%cd% && cd ..
REM "Building GUI"
cd src\
REM pyinstaller --upx-dir=%UPX_PATH% gui.spec --log-level ERROR
pyinstaller --upx-dir=%UPX_PATH% gui.spec
7z a STPDF-gui.7z dist > NUL:
REM "GUI BUILT"
RMDIR /Q/S dist\
RMDIR /Q/S build\
REM "Building CLI"
pyinstaller --upx-dir=%UPX_PATH% cli.spec --log-level ERROR
7z a STPDF-cli.7z dist > NUL:
REM "CLI BUILT"
RMDIR /Q/S dist\
MKDIR dist\
REM "Copying files"
xcopy *.7z dist\