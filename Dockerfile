FROM alpine:edge
RUN sed -e 's;^#http\(.*\)/v3.9/community;http\1/v3.9/community;g' -i /etc/apk/repositories
RUN apk add --no-cache --update \
    git \
    dash \
    libffi-dev \
    openssl-dev \
    bzip2-dev \
    zlib-dev \
    readline-dev \
    sqlite-dev \
    build-base \
    python3 \
    redis \
    libxslt-dev \
    libxml2 \
    libxml2-dev \
    py-pip \
    libpq \
    build-base \
    linux-headers \
    jpeg-dev \
    curl \
    neofetch \
    sudo \
    gcc \
    python-dev \
    python3-dev \
    musl \
    sqlite \
    figlet \
    libwebp-dev

RUN pip3 install --upgrade pip setuptools
RUN  sed -e 's;^# \(%wheel.*NOPASSWD.*\);\1;g' -i /etc/sudoers
RUN adduser jarvis --disabled-password --home /home/jarvis
RUN adduser jarvis wheel
USER jarvis
RUN mkdir /home/jarvis/instance
RUN git clone -b master https://git.stykers.moe/scm/~stykers/jarvis.git /home/jarvis/instance
WORKDIR /home/jarvis/instance
COPY ./jarvis.session ./config.env /home/jarvis/instance/
RUN sudo pip3 install -r requirements.txt
RUN sudo chmod -R 777 /home/jarvis/instance
CMD ["dash","utils/entrypoint.sh"]
