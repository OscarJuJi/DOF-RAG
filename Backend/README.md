# CapiDOFChat backend

For the local production stack, use `scripts/Start-Local.ps1` from the repository
root. It runs `Docker/Dockerfile.local` with SQLite and native Ollama; no API keys
are required. See the [root README](../README.md) for accounts, data, and operations.

The following commands apply only to the legacy cloud-backed entry point:

Copy `.env.example` to `.env` and set the required credentials. Never commit `.env`.

Build and run the API from this directory:

```sh
docker build -f Docker/Dockerfile -t capidofchat-api .
docker run --env-file .env -p 8000:8000 capidofchat-api
```

The API exposes the following endpoints:

- `GET /health`
- `POST /query/invoke`
- `POST /notification/invoke`
- `POST /summary/invoke`
- `POST /specific/invoke`

Each `POST` endpoint accepts an `input` object and returns `{ "output": "..." }`.
