# DOF MCP and plain-text archive

Read-only MCP server for the production SIDOF public API. No API key, paid
service, hosted model, or cloud account is required. The connector does not read
the application's administrator credentials. All tools are annotated read-only.

## Run and connect

From the repository root:

```powershell
docker compose up -d --build dof-mcp
```

Streamable HTTP endpoint: `http://localhost:8001/mcp`. This is an MCP protocol
endpoint, not a browser page or ordinary REST endpoint. Register that URL in an
MCP-compatible client. Only the loopback interface is published; host/origin
validation blocks DNS rebinding. Do not expose this unauthenticated local server
on a public interface.

For clients supporting stdio, use `client.example.json`; adjust the absolute
project directory if this repository moves. The stdio process is launched by the
client, so Docker Desktop must be running. No global client settings are changed
by this project.

| Tool | Purpose |
| --- | --- |
| `dof_list_editions` | Live MAT, VES and EXT editions for one ISO date |
| `dof_list_notes` | Live note metadata for every edition, paginated |
| `dof_get_note` | Live HTML note converted to plain text, paginated |
| `dof_archive_status` | Download coverage, errors and extraction warnings |
| `dof_archive_list` | Local editions and TXT paths, paginated |
| `dof_archive_search` | Local SQLite FTS5 search with dates and PDF page references |
| `dof_archive_read` | Local full-text pages with explicit continuation offsets |

No tool accepts arbitrary URLs, filesystem paths, SQL, shell commands, or secrets.
Tools do not start bulk downloads or modify upstream publications. Retrieved text
is source data, never instructions. Search matches all supplied words and ignores
accent differences; it does not infer legal validity.

## Download from 2024 to today

```powershell
pwsh -File ./scripts/Sync-Dof.ps1

# Reproduce a fixed inclusive range.
pwsh -File ./scripts/Sync-Dof.ps1 -StartDate 2024-01-01 -EndDate 2026-09-10

# Recheck previously successful calendar responses for upstream changes.
pwsh -File ./scripts/Sync-Dof.ps1 -Refresh
```

"Today" uses UTC-06 (Mexico City/Guatemala), evaluated once at startup.
The current request's cutoff is September 10, 2026. This is a finite import,
not a scheduled daily subscription. The downloader checks every calendar date,
including weekends and holidays, and combines the yearly catalog with all daily
edition groups. Empty daily responses are cross-checked with the notes endpoint.
`no_editions_reported` describes those API responses, not independently proven
absence of publication. Unavailable or malformed responses remain errors and
are never silently marked as empty days.

All network requests use verified TLS against the production
`sidof.segob.gob.mx` host; no QA host or certificate-validation bypass is used.
A process-wide limiter allows up to two requests per second. Downloads use a
bounded worker pool, retries, exponential backoff and `Retry-After`. The full
archive can take a long time, especially OCR. Interrupted runs resume by edition
ID and retained PDF; successful existing files are not downloaded again.
A file lock prevents concurrent bulk imports of the same archive.

The initial backfill was launched as the background container
`dof-rag-archive-2024`, with up to three restarts on failure. Keep the computer
and Docker Desktop running. Inspect its progress with:

```powershell
docker logs --tail 20 dof-rag-archive-2024
Get-Content ./data/dof/status.json
```

To interrupt that job without deleting any downloaded data, run
`docker stop dof-rag-archive-2024`. Resume later with `Sync-Dof.ps1`; it retains
completed editions. The MCP server and GUI are separate from this finite job.

## Local outputs

Everything below `data/` is ignored by Git. Originals and text remain on the host:

```text
data/dof/
  text/2024/YYYY-MM-DD_MAT_ID.txt
  text/2025/...
  text/2026/...
  pdf/2024/YYYY-MM-DD_MAT_ID.pdf
  pdf/2025/...
  pdf/2026/...
  responses/                 Original API discovery responses
  catalog.sqlite3           Edition/page catalog and full-text search
  manifest.json             File paths, hashes, coverage, warnings and failures
  status.json               Compact progress report
```

There is one UTF-8 TXT per complete **edition**, containing all its extracted
PDF pages, not just a summary or a title list. Each TXT includes source metadata
and explicit PDF page markers. PDF page positions can differ from printed page
numbers. Each file has a SHA-256 recorded in the manifest. The original public
documents are not redacted or rewritten.

Poppler extracts text while retaining table spacing. Pages with fewer than 80
alphanumeric characters are passed through local Spanish/English Tesseract OCR.
Pages that still have little text and API/PDF page-count discrepancies are
flagged `needs_review`; these may include blank pages, maps, signatures, or source
metadata inconsistencies. OCR can make mistakes. Charts, images embedded in
otherwise readable pages, and externally linked attachments are not fully
transcribed. The official PDF remains the source of truth. A complete download
does not imply flawless transcription or independent verification of DOF coverage.

`completed` means all discovered editions in the run were converted with no
recorded extraction warning; `completed_with_warnings` means all were converted
but some require review. `incomplete` indicates failed dates or editions; rerun
the same command to retry. `running` and `interrupted` must not be reported as
complete. Manifests refresh every 25 discovered dates or 10 processed editions.
The MCP status tool reads the live database between those refreshes.

The MCP archive is independent of the GUI's vector index. It is searchable as
soon as editions are extracted, without generating embeddings for hundreds of
thousands of pages. This operation does **not** silently reindex the existing
Ollama RAG application or change its Spanish GUI.

## Validation

```powershell
docker compose run --rm --no-deps -v "${PWD}/MCP/tests:/tests:ro" dof-mcp python -m unittest discover -s /tests -v
docker compose run --rm --no-deps -v "${PWD}/MCP/tests:/tests:ro" dof-mcp python /tests/smoke_mcp.py
docker compose run --rm --no-deps -v "${PWD}/MCP/tests:/tests:ro" dof-mcp python /tests/smoke_mcp.py --stdio

# Check every output hash and page count against the manifest.
docker compose run --rm --no-deps dof-mcp python -m dof_mcp.audit --start 2024-01-01 --end 2026-09-10
```

Tests use temporary databases and mock responses. The smoke check uses the
actual MCP handshake, public DOF API, and the January 2, 2024 local edition.
It also checks rejection of unexpected hosts/origins.
The audit writes `data/dof/audit.json` and returns a nonzero exit code for missing
dates, pending/failed editions, missing files, or checksum/page-count mismatches.
Extraction warnings are reported separately from download/integrity failures.

Official references: [SIDOF open data](https://sidof.segob.gob.mx/datos_abiertos),
[edition API](https://sidof.segob.gob.mx/datos_abiertos/getPDF/65),
[document API](https://sidof.segob.gob.mx/datos_abiertos/getPDF/43),
[note API](https://sidof.segob.gob.mx/datos_abiertos/getPDF/57),
[DOF source-use notice](https://sidof.segob.gob.mx/avisoLegal),
[official MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk).
