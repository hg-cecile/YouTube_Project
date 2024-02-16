FROM ubuntu:latest
LABEL maintainer="Yoan"

RUN apt update && apt-get install -y zip && apt-get install -y vim && apt-get install -y python3 && apt-get install -y python3-pip

WORKDIR /app
COPY . /app

EXPOSE 5150

RUN python3 -m pip install -r requirements.txt

CMD bash -c ". launch.sh"
