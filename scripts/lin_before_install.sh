mkdir UPX && cd UPX
echo UPX_PATH is $PWD
curl -sL -o upx.txz https://github.com/upx/upx/releases/download/v3.95/upx-3.95-amd64_linux.tar.xz
tar -xvf upx.txz --strip-components=1
cd ..
echo UPX_PATH contents
ls UPX/