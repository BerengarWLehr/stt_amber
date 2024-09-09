FROM python:3.11-bookworm

COPY requirements.txt /
RUN \
  python3 -m pip install -r requirements.txt && rm -rf ~/.cache && rm requirements.txt

ADD secret.key lib /app/lib

WORKDIR /app/lib
ENV APP_PORT=80
ENV APP_HOST=0.0.0.0
ENTRYPOINT ["python3", "main.py"]
