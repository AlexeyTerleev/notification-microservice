# poetry export --without-hashes --format=requirements.txt > requirements.txt
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update

COPY requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /usr/src/app
    
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

COPY ./app /usr/src/app

ENV PYTHONPATH /usr/src

CMD ["python", "main.py"]

