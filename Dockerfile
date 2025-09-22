# Dockerfile (Flask + gunicorn)
FROM python:3.12-slim

WORKDIR /app

# System deps: certs for TLS to SMTP
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . ./

EXPOSE 8080
CMD ["gunicorn", "-w", "2", "-k", "gthread", "--threads", "8", "-b", "0.0.0.0:8080", "app:app"]
