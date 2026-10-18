# Pinned by digest: `FROM python` meant whatever python:latest was on the day
# of the build, which reached 3.14 -- outside requires-python, and where
# setuptools is no longer bundled. Bump this deliberately.
FROM python:3.11-slim@sha256:90744cff8f32887f075c47d747a173ff333e9e98801667af93c357fa9f5e28ff AS base

# What rendering needs from the system: ImageMagick for text, cairo for the
# gizeh shapes, and fonts -- Open Sans is the templates' default, urw-base35
# provides the standard PostScript names (Courier, Helvetica, Times).
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        imagemagick libcairo2 fonts-open-sans fonts-urw-base35 \
    && rm -rf /var/lib/apt/lists/*

# moviepy hands text to ImageMagick as `@file`, which the distribution policy
# forbids. Remove that one rule, wherever this ImageMagick keeps its policy,
# rather than the whole policy: the rest still applies to the media it reads.
RUN for policy in /etc/ImageMagick-6/policy.xml /etc/ImageMagick-7/policy.xml; do \
        if [ -f "$policy" ]; then sed -i '/pattern="@\*"/d' "$policy"; fi; \
    done

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN pip install -U pip uvicorn


# The test suite, against this image's system dependencies:
#   docker build --target test -t otto-test . && docker run --rm otto-test
FROM base AS test
COPY pyproject.toml pdm.lock README.md ./
COPY otto otto
COPY tests tests
RUN pip install -e .[render,test] && mkdir -p data
CMD ["pytest", "-v"]


# The service (the default target).
FROM base AS app
COPY pyproject.toml pdm.lock README.md ./
COPY otto otto
RUN pip install .[render]
CMD ["uvicorn", "otto.main:app", "--host", "0.0.0.0", "--reload"]
