"""Download an inclusive date range without discarding resumable progress."""

import argparse
import fcntl
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import timedelta

from .archive import Archive, now, today
from .client import DofClient, api_date, parse_date


def synchronize(start_date: str, end_date: str, workers=2, refresh=False) -> dict:
    start, end = parse_date(start_date), parse_date(end_date)
    if start < parse_date("2024-01-01") or end < start or end > today():
        raise ValueError(
            "Dates must be between 2024-01-01 and today (UTC-06), inclusive."
        )
    if not 1 <= workers <= 4:
        raise ValueError("Use between one and four workers.")
    archive = Archive()
    client = DofClient()
    with (archive.root / "sync.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError(
                "Another archive synchronization is already running."
            ) from error
        with archive.connection() as db:
            db.execute(
                "UPDATE runs SET status='interrupted',finished_at=? WHERE status='running'",
                (now(),),
            )
            run_id = db.execute(
                "INSERT INTO runs(start_date,end_date,started_at,status) VALUES(?,?,?,'running')",
                (start_date, end_date, now()),
            ).lastrowid
        try:
            for year in range(start.year, end.year + 1):
                payload = client.json(f"/diarios/{year}")
                archive.save_response(str(year) + "-calendar", payload)
                for item in payload.get("ListaDiarios") or []:
                    publication_date = api_date(item["fecha"])
                    if start_date <= publication_date <= end_date:
                        archive.register_edition(
                            {
                                "id": item["codDiario"],
                                "date": publication_date,
                                "edition": item["codEdicion"],
                            }
                        )
            dates = [
                start + timedelta(days=offset)
                for offset in range((end - start).days + 1)
            ]
            print(
                f"Discovering {len(dates)} calendar days: {start_date} through {end_date}.",
                flush=True,
            )
            with ThreadPoolExecutor(max_workers=workers) as pool:
                futures = {
                    pool.submit(archive.discover_day, client, day, refresh): day
                    for day in dates
                }
                for completed, future in enumerate(as_completed(futures), 1):
                    future.result()
                    if completed % 25 == 0 or completed == len(dates):
                        archive.export_manifest()
                        print(
                            f"Discovered {completed}/{len(dates)} days. {json.dumps(archive.status()['editions'])}",
                            flush=True,
                        )
            with archive.connection() as db:
                identifiers = [
                    row[0]
                    for row in db.execute(
                        "SELECT id FROM editions WHERE date BETWEEN ? AND ? ORDER BY date,id",
                        (start_date, end_date),
                    )
                ]
            print(
                f"Downloading and extracting {len(identifiers)} editions.", flush=True
            )
            with ThreadPoolExecutor(max_workers=workers) as pool:
                futures = {
                    pool.submit(archive.import_edition, client, identifier): identifier
                    for identifier in identifiers
                }
                for completed, future in enumerate(as_completed(futures), 1):
                    result = future.result()
                    print(
                        f"Edition {futures[future]}: {result}. {completed}/{len(identifiers)}",
                        flush=True,
                    )
                    if completed % 10 == 0 or completed == len(identifiers):
                        archive.export_manifest()
            with archive.connection() as db:
                errors = db.execute(
                    "SELECT COUNT(*) FROM days WHERE status='error' AND date BETWEEN ? AND ?",
                    (start_date, end_date),
                ).fetchone()[0]
                errors += db.execute(
                    "SELECT COUNT(*) FROM editions WHERE status NOT IN ('complete','needs_review') AND date BETWEEN ? AND ?",
                    (start_date, end_date),
                ).fetchone()[0]
                reviews = db.execute(
                    "SELECT COUNT(*) FROM editions WHERE status='needs_review' AND date BETWEEN ? AND ?",
                    (start_date, end_date),
                ).fetchone()[0]
                state = (
                    "incomplete"
                    if errors
                    else "completed_with_warnings"
                    if reviews
                    else "completed"
                )
                db.execute(
                    "UPDATE runs SET status=?,finished_at=? WHERE id=?",
                    (state, now(), run_id),
                )
        except BaseException as error:
            with archive.connection() as db:
                db.execute(
                    "UPDATE runs SET status='interrupted',error=?,finished_at=? WHERE id=?",
                    (str(error)[:2000], now(), run_id),
                )
            raise
        finally:
            client.close()
            archive.export_manifest()
    return archive.status()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default="2024-01-01")
    parser.add_argument("--end", default=today().isoformat())
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Recheck successful historical date responses.",
    )
    args = parser.parse_args()
    result = synchronize(args.start, args.end, args.workers, args.refresh)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["latest_run"]["status"] == "incomplete":
        raise SystemExit(2)
