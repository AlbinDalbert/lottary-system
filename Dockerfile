FROM python:3.12-slim

RUN apt-get update && apt-get install -y gosu && rm -rf /var/lib/apt/lists/*

RUN groupadd -r app && useradd --no-log-init -r -g app app

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x start.sh

RUN mkdir -p /app/instance && chown -R app:app /app && chmod -R 755 /app

CMD ["./start.sh"]
