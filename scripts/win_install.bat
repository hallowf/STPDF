REM "Installing PyQt5"
%PY% -m pip install PyQt5
REM "Setting python path"
SET PATH=%PATH%;C:\Python37\scripts
REM "Setting upx path"
cd UPX\
SET UPX_PATH=%cd% && cd ..
REM "Setting QT plugin path"
SET "QT_QPA_PLATFORM_PLUGIN_PATH=C:\Python37\Lib\site-packages\PyQt5\Qt\plugins\platforms"
SET "QT_PLUGIN_PATH=C:\Python37\Lib\site-packages\PyQt5\Qt\plugins"
REM "Contents of QT plugin path"
DIR %QT_QPA_PLATFORM_PLUGIN_PATH%
REM "Building GUI"
cd src\
pyinstaller --upx-dir %UPX_PATH% gui.spec
7z a STPDF-gui.7z dist\STPDF > NUL:
REM "GUI BUILT"
RMDIR /Q/S dist\
RMDIR /Q/S build\
REM "Building CLI"
pyinstaller --upx-dir %UPX_PATH% cli.spec --log-level ERROR
7z a STPDF-cli.7z dist\STPDF-cli > NUL:
REM "CLI BUILT"
RMDIR /Q/S dist\
MKDIR dist\
REM "Copying files"
xcopy *.7z dist\