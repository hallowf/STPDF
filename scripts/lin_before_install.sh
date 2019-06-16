sudo apt update
mkdir UPX
curl https://github.com/upx/upx/releases/download/v3.95/upx-3.95-win64.zip -J -L --output UPX.zip
7z e -y UPX.zip -o"." upx-3.95-win64\*.exe
cd ..