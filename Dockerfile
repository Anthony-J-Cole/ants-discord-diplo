FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY diplo_engine/ ./diplo_engine
copy discord_bot/ ./discord_bot

run mkdir -p /data
VOLUME ["/data"]

ENV DB_PATH=/data/diplomacy.db
ENV DEFAULT_MAP_PATH=/app/diplo_engine/maps/map_test.json
ENV PYTHONBUFFERED=1


CMD ["python", "-m", "discord_bot.main"]