FROM archlinux/base:latest
RUN pacman -Syu --needed --noconfirm \
    git \
    libffi \
    tesseract \
    openssl \
    bzip2 \
    zlib \
    readline \
    sqlite \
    fortune-mod \
    figlet \
    python-virtualenv \
    redis \
    libxslt \
    libxml2 \
    libpqxx \
    linux-api-headers \
    freetype2 \
    jpeg-archive \
    curl \
    wget \
    neofetch \
    sudo \
    gcc \
    gcc8 \
    imagemagick \
    libwebp \
    zbar \
    procps-ng
RUN sed -e 's;^# \(%wheel.*NOPASSWD.*\);\1;g' -i /etc/sudoers
RUN useradd jarvis -r -m -d /jarvis
RUN usermod -aG wheel,users jarvis
USER jarvis
RUN mkdir /jarvis/instance
RUN git clone -b master https://git.stykers.moe/scm/~stykers/jarvis.git /jarvis/instance
WORKDIR /jarvis/instance
COPY ./jarvis.session* ./config.env /jarvis/instance/
RUN sudo chown jarvis:jarvis /jarvis/instance/config.env
RUN sudo chown jarvis:jarvis /jarvis/instance/jarvis.session
RUN python3 -m virtualenv venv
RUN source venv/bin/activate; pip3 install -r requirements.txt
CMD ["sh","utils/entrypoint.sh"]
