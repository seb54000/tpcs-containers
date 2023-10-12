FROM ubuntu:latest

WORKDIR /app/vikunja

RUN apt-get update
RUN apt-get install -y ?...?

ADD https://dl.vikunja.io/api/??.........??

RUN unzip ??.........?? -d vikunja

ENTRYPOINT ["/app/vikunja/??......???"]