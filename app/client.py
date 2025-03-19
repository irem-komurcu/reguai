import os
import vertexai
from google import genai
from google import auth

LOCATION = "us-central1"

VERTEXAI = os.getenv("VERTEXAI", "true").lower() == "true"

# Initialize Google Cloud clients
credentials, project_id = auth.default()
vertexai.init(project=project_id, location=LOCATION)
if VERTEXAI:
    genai_client = genai.Client(project=project_id, location=LOCATION, vertexai=True)
else:
    # API key should be set using GOOGLE_API_KEY environment variable
    genai_client = genai.Client(http_options={"api_version": "v1alpha"})