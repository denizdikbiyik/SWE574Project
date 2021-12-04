FROM python:3.10.0-alpine3.15

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /SWE573PROJECT-MAIN


# Pillow dependencies
RUN apk add --no-cache jpeg-dev zlib-dev
RUN apk add --no-cache --virtual .build-deps build-base linux-headers \
    && pip install Pillow

# install psycopg2 dependencies

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev\
    && apk -U upgrade\
    && apk add --no-cache libffi-dev openssl-dev

COPY  ./requirements.txt .
RUN pip install --upgrade pip
RUN pip3 install --upgrade setuptools

RUN pip install -r requirements.txt

# copy project
COPY . .