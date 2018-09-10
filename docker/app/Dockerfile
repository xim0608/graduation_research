FROM python:3.6.4-slim-stretch

RUN apt-get update && \
    apt-get -y install sudo \
    git \
    gcc \
    g++ \
    make \
    curl \
    xz-utils \
    liblzma-dev \
    file \
    mecab-ipadic \
    mecab-ipadic-utf8 \
    mysql-client \
    default-libmysqlclient-dev

RUN mkdir -p /opt/downloads && \
    cd /opt/downloads && \
    git clone https://github.com/taku910/mecab.git && \
    git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git

RUN cd /opt/downloads/mecab/mecab && \
    ./configure  --enable-utf8-only && \
    make && \
    make check && \
    make install

RUN apt-get -y install
RUN cd /opt/downloads/mecab-ipadic-neologd && \
    ./bin/install-mecab-ipadic-neologd -n -y

RUN pip install pipenv

RUN mkdir /app

COPY ./Pipfile /app
COPY ./Pipfile.lock /app
WORKDIR /app

RUN pipenv install

ENTRYPOINT ["pipenv", "run"]

CMD ["python", "main.py"]
