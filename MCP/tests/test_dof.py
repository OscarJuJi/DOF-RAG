import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import Mock, patch

import httpx
from dof_mcp.archive import Archive, extract_pdf
from dof_mcp.audit import audit
from dof_mcp.client import DofClient, html_to_text, parse_date, validate_id


class ClientTests(unittest.TestCase):
    def client(self, payload, status=200):
        client = DofClient(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(status, json=payload)
            )
        )
        self.addCleanup(client.close)
        return client

    def test_all_editions_and_duplicate_sections(self):
        client = self.client(
            {
                "messageCode": 200,
                "Matutina": [
                    {"codDiario": 123456, "paginaMax": "10"},
                    {"codDiario": 123456, "paginaMax": "30"},
                ],
                "Vespertina": [{"codDiario": 123457}],
                "Extraordinaria": [{"codDiario": 123458}],
            }
        )
        result, _ = client.editions("2024-01-02")
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["expected_pages"], 30)
        self.assertEqual({item["edition"] for item in result}, {"MAT", "VES", "EXT"})

    def test_official_not_found_is_supported(self):
        client = self.client({"messageCode": 404, "response": "NOT_FOUND"}, 404)
        self.assertEqual(client.editions("2024-01-01")[0], [])

    def test_broken_schema_is_not_an_empty_day(self):
        with self.assertRaises(ValueError):
            self.client({"messageCode": 200, "changed": []}).editions("2024-01-01")

    def test_input_validation_rejects_paths_and_non_iso_dates(self):
        for value in ["2024-1-2", "02-01-2024", "../../etc/passwd", "2024-02-30"]:
            with self.assertRaises(ValueError):
                parse_date(value)
        for value in [-1, 100000000, True]:
            with self.assertRaises(ValueError):
                validate_id(value)

    def test_text_preserves_accents_and_drops_executable_markup(self):
        text = html_to_text(
            "<head><title>REMOVE</title><style>REMOVE</style></head><p>Artículo 1.&nbsp;México.</p><script>REMOVE</script><p>Segundo<br>Renglón</p>"
        )
        self.assertNotIn("REMOVE", text)
        self.assertIn("Artículo 1. México.", text)
        self.assertIn("Segundo\nRenglón", text)

    def test_note_empty_body_is_explicit(self):
        client = self.client(
            {"messageCode": 200, "Nota": {"codNota": 1234567, "cadenaContenido": ""}}
        )
        self.assertFalse(client.note(1234567)["has_text"])

    def test_pdf_must_be_binary_pdf(self):
        with tempfile.TemporaryDirectory() as folder:
            client = self.client({"messageCode": 200})
            output = Path(folder) / "test.pdf"
            with self.assertRaises(ValueError):
                client.download_pdf(123456, output)
            self.assertFalse(output.exists())

    def test_retry_after_is_applied(self):
        responses = [
            httpx.Response(429, headers={"Retry-After": "5"}),
            httpx.Response(200, json={"messageCode": 200}),
        ]
        client = DofClient(
            transport=httpx.MockTransport(lambda request: responses.pop(0))
        )
        self.addCleanup(client.close)
        with (
            patch.object(client, "_throttle"),
            patch.object(client, "_cooldown") as cooldown,
        ):
            self.assertEqual(client.json("/test")["messageCode"], 200)
            cooldown.assert_called_once_with("5", 0)


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.archive = Archive(Path(folder.name))
        self.item = {
            "id": 123456,
            "date": "2024-01-02",
            "edition": "MAT",
            "expected_pages": 2,
        }

    def seed(self):
        self.archive.register_edition(self.item)
        client = Mock()
        client.download_pdf.side_effect = lambda identifier, path: (
            path.parent.mkdir(parents=True, exist_ok=True),
            path.write_bytes(b"%PDF-test"),
        )
        with patch(
            "dof_mcp.archive.extract_pdf",
            return_value=(
                ["Acuerdo de protección ambiental. " * 10, "Artículo 2. México."],
                [],
                [],
            ),
        ):
            self.assertEqual(self.archive.import_edition(client, 123456), "complete")
        return client

    def test_resume_does_not_duplicate_downloads_or_pages(self):
        client = self.seed()
        self.assertEqual(self.archive.import_edition(client, 123456), "unchanged")
        self.assertEqual(client.download_pdf.call_count, 1)
        with self.archive.connection() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM pages").fetchone()[0], 2)
        self.archive.export_manifest()
        self.assertTrue((self.archive.root / "manifest.json").exists())

    def test_audit_detects_modified_text_and_missing_dates(self):
        self.seed()
        with patch("dof_mcp.audit.Archive", return_value=self.archive):
            result = audit("2024-01-01", "2024-01-02")
            self.assertFalse(result["download_complete"])
            self.assertEqual(len(result["missing_dates"]), 2)
            self.assertEqual(result["verified_editions"], 1)
            text_file = self.archive.root / self.archive.edition(123456)["text_path"]
            text_file.write_text("modified", encoding="utf-8")
            result = audit("2024-01-01", "2024-01-02")
            self.assertEqual(len(result["integrity_errors"]), 1)

    def test_search_filters_dates_and_diacritics(self):
        self.seed()
        results = self.archive.search(
            "proteccion ambiental", "2024-01-01", "2024-12-31"
        )
        self.assertEqual(results[0]["edition_id"], 123456)
        self.assertEqual(results[0]["page"], 1)
        self.assertEqual(
            self.archive.search("ambiental", "2025-01-01", "2025-12-31"), []
        )
        self.assertEqual(self.archive.search("OR 1=1", "2024-01-01", "2024-12-31"), [])

    def test_reader_has_no_silent_truncation(self):
        self.seed()
        first = self.archive.read_pages(123456, max_chars=20)
        self.assertEqual(first["next_offset"], 20)
        second = self.archive.read_pages(123456, offset=20, max_chars=20)
        full = self.archive.read_pages(123456)
        self.assertEqual(first["text"] + second["text"], full["text"][:40])

    def test_failed_date_is_retried_not_skipped(self):
        client = Mock()
        client.editions.side_effect = ValueError("upstream broken")
        self.archive.discover_day(client, date(2024, 1, 2))
        self.assertEqual(self.archive.status()["days"], {"error": 1})
        client.editions.side_effect = None
        client.editions.return_value = ([self.item], {"messageCode": 200})
        self.archive.discover_day(client, date(2024, 1, 2))
        self.assertEqual(self.archive.status()["days"], {"editions_found": 1})
        self.assertEqual(client.editions.call_count, 2)

    def test_empty_date_uses_notes_and_annual_catalog(self):
        self.archive.register_edition(self.item)
        client = Mock()
        client.editions.return_value = ([], {"messageCode": 404})
        client.notes.return_value = ([], {"messageCode": 200})
        self.archive.discover_day(client, date(2024, 1, 2))
        client.notes.assert_called_once()
        self.assertEqual(self.archive.status()["days"], {"editions_found": 1})

    def test_pdf_page_loss_is_an_error(self):
        with patch(
            "dof_mcp.archive.subprocess.run",
            side_effect=[Mock(stdout="Pages: 2\n"), Mock(stdout=b"one\f")],
        ):
            with self.assertRaises(ValueError):
                extract_pdf(Path("source.pdf"))

    def test_empty_page_triggers_ocr_and_review(self):
        with patch(
            "dof_mcp.archive.subprocess.run",
            side_effect=[
                Mock(stdout="Pages: 1\n"),
                Mock(stdout=b"\f"),
                Mock(),
                Mock(stdout=b""),
            ],
        ):
            pages, ocr, low = extract_pdf(Path("source.pdf"))
        self.assertEqual(pages, [""])
        self.assertEqual(ocr, [1])
        self.assertEqual(low, [1])


if __name__ == "__main__":
    unittest.main()
