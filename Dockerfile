FROM python
WORKDIR /app

RUN pip install -U pip uvicorn

COPY pyproject.toml pdm.lock README.md ./
COPY otto otto

ENV BEZIER_NO_EXTENSION=true
RUN pip install .[render]

CMD uvicorn otto.main:app --host 0.0.0.0 --reload
