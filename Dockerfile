FROM python:3.8-alpine
 
ENV PYTHONUNBUFFERED 1
COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache postgresql-client jpeg-dev \
	&& apk add --update --no-cache --virtual .tmp-build-deps \ 
    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev \
	&& pip install -r /requirements.txt \
	&& apk del .tmp-build-deps
RUN mkdir /app 
COPY ./app /app
WORKDIR /app