FROM python:3.11-slim

WORKDIR /app

COPY Docker/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY Docker/capidofchat_api ./capidofchat_api

EXPOSE 8000

CMD ["sh", "-c", "uvicorn capidofchat_api.server:app --host 0.0.0.0 --port ${PORT:-8000}"]
