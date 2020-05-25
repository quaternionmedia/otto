FROM python:3.8.3-alpine3.11

# TODO install imagemagick from curl file; linked properly; needs a "data" folder locally relative;

# TODO build form input for talavideo.json

RUN apk update && apk add --no-cache --virtual .builds-deps \
  build-base \
  gcc \
  openssl-dev \
  libffi-dev \
  jpeg-dev \
  zlib-dev

RUN apk add \
  g++ \
  curl \
  git \
  gnupg \
  rpm
#  ssh \

RUN curl -s 'https://raw.githubusercontent.com/zerotier/ZeroTierOne/master/doc/contact%40zerotier.com.gpg' | gpg --import

RUN apk add \
  ffmpeg \
  zerotier-one

#RUN zerotier-cli join $zerotier

#RUN pip install -U pip

RUN pip install \
  FastAPI \
  aiofiles \
  python-multipart \
  tinydb \
  pyjwt \
  passlib[bcrypt] \
  pymongo \
  ffmpeg-python \
  moviepy \
  gizeh
RUN pip install \
  numpy

RUN pip install \
  aubio

#COPY requirements.txt /
#RUN pip install -r /requirements.txt

RUN apk add \
  cairo-dev
#  imagemagick

# Toss if ImageMagick runs without the below.
#RUN curl -SL https://imagemagick.org/download/linux/CentOS/x86_64/ImageMagick-7.0.10-14.x86_64.rpm -o ./ImageMagick-7.0.10-14.x86_64.rpm \
#  && curl -s https://imagemagick.org/download/linux/CentOS/x86_64/ImageMagick-libs-7.0.10-14.x86_64.rpm -o ./ImageMagick-libs-7.0.10-14.x86_64.rpm
#  RUN rpm -Uvh ImageMagick-libs-7.0.10-14.x86_64.rpm
#RUN rpm -Uvh ImageMagick-7.0.10-14.x86_64.rpm

RUN curl https://imagemagick.org/download/ImageMagick.tar.gz -o ./ImageMagick.tar.gz
RUN tar xvzf ImageMagick.tar.gz
RUN cd ImageMagick-7.0.10-14 && ./configure && make
RUN  cd ImageMagick-7.0.10-14 && make install
RUN ldconfig /usr/local/lib

WORKDIR /opt/code
# TODO uncomment RUN and COPY for kburns
RUN git clone https://github.com/Trekky12/kburns-slideshow.git
#COPY ./examples/config_otto.json ./kburns-slideshow/config.json
# Toss if it runs without the below.
#cd kburns-slideshow

RUN apk add \
  wget

#CMD ["python3","otto.py"]
CMD ["python3"]
