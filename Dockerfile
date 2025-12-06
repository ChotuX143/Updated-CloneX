FROM nikolaik/python-nodejs:python3.10-nodejs19

# prevent interactive prompts and disable apt Valid-Until check for archived repos
ENV DEBIAN_FRONTEND=noninteractive
RUN echo 'Acquire::Check-Valid-Until "0";' > /etc/apt/apt.conf.d/99no-check-valid-until && \
    sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list && \
    sed -i '/security.debian.org/d' /etc/apt/sources.list && \
    apt-get update || (cat /etc/apt/sources.list && apt-get update) && \
    apt-get install -y --no-install-recommends ffmpeg aria2 ca-certificates && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
