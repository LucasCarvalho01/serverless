FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

COPY runtime.py /usr/src/app/
COPY requirements.txt /usr/src/app/

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /opt

EXPOSE 6379

CMD ["python", "runtime.py"]
