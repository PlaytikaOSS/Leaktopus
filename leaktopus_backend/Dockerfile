FROM golang:alpine AS builder

RUN apk update && apk add --no-cache git
ENV GOBIN /go/bin

#RUN export CGO_ENABLED=0 && go get github.com/eth0izzle/shhgit
RUN export CGO_ENABLED=0 && go install github.com/eth0izzle/shhgit@latest

FROM python:3.10-slim-buster as sqlite
RUN apt-get update \
  && apt-get install -y build-essential tk-dev mesa-common-dev wget git --no-install-recommends \
  && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
  && apt-get clean


# Update sqlite3 to latest version.
# @see https://github.com/swagcharm/latest-sqlite-for-python-images
RUN \
  wget \
    -O sqlite.tar.gz \
    https://www.sqlite.org/src/tarball/sqlite.tar.gz?r=release \
    && \
    tar xvfz sqlite.tar.gz

RUN \
  ./sqlite/configure --prefix=/sqlite && \
  make && \
  make install

FROM python:3.10-slim-buster as app
LABEL maintainer="Rotem Reiss <rotemr@playtika.com>"

WORKDIR /app

RUN apt-get update \
  && apt-get install -y build-essential tk-dev mesa-common-dev wget git --no-install-recommends \
  && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
  && apt-get clean \
  && useradd --create-home python \
  && mkdir -p /home/python/.cache/pip && chown python:python -R /home/python /app


ENV LD_PRELOAD="/usr/lib/libsqlite3.so"

RUN git config --system core.longpaths true

USER python

COPY --chown=python:python requirements*.txt ./
COPY --chown=python:python bin/ ./bin
# Directory for the SQLite DB.
COPY --chown=python:python db/ /db
# Directory for the temp data (e.g. clones).
COPY --chown=python:python data/ /data

COPY --from=sqlite --chown=python:python /sqlite/bin/sqlite3 /usr/local/bin
COPY --from=sqlite --chown=python:python /sqlite/lib/* /usr/lib/

RUN --mount=type=cache,target=/root/.cache chmod 0755 bin/* && bin/pip3-install

ARG FLASK_ENV="production"
ENV FLASK_ENV="${FLASK_ENV}" \
    FLASK_APP="leaktopus.app" \
    FLASK_SKIP_DOTENV="true" \
    PYTHONUNBUFFERED="true" \
    PYTHONPATH="." \
    PATH="${PATH}:/home/python/.local/bin" \
    USER="python" \
    DB_PATH="/db/leaktopus.sqlite"


COPY --chown=python:python . .

#RUN if [ "${FLASK_ENV}" != "development" ]; then \
#  ln -s /public /app/public && flask digest compile && rm -rf /app/public; fi

# Add
COPY --from=builder --chown=python:python /go/bin/shhgit /usr/local/bin
ENTRYPOINT ["/app/bin/docker-entrypoint-web"]

EXPOSE 8000

CMD ["gunicorn", "-c", "python:config.gunicorn", "leaktopus.app:create_app()"]
