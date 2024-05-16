FROM python:3.10-alpine3.17
WORKDIR /usr/src/app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.3.0 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_HOME='/usr/src/app'

RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev \
    && apk add libffi-dev

RUN pip install --no-cache-dir poetry

# install dependencies
COPY poetry.lock pyproject.toml ./
RUN poetry config installer.max-workers 10
RUN poetry install
COPY --chmod=0755 docker-entrypoint.sh ./

ENTRYPOINT [ "/bin/sh", "docker-entrypoint.sh" ]