import os
import logging
from dotenv import load_dotenv

import hvac
import sys

load_dotenv()

VAULT_TOKEN = os.getenv("VAULT_TOKEN")


def load_vault_env(
    vault_url="http://127.0.0.1:8200",
    token=VAULT_TOKEN,
    secret_paths=None,
):
    """Fetches secrets from multiple Vault paths and injects them into os.environ."""
    if secret_paths is None:
        secret_paths = [
            "openai_api_key",
            "langsmith_api_key",
            "tavily_api_key",
            "qdrant_api_key",
        ]

    client = hvac.Client(url=vault_url, token=token)

    if not client.is_authenticated():
        sys.exit("Vault authentication failed.")

    for path in secret_paths:
        try:
            read_response = client.secrets.kv.v2.read_secret_version(
                path=path,
                raise_on_deleted_version=True,
            )
            secrets = read_response["data"]["data"]

            for key, value in secrets.items():
                os.environ[key] = str(value)

        except Exception as e:
            logging.info("❌ Error reading %s: %s", path, e)
