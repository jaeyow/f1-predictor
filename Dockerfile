# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster as builder

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

# Core dependencies
RUN apt-get update && apt-get install -y curl sudo

# Node
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
RUN sudo apt-get install -y nodejs

WORKDIR /

COPY . /app/

# install chrome
RUN apt-get install wget -y
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | tee /etc/apt/sources.list.d/google-chrome.list
RUN apt update -y
RUN apt install -y google-chrome-stable

RUN npm install -g serverless

WORKDIR /app/flask-api

RUN sls plugin install -n serverless-wsgi

ARG SLS_KEY=dummykey

ARG SLS_SECRET=dummysecret

ENV AWS_ACCESS_KEY_ID=${SLS_KEY}

ENV AWS_SECRET_ACCESS_KEY=${SLS_SECRET}

RUN sls config credentials --provider aws --key ${AWS_ACCESS_KEY_ID}  --secret ${AWS_SECRET_ACCESS_KEY}

WORKDIR /app
