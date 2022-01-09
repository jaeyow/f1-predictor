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
# RUN echo "NODE Version:" && node --version
# RUN echo "NPM Version:" && npm --version

WORKDIR /

COPY . /app/

RUN ls -la

RUN npm install -g serverless

WORKDIR /app/flask-api

RUN ls -la && pwd

RUN sls plugin install -n serverless-wsgi

ARG SLS_KEY=dummykey

ARG SLS_SECRET=dummysecret

ENV ENV_SLS_KEY=${SLS_KEY}

ENV ENV_SLS_SECRET=${SLS_SECRET}

RUN sls config credentials --provider aws --key ${ENV_SLS_KEY}  --secret ${ENV_SLS_SECRET}

# install chrome
RUN apt-get install wget -y
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | tee /etc/apt/sources.list.d/google-chrome.list
RUN apt update -y
RUN apt install -y google-chrome-stable

WORKDIR /app

# Run scripts
RUN python './scripts/1-ergast-to-mongo.py'