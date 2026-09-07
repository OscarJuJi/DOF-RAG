import argparse

import requests


def invoke_chat(api_url: str, question: str, chat_history: str) -> dict:
    response = requests.post(
        f"{api_url.rstrip('/')}/query/invoke",
        json={"input": {"question": question, "chat_history": chat_history}},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Invoke the local CapiDOFChat API.")
    parser.add_argument("question", help="Question to send to the chatbot.")
    parser.add_argument("--history", default="", help="Optional chat history.")
    parser.add_argument("--api-url", default="http://localhost:8000")
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_arguments()
    print(invoke_chat(arguments.api_url, arguments.question, arguments.history))
