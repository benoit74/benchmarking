FROM python:3.11.5-slim-bookworm

WORKDIR /app

COPY uploader.py requirements.txt /app/

RUN python -m pip install --no-cache-dir -U \
      pip

RUN python -m pip install -r requirements.txt

ENTRYPOINT ["python", "/app/uploader.py"]