#!/usr/bin/env sh
echo "Installing packages"
sudo apt -y install p7zip-full libpython3.7 libpython3.7-dev python3.7-dev
mkdir UPX && cd UPX || return
echo "UPX_PATH is $PWD"
curl -sL -o upx.txz https://github.com/upx/upx/releases/download/v3.95/upx-3.95-amd64_linux.tar.xz
tar -xvf upx.txz --strip-components=1
cd ..
echo UPX_PATH contents
ls UPX/