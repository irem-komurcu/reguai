from langchain_google_cloud_sql_pg import PostgresVectorStore, PostgresEngine
from langchain_google_vertexai import VertexAIEmbeddings
from app.templates import FORMAT_DOCS
import google
import vertexai
from google import genai
from google.genai.types import (
    FunctionDeclaration,
    Tool,
)
from app.secrets import get_db_secrets
import os


LOCATION = "us-central1"
EMBEDDING_MODEL = "text-multilingual-embedding-002"#"text-embedding-004"
TABLE_NAME = os.getenv("TABLE_NAME", "documents")
VERTEXAI = os.getenv("VERTEXAI", "true").lower() == "true"

# Initialize Google Cloud clients
credentials, project_id = google.auth.default()
vertexai.init(project=project_id, location=LOCATION)
if VERTEXAI:
    genai_client = genai.Client(project=project_id, location=LOCATION, vertexai=True)
else:
    # API key should be set using GOOGLE_API_KEY environment variable
    genai_client = genai.Client(http_options={"api_version": "v1alpha"})

secrets = get_db_secrets()
engine = PostgresEngine.from_instance(
    project_id=project_id,
    region=secrets["REGION"],
    instance=secrets["INSTANCE_NAME"],
    database=secrets["DB_NAME"],
    user=secrets["DB_USER"],
    password=secrets["DB_PASS"]
)

embedding_service = VertexAIEmbeddings(model_name=EMBEDDING_MODEL)

vector_store = PostgresVectorStore.create_sync(
    engine,
    table_name=TABLE_NAME,
    embedding_service=embedding_service,
    metadata_columns=["file_name", "page"],
)

retriever = vector_store.as_retriever()

def retrieve_docs(query: str) -> dict[str, str]:
    """
    Retrieves pre-formatted documents about about newly published regulations
    published by governments.

    Args:
        query: Search query string related to regulations, laws, or restrictions.

    Returns:
        A set of relevant, pre-formatted documents.
    """
    docs = retriever.invoke(query)
    formatted_docs = FORMAT_DOCS.format(docs=docs)
    return {"output": formatted_docs}

retrieve_docs_tool = Tool(
    function_declarations=[
        FunctionDeclaration.from_callable(client=genai_client, callable=retrieve_docs)
    ]
)