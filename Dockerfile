FROM python:3.9-alpine3.16 

COPY requirements.txt /temp/requirements.txt
COPY music_app /music_app
WORKDIR /music_app

EXPOSE 8000

RUN apk add postgresql-client build-base postgresql-dev

RUN pip install -r /temp/requirements.txt
RUN adduser --disabled-password music_app-user

USER music_app-user

