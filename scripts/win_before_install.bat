REM "Installing python"
choco install python --version 3.4.4
REM "Installing PyQt"
choco install pyqt5 --version 5.1
REM "Fetching UPX"
mkdir UPX && cd UPX
ECHO UPX_PATH is %cd%
curl https://github.com/upx/upx/releases/download/v3.95/upx-3.95-win64.zip -J -L --output UPX.zip
7z e -y UPX.zip -o"." upx-3.95-win64\*.exe
cd ..