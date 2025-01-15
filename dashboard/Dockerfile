FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

ENV REDIS_IP=0.0.0.0

EXPOSE 8050

CMD ["python", "app.py"]
