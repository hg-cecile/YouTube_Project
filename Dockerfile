FROM ubuntu:latest
LABEL maintainer="Yoan"

RUN apt update && apt-get install -y zip && apt-get install -y vim && apt-get install -y python3 && apt-get install -y python3-pip

WORKDIR /app
COPY . /app

# je dis a dock que mon conteneur ecoute sur le port 5000 (ne mappe pas le port)
EXPOSE 5000

RUN python3 -m pip install -r requirements.txt

CMD bash -c ". run.sh"

