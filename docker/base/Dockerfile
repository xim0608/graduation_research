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

# compile mecab neologd
RUN apt-get -y install
RUN cd /opt/downloads/mecab-ipadic-neologd && \
    ./bin/install-mecab-ipadic-neologd -n -y

ENV JUMANPP_VERSION 1.02
ENV JUMAN_VERSION 7.01
ENV KNP_VERSION 4.19
# install jumanpp
RUN apt-get -y install wget \
    libboost-dev \
    google-perftools \
    libgoogle-perftools-dev \
    bzip2

RUN wget http://lotus.kuee.kyoto-u.ac.jp/nl-resource/jumanpp/jumanpp-${JUMANPP_VERSION}.tar.xz -O /tmp/jumanpp.tar.xz &&\
    tar xJvf /tmp/jumanpp.tar.xz -C /tmp &&\
    cd /tmp/jumanpp-${JUMANPP_VERSION} &&\
    ./configure --prefix=/usr/local/ && make && make install &&\
    rm -rf /tmp/* &&\
    rm -rf /var/cache/apk/*

# install JUMAN
RUN wget http://nlp.ist.i.kyoto-u.ac.jp/nl-resource/juman/juman-${JUMAN_VERSION}.tar.bz2 -O /tmp/juman.tar.bz2 &&\
    tar xf /tmp/juman.tar.bz2 -C /tmp &&\
    cd /tmp/juman-${JUMAN_VERSION} &&\
    ./configure --prefix=/usr/local/ && make && make install &&\
    rm -rf /tmp/* &&\
    rm -rf /var/cache/apk/* &&\
    apt-get update && apt-get install -y --fix-missing libjuman4

# install KNP
RUN apt-get install -y --fix-missing zlib1g-dev &&\
    wget http://nlp.ist.i.kyoto-u.ac.jp/nl-resource/knp/knp-${KNP_VERSION}.tar.bz2 -O /tmp/knp.tar.bz2 &&\
    tar xf /tmp/knp.tar.bz2 -C /tmp &&\
    cd /tmp/knp-${KNP_VERSION} / &&\
    ./configure --prefix=/usr/local/ --with-juman-prefix=/usr/local/ && make && make install &&\
    rm -rf /tmp/* &&\
    rm -rf /var/cache/apk/*

RUN pip install pipenv

CMD /bin/bash