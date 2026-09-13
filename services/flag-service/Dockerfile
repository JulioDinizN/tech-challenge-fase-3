FROM python:3.11-slim

# Apply available distribution security fixes before installing application packages.
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
RUN useradd --uid 10001 --create-home --shell /usr/sbin/nologin appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

USER 10001
EXPOSE 8002
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8002} app:app"]
