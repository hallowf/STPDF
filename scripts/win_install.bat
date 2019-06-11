REM "Creating virtualenv so that os detects pyinstaller"
%PY% -m pip install virtualenv==16.1
%PY% -m virtualenv venv
venv\Scripts\activate.bat
REM "Reinstalling requirements on virtualenv"
python -m pip install -r requirements.txt
REM "Building GUI"
cd src\
pyinstaller --upx-dir=%UPX_PATH% gui.spec
7z a STPDF-gui.7z dist > NUL:
REM "GUI BUILT"
RMDIR /Q/S dist\
RMDIR /Q/S build\
REM "Building CLI"
pyinstaller --upx-dir=%UPX_PATH% stpdf_cli.spec
7z a STPDF-cli.7z dist > NUL:
REM "CLI BUILT"
RMDIR /Q/S dist\
MKDIR dist\
REM "Copying files"
xcopy *.7z dist\