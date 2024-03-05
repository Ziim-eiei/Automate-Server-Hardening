FROM node:18 as build-front
WORKDIR /build
COPY ./ash/ash-front/ ./
RUN npm i && npm run build

FROM ubuntu:latest
ENV DEBIAN_FRONTEND=noninteractive

#install & update
RUN apt-get update -y && \
    apt-get install -y \
    curl \
    gnupg \
    wget \
    ca-certificates \
    nginx \
    python3 \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://pgp.mongodb.com/server-7.0.asc | \
    gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg \
    --dearmor && echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends mongodb-org && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# add user to run app    
ARG USER=ash
RUN useradd -m -s /bin/bash $USER && \
    PASSWORD=$(openssl rand -base64 20) && \
    echo "$USER:$PASSWORD" | chpasswd && \
    chown -R ash:ash /var/log/nginx/ && \
    chown -R ash:ash /var/lib/nginx/ && \
    touch /run/nginx.pid && chown -R ash:ash /run/nginx.pid && \
    chown -R ash:ash /var/lib/mongodb && \
    chown -R ash:ash /var/log/mongodb

# set up app
WORKDIR /ash
COPY --from=build-front /build/dist ./front
COPY ./ash/app ./back
COPY ./ash/.devcontainer/requirements.txt ./back/requirements.txt
RUN pip install -r ./back/requirements.txt && pip install ansible pywinrm
RUN chown -R ash:ash /ash
USER $USER
COPY ash.conf /etc/nginx/conf.d/default.conf
COPY ./ash/.devcontainer/mongo/cis-benchmark-new.json /home/ash/cis-benchmark-new.json
COPY --chmod=777 docker-entrypoint.sh /ash/docker-entrypoint.sh
ENTRYPOINT ["/ash/docker-entrypoint.sh"]
EXPOSE 80 8000