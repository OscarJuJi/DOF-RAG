# DOF-RAG

Local document search and Spanish-language questions over the Diario Oficial de la
Federación. The Vue interface is served as a production build by Nginx. FastAPI
provides accounts, document retrieval, and generation. SQLite stores users,
revocable sessions, document text, and vectors in a persistent Docker volume.

The local deployment uses Ollama with `qwen3:8b` and
`qwen3-embedding:0.6b`. It does not require API keys, cloud accounts, trial credits,
OpenAI, Pinecone, Azure, or a hosted vector database. Models and dependencies must
be downloaded once. Inference and document storage run on this computer.

## Start locally on Windows

Requirements: Docker Desktop with its Linux engine running, PowerShell 7, and
[Ollama for Windows](https://ollama.com/download/windows). The default models fit
this project's development machine (32 GB RAM and an RTX 3070 with 8 GB VRAM).
CPU-only execution is possible but slower.

From the repository root:

```powershell
pwsh -File ./scripts/Start-Local.ps1
```

The script creates `.env` with a random administrator password if it does not
exist, downloads missing models, builds and starts the services, and indexes the
bundled PDF. Open:

- Application: <http://localhost:8080>
- Backend health: <http://localhost:8000/health>
- API documentation: <http://localhost:8000/docs>
- Local password-recovery mailbox: <http://localhost:8025>

Sign in as `admin@dof.local` using `ADMIN_PASSWORD` from the root `.env`.
The initial credentials only create the administrator when the database is empty;
editing `.env` does not change an existing account's password. Use the recovery
flow to change an existing password. Mailpit receives recovery emails locally;
messages are not sent to an external inbox or SMS provider.

All published ports bind to `127.0.0.1`. This deployment is for this computer and
is not configured for public internet exposure. The HTTP session cookie uses
HttpOnly and SameSite=Strict; add HTTPS and secure cookies before any remote deployment.
Only administrators can create, list, or delete other users. Passwords use scrypt,
session tokens are stored as hashes, and recovery codes expire with attempt limits.

## Operations

```powershell
# Start existing images without rebuilding or reindexing.
pwsh -File ./scripts/Start-Local.ps1 -SkipBuild -SkipIndex

# Update the document index without changing images.
docker compose exec -T backend python -m capidofchat_api.local_rag

# Status and logs.
docker compose ps
docker compose logs --tail 100 backend frontend

# Stop services while keeping all data.
pwsh -File ./scripts/Stop-Local.ps1
```

Services restart when Docker Desktop starts again. Ollama must also be running.
The default Compose configuration connects to native Ollama through
`host.docker.internal:11434`, so it reuses the Windows GPU and downloaded models.
Configure `OLLAMA_URL` in the root `.env` if your Ollama server uses another address.

The named volumes `dof-rag_app-data` and `dof-rag_mail-data` persist across image
rebuilds and container restarts. `docker compose down -v` deletes these databases;
do not use it for routine shutdown. Keep `.env` and volume backups private.
The older `Backend/.env` is ignored and is not passed to the local services.

## Document scope

The separate [DOF MCP connector](MCP/README.md) downloads the official editions
from 2024 onward as plain-text files and exposes live API queries and local
full-text search at `http://localhost:8001/mcp`. Run
`pwsh -File ./scripts/Sync-Dof.ps1` to import or resume the archive.
Text files, originals and the coverage manifest are stored in `data/dof/` and
ignored by Git. This archive does not automatically replace the GUI vector index.

The bundled seed is the April 3, 2024 DOF edition (240 pages), not the latest DOF.
Place additional PDF or UTF-8 text files in `documents/` and run the index command.
Scanned PDFs need OCR first. Identical files are deduplicated by content hash.
Existing indexed editions are retained as a historical archive even if their source
files are removed. A missing source file cannot be downloaded from the interface.

Queries return retrieved page references. Generated document overviews use a
selection of up to ten excerpts and explicitly identify themselves as partial.
There is no automatic latest-edition ingestion, legal-validity verification, or
live regulatory-change subscription. Local model responses still need review.

## Validation

```powershell
cd Frontend
npm ci
npm run lint
npm run format:check
npm run build
cd ..

# Account security and API contracts in an isolated temporary database.
docker compose run --rm --no-deps -v "${PWD}/Backend/tests:/tests:ro" backend python -m unittest discover -s /tests -v

# Live login, document download, and RAG query through the production proxy.
docker compose run --rm --no-deps -v "${PWD}/Backend/tests:/tests:ro" backend python /tests/smoke_local.py --query
```

The live smoke test reads the initial administrator credentials from the container
environment. If the administrator's password has changed, use the UI for live
verification; the isolated regression tests remain independent of that account.

The legacy cloud entry point remains in `Backend/Docker/capidofchat_api/server.py`
for reference. Compose uses `local_server.py` and `requirements-local.txt` exclusively.

Upstream references: [Ollama local authentication](https://docs.ollama.com/api/authentication),
[Qwen3](https://ollama.com/library/qwen3),
[multilingual embeddings](https://ollama.com/library/qwen3-embedding:0.6b),
[Mailpit](https://mailpit.axllent.org/docs/install/docker/).
