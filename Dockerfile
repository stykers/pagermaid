FROM alpine:edge
RUN sed -e 's;^#http\(.*\)/v3.9/community;http\1/v3.9/community;g' -i /etc/apk/repositories
RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/testing/" >> /etc/apk/repositories
RUN apk add --no-cache --update \
    git \
    dash \
    libffi-dev \
    tesseract-ocr \
    openssl-dev \
    bzip2-dev \
    zlib-dev \
    readline-dev \
    sqlite-dev \
    build-base \
    fortune \
    figlet \
    python3 \
    redis \
    libxslt-dev \
    libxml2 \
    libxml2-dev \
    py-pip \
    py-virtualenv \
    libpq \
    build-base \
    linux-headers \
    freetype-dev \
    jpeg-dev \
    curl \
    neofetch \
    sudo \
    gcc \
    python-dev \
    python3-dev \
    musl \
    imagemagick \
    sqlite \
    figlet \
    libwebp-dev \
    zbar
RUN sed -e 's;^# \(%wheel.*NOPASSWD.*\);\1;g' -i /etc/sudoers
RUN adduser jarvis --disabled-password --home /jarvis
RUN adduser jarvis wheel
USER jarvis
RUN mkdir /jarvis/instance
RUN git clone -b master https://git.stykers.moe/scm/~stykers/jarvis.git /jarvis/instance
WORKDIR /jarvis/instance
COPY ./jarvis.session ./config.env /jarvis/instance/
RUN sudo chown jarvis:jarvis /jarvis/instance/config.env
RUN sudo chown jarvis:jarvis /jarvis/instance/jarvis.session
RUN python3 -m virtualenv venv
RUN source venv/bin/activate; pip3 install -r requirements.txt
CMD ["bash","utils/entrypoint.sh"]
