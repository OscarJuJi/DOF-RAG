"""Local account security and API contract regression tests, without external calls."""

import os
import tempfile
import unittest
from unittest.mock import patch

from capidofchat_api.local_server import app
from capidofchat_api.storage import database
from fastapi.testclient import TestClient


class LocalApiTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.environment = patch.dict(
            os.environ,
            {
                "DATA_DIR": self.directory.name,
                "ADMIN_EMAIL": "admin@example.test",
                "ADMIN_PASSWORD": "Test-only-password!234",
            },
        )
        self.environment.start()
        self.client = TestClient(app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.environment.stop()
        self.directory.cleanup()

    def login(self, email="admin@example.test", password="Test-only-password!234"):
        response = self.client.post(
            "/api/login",
            json={"correo": email, "contraseña": password, "keepsesion": "false"},
        )
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()["token"]

    def create_employee(self):
        response = self.client.post(
            "/api/registro",
            json={
                "correo": "employee@example.test",
                "contraseña": "Employee!234",
                "nombre": "Test",
                "appat": "User",
                "notif": "1",
            },
        )
        self.assertEqual(response.status_code, 201, response.text)

    def test_endpoints_require_authentication(self):
        self.assertEqual(self.client.get("/health").status_code, 200)
        for path in [
            "/query/invoke",
            "/specific/invoke",
            "/summary/invoke",
            "/notification/invoke",
            "/api/usuarios",
        ]:
            self.assertEqual(
                self.client.post(
                    path, json={"input": {"question": "test"}}
                ).status_code,
                401,
            )
        self.assertEqual(self.client.get("/api/documents").status_code, 401)

    def test_login_uses_hashes_and_logout_revokes_session(self):
        token = self.login()
        with database() as connection:
            password_hash = connection.execute(
                "SELECT password_hash FROM users"
            ).fetchone()[0]
            token_hash = connection.execute(
                "SELECT token_hash FROM sessions"
            ).fetchone()[0]
        self.assertNotIn("Test-only", password_hash)
        self.assertNotEqual(token, token_hash)
        self.assertTrue(
            self.client.post("/api/validar_token", json={"token": token}).json()[
                "valid"
            ]
        )
        self.client.post("/api/logout")
        self.assertFalse(
            self.client.post("/api/validar_token", json={"token": token}).json()[
                "valid"
            ]
        )
        self.assertEqual(self.client.get("/api/documents").status_code, 401)

    def test_employee_cannot_escalate_or_modify_other_users(self):
        self.login()
        self.create_employee()
        self.client.post("/api/logout")
        self.login("employee@example.test", "Employee!234")
        self.assertEqual(self.client.post("/api/usuarios").status_code, 403)
        self.assertEqual(
            self.client.post(
                "/api/actualizar_user",
                json={"correo": "admin@example.test", "nombre": "Changed"},
            ).status_code,
            403,
        )
        response = self.client.post(
            "/api/actualizar_user",
            json={
                "correo": "employee@example.test",
                "nombre": "Updated",
                "rol": "admin",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.post("/api/usuarios").status_code, 403)
        self.assertEqual(
            self.client.delete(
                "/api/delete_user", params={"correo": "admin@example.test"}
            ).status_code,
            403,
        )

    @patch("capidofchat_api.accounts.smtplib.SMTP")
    def test_password_reset_requires_single_use_token_and_revokes_sessions(self, smtp):
        token = self.login()
        response = self.client.post(
            "/api/solicitar_codigo", json={"correo": "admin@example.test"}
        )
        self.assertEqual(response.status_code, 200)
        message = smtp.return_value.__enter__.return_value.send_message.call_args.args[
            0
        ]
        import re

        code = re.search(r"\b\d{6}\b", message.get_content()).group()
        self.assertNotIn(code, response.text)
        self.assertEqual(
            self.client.post(
                "/api/actualizar_password",
                json={"correo": "admin@example.test", "contraseña": "Changed!234"},
            ).status_code,
            422,
        )
        response = self.client.post(
            "/api/validar_codigo", json={"correo": "admin@example.test", "codigo": code}
        )
        self.assertEqual(response.status_code, 200, response.text)
        reset_token = response.json()["reset_token"]
        self.assertEqual(
            self.client.post(
                "/api/validar_codigo",
                json={"correo": "admin@example.test", "codigo": code},
            ).status_code,
            400,
        )
        payload = {
            "correo": "admin@example.test",
            "contraseña": "Changed!234",
            "reset_token": reset_token,
        }
        self.assertEqual(
            self.client.post("/api/actualizar_password", json=payload).status_code, 200
        )
        self.assertEqual(
            self.client.post("/api/actualizar_password", json=payload).status_code, 400
        )
        self.assertFalse(
            self.client.post("/api/validar_token", json={"token": token}).json()[
                "valid"
            ]
        )
        self.login(password="Changed!234")

    @patch("capidofchat_api.accounts.secrets.randbelow", return_value=123456)
    @patch("capidofchat_api.accounts.smtplib.SMTP")
    def test_reset_code_attempt_limit_persists(self, smtp, random_code):
        self.client.post("/api/solicitar_codigo", json={"correo": "admin@example.test"})
        for _ in range(6):
            self.client.post(
                "/api/validar_codigo",
                json={"correo": "admin@example.test", "codigo": "000000"},
            )
        with database() as connection:
            attempts = connection.execute("SELECT attempts FROM resets").fetchone()[0]
        self.assertEqual(attempts, 5)

    @patch("capidofchat_api.local_rag.answer_query")
    def test_query_contract_and_validation(self, answer):
        self.login()
        answer.return_value = {"output": "Respuesta de prueba", "sources": []}
        response = self.client.post(
            "/query/invoke", json={"input": {"question": "Prueba", "chat_history": ""}}
        )
        self.assertEqual(response.json()["output"], "Respuesta de prueba")
        self.assertEqual(
            self.client.post(
                "/query/invoke", json={"input": {"document": "wrong schema"}}
            ).status_code,
            422,
        )


if __name__ == "__main__":
    unittest.main()
