FROM ubuntu:20.04

RUN apt-get update
#&& apt-get install -y \
#  gcc
#\  build-base \  openssl-dev \  libffi-dev \  jpeg-dev \  zlib-dev

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata
RUN apt-get install -y \
  python3.8 \
  python3-pip \
  python3-dev \
  python3-setuptools

RUN apt-get install -y \
  ffmpeg \
  aubio-tools \
  libaubio-dev \
  libaubio-doc

RUN apt-get install -y \
  g++ \
  curl \
  git \
  gnupg \
  rpm \
  ffmpeg \
  wget


#zerotier-one \  cairo-dev \  openssh \  openrc

RUN pip3 install \
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

RUN pip3 install \
  numpy

#COPY requirements.txt /
#RUN pip3 install -r /requirements.txt

RUN curl https://imagemagick.org/download/ImageMagick.tar.gz -o ./ImageMagick.tar.gz
RUN tar xvzf ImageMagick.tar.gz
RUN cd ImageMagick-7.0.10-14 && ./configure && make
#COPY ./examples/ImageMagick-7.0.10-14.tar.gz / &&
#RUN ./examples/tar xvzf ImageMagick-7.0.10-14.tar.gz &&
RUN cd ImageMagick-7.0.10-14 && make install
RUN ldconfig /usr/local/lib

RUN git clone git://github.com/Trekky12/kburns-slideshow.git
COPY ./examples/config_otto.json /kburns-slideshow/config.json
RUN chmod +x /kburns-slideshow/main.py && ln -s /kburns-slideshow/main.py /usr/local/bin/kburns

WORKDIR /opt/code
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y ttf-mscorefonts-installer && fc-cache -f && mkdir ~/.fonts
#RUN cp ./examples/seg{oeui{,b,i,l,sl,z},ui{bl,bli,li,sb,sbi,sli}}.ttf ~/.fonts/ && fc-cache -f

RUN mkdir -p  /opt/code/audios/ /opt/code/videos/ /opt/code/output/ /opt/code/data/
#Add talaaudio.mp3 talavid.mp4

CMD ["python3"]
