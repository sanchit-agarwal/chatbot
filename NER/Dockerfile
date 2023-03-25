# syntax=docker/dockerfile:1
FROM python:slim

RUN apt-get update && apt-get install -y git

COPY . chatbot/ner

WORKDIR "chatbot/ner"

RUN python -m venv venv
RUN . venv/bin/activate
RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn

EXPOSE 5002

CMD gunicorn --bind 0.0.0.0:5002 app:app
