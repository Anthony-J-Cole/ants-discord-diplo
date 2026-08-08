FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

run mkdir -p /data
VOLUME ["/data"]

ENV DB_PATH=/data/diplomacy.db
ENV DEFAULT_MAP_PATH=/app/diplo_engine/maps/test_map.json
ENV PYTHONBUFFERED=1

CMD ["python", "-m", "main"]