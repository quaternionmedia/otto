FROM ubuntu:20.04

RUN apt-get update

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

RUN pip3 install \
  numpy

#COPY requirements.txt /
#RUN pip3 install -r /requirements.txt

RUN apt-get install -y \
  libmagick++-dev

COPY ./deps/ImageMagick-7.0.10-14.tar.gz /
RUN tar xvzf ImageMagick-7.0.10-14.tar.gz
RUN cd ImageMagick-7.0.10-14 && make install
RUN ldconfig /usr/local/lib
ENV MAGICK_HOME="/ImageMagick-7.0.10-14"
ENV PATH="$MAGICK_HOME/bin:$PATH"
ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH:+$LD_LIBRARY_PATH:}$MAGICK_HOME/lib"

# FROM git://github.com/Trekky12/kburns-slideshow.git
COPY ./deps/kburns-slideshow.tar.gz /
RUN tar xvzf kburns-slideshow.tar.gz
COPY ./otto/examples/config_otto.json /kburns-slideshow/config.json
RUN chmod +x /kburns-slideshow/main.py && ln -s /kburns-slideshow/main.py /usr/local/bin/kburns


RUN DEBIAN_FRONTEND=noninteractive apt-get install -y ttf-mscorefonts-installer && fc-cache -f && mkdir ~/.fonts
COPY ./deps/segoeuibl.ttf /usr/share/fonts/
RUN fc-cache -f

RUN pip3 install \
  fastapi \
  uvicorn \
  pydantic \
  typing \
  jinja2

WORKDIR /opt/code
# COPY ./deps/*.mp3 audios/
# COPY ./deps/*.mp4 videos/

#CMD ["python3"]
ENTRYPOINT ["uvicorn", "main:app", "--reload"]
CMD ["--host", "0.0.0.0", "--port", "80"]
