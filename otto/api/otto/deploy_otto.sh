#!/bin/bash
apt-get update
#&& apt-get install -y \
#  gcc
#\  build-base \  openssl-dev \  libffi-dev \  jpeg-dev \  zlib-dev

DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata
apt-get install -y \
  python3.8 \
  python3-pip \
  python3-dev \
  python3-setuptools

apt-get install -y \
  ffmpeg \
  aubio-tools \
  libaubio-dev \
  libaubio-doc

apt-get install -y \
  g++ \
  curl \
  git \
  gnupg \
  rpm \
  ffmpeg \
  wget


#zerotier-one \  cairo-dev \  openssh \  openrc

pip3 install \
  FastAPI \
  aiofiles \
  python-multipart \
  tinydb \
  pyjwt \
  passlib[bcrypt] \
  pymongo \
  moviepy \
  gizeh \
  ffmpeg-python
  #aubio

pip3 install \
  numpy

#COPY requirements.txt /
#pip3 install -r /requirements.txt

curl https://imagemagick.org/download/ImageMagick.tar.gz -o ./ImageMagick.tar.gz
tar xvzf ImageMagick.tar.gz
cd ImageMagick-7.0.10-14 && ./configure && make
#COPY ./examples/ImageMagick-7.0.10-14.tar.gz / &&
#RUN ./examples/tar xvzf ImageMagick-7.0.10-14.tar.gz &&
cd ImageMagick-7.0.10-14 && make install
ldconfig /usr/local/lib

git clone git://github.com/Trekky12/kburns-slideshow.git
cp ./examples/config_otto.json /kburns-slideshow/config.json
chmod +x /kburns-slideshow/main.py && ln -s /kburns-slideshow/main.py /usr/local/bin/kburns

cd /opt/code
DEBIAN_FRONTEND=noninteractive apt-get install -y ttf-mscorefonts-installer && fc-cache -f && mkdir ~/.fonts
cp ./examples/seg{oeui{,b,i,l,sl,z},ui{bl,bli,li,sb,sbi,sli}}.ttf ~/.fonts/ && fc-cache -f

mkdir -p  /opt/code/audios/ /opt/code/videos/ /opt/code/output/ /opt/code/data/
#ADD talaaudio.mp3 talavid.mp4
