"""Exercise the running local stack; never prints administrator credentials."""

import argparse
import os
import secrets
import time

import httpx


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser-user", action="store_true")
    parser.add_argument("--remove-browser-user")
    parser.add_argument("--query", action="store_true")
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--request-browser-code")
    options = parser.parse_args()
    with httpx.Client(
        base_url="http://frontend:8080", timeout=600, trust_env=False
    ) as client:
        assert client.get("/health").json() == {"status": "ok"}
        response = client.post(
            "/api/login",
            json={
                "correo": os.environ["ADMIN_EMAIL"],
                "contraseña": os.environ["ADMIN_PASSWORD"],
            },
        )
        response.raise_for_status()
        client.headers["Authorization"] = f"Bearer {response.json()['token']}"
        if options.browser_user:
            email = f"browser-check-{secrets.token_hex(4)}@example.test"
            password = secrets.token_urlsafe(24)
            response = client.post(
                "/api/registro",
                json={
                    "correo": email,
                    "contraseña": password,
                    "nombre": "Verificación local",
                },
            )
            response.raise_for_status()
            print(f"BROWSER_EMAIL={email}")
            print(f"BROWSER_PASSWORD={password}")
        elif options.request_browser_code:
            assert options.request_browser_code.startswith("browser-check-")
            response = client.post(
                "/api/solicitar_codigo",
                json={
                    "correo": options.request_browser_code,
                },
            )
            response.raise_for_status()
            print("Recovery email sent to the local test mailbox.")
        elif options.remove_browser_user:
            assert options.remove_browser_user.startswith(
                "browser-check-"
            ) and options.remove_browser_user.endswith("@example.test")
            response = client.delete(
                "/api/delete_user", params={"correo": options.remove_browser_user}
            )
            response.raise_for_status()
            print("Temporary browser account removed.")
        else:
            status = client.get("/api/status").json()
            print("Status:", status)
            assert status["ready"], status
            documents = client.get("/api/documents").json()
            assert documents
            print(
                "Documents:",
                [{"name": doc["name"], "pages": doc["pages"]} for doc in documents],
            )
            response = client.get(f"/api/documents/{documents[0]['id']}/file")
            response.raise_for_status()
            assert response.content.startswith(b"%PDF")
            assert client.get("/consult-view").status_code == 200
            if options.query:
                start = time.monotonic()
                response = client.post(
                    "/modelo/query/invoke",
                    json={
                        "input": {
                            "question": "¿Cuál es el tipo de cambio para solventar "
                            "obligaciones en moneda extranjera "
                            "publicado en este diario?",
                            "chat_history": "",
                        }
                    },
                )
                response.raise_for_status()
                output = response.json()
                assert output["sources"] and len(output["output"]) > 100, output
                print(f"Query completed in {time.monotonic() - start:.1f}s")
                print(output["output"])
            if options.summary:
                response = client.post(f"/api/documents/{documents[0]['id']}/summary")
                response.raise_for_status()
                print("Generated overview:", response.json()["output"])
        client.post("/api/logout").raise_for_status()


if __name__ == "__main__":
    main()
