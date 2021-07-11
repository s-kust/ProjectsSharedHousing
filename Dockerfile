# FROM python:3.8-alpine
FROM python:3.6.4-slim-jessie
 
ENV PYTHONUNBUFFERED 1
COPY ./requirements.txt /requirements.txt
RUN pip install --upgrade pip \
	&& pip install -r /requirements.txt \
	&& mkdir /app 
# RUN mkdir /app 
COPY ./app /app
WORKDIR /app