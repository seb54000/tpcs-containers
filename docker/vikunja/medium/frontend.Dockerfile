FROM nginx:latest

WORKDIR /app

RUN apt-get update
RUN apt-get install -y unzip

ADD https://dl.vikunja.io/frontend/<ZIP_version _reference> ./
COPY <conifguration file nginx> /etc/nginx/conf.d/

RUN unzip <ZIP_version _reference> -d vikunja

#v1 Docker
RUN sed -i 's/window.API_URL = '\''\/api\/v1'\''/window.API_URL = '\''localhost:3456\/api\/v1'\''/g' vikunja/index.html

#v2 Kube
# ENV VIKUNJA_API_URL /api/v1
# RUN sed -ri "s:^(\s*window.API_URL\s*=)\s*.+:\1 '${VIKUNJA_API_URL}':g" vikunja/index.html
