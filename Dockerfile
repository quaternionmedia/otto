FROM dpokidov/imagemagick
WORKDIR /app

RUN apt update && apt install -y python3 python3-pip

RUN pip install -U pip uvicorn

COPY ./otto ./otto
COPY README.md .
COPY ./pyproject.toml .
COPY ./poetry.lock .

RUN pip install .

ENTRYPOINT python3 otto/main.py