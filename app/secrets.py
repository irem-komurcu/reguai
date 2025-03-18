import os
import json
import google
from google.cloud.secretmanager import SecretManagerServiceClient

credentials, PROJECT_ID = google.auth.default()
SECRET_ID = os.getenv("SECRET_ID", "agent-knowledgebase")
SECRET_VERSION = os.getenv("SECRET_VERSION", "latest")

def get_db_secrets():
    client = SecretManagerServiceClient()
    response = client.access_secret_version(request={"name": f"projects/{PROJECT_ID}/secrets/{SECRET_ID}/versions/{SECRET_VERSION}"})
    secrets = json.loads(response.payload.data.decode("UTF-8"))
    return secrets

