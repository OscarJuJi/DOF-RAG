"""Verify local archive coverage, file checksums, and stored page counts."""

import argparse
import hashlib
import json
from datetime import timedelta

from .archive import Archive, atomic_text, now
from .client import parse_date


def audit(start_date: str, end_date: str) -> dict:
    start, end = parse_date(start_date), parse_date(end_date)
    if start > end:
        raise ValueError("The start date must precede the end date.")
    archive = Archive()
    with archive.connection() as db:
        days = {
            row["date"]: row["status"]
            for row in db.execute(
                "SELECT date,status FROM days WHERE date BETWEEN ? AND ?",
                (start_date, end_date),
            )
        }
        editions = [
            dict(row)
            for row in db.execute(
                "SELECT editions.*,COUNT(pages.id) AS stored_pages FROM editions "
                "LEFT JOIN pages ON pages.edition_id=editions.id WHERE editions.date BETWEEN ? AND ? "
                "GROUP BY editions.id ORDER BY editions.date,editions.id",
                (start_date, end_date),
            )
        ]
    missing_dates = []
    failed_dates = []
    for offset in range((end - start).days + 1):
        day = str(start + timedelta(days=offset))
        if day not in days:
            missing_dates.append(day)
        elif days[day] == "error":
            failed_dates.append(day)
    errors = []
    verified = 0
    pending = []
    warnings = []
    for item in editions:
        identifier = item["id"]
        if item["status"] not in {"complete", "needs_review"}:
            pending.append(
                {"id": identifier, "status": item["status"], "error": item["error"]}
            )
            continue
        if item["status"] == "needs_review":
            warnings.append(
                {
                    "id": identifier,
                    "low_text_pages": json.loads(item["low_text_pages"]),
                    "warning": item["error"],
                }
            )
        edition_errors = []
        for key, checksum in [("pdf_path", "sha256"), ("text_path", "text_sha256")]:
            path = (archive.root / item[key]).resolve()
            if not path.is_relative_to(archive.root) or not path.is_file():
                edition_errors.append(f"Missing or unsafe {key}.")
                continue
            with path.open("rb") as source:
                if hashlib.file_digest(source, "sha256").hexdigest() != item[checksum]:
                    edition_errors.append(f"Checksum mismatch for {key}.")
        if item["stored_pages"] != item["pages"]:
            edition_errors.append(
                "Stored page count differs from extracted PDF page count."
            )
        if edition_errors:
            errors.append({"id": identifier, "errors": edition_errors})
        else:
            verified += 1
    result = {
        "checked_at": now(),
        "start_date": start_date,
        "end_date": end_date,
        "expected_calendar_days": (end - start).days + 1,
        "checked_calendar_days": len(days),
        "discovered_editions": len(editions),
        "verified_editions": verified,
        "missing_dates": missing_dates,
        "failed_dates": failed_dates,
        "pending_editions": pending,
        "integrity_errors": errors,
        "extraction_warnings": warnings,
        "download_complete": not (missing_dates or failed_dates or pending or errors),
        "warning": "Verification covers API-discovered editions and local integrity, not independent DOF completeness or OCR accuracy.",
    }
    atomic_text(
        archive.root / "audit.json", json.dumps(result, ensure_ascii=False, indent=2)
    )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    args = parser.parse_args()
    result = audit(args.start, args.end)
    print(
        json.dumps(
            {
                key: len(value) if isinstance(value, list) else value
                for key, value in result.items()
            },
            indent=2,
        )
    )
    if not result["download_complete"]:
        raise SystemExit(2)
