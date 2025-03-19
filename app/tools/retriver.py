import os
from app.client import project_id
from app.templates import FORMAT_DOCS
from app.secrets import get_db_secrets
from google.genai.types import FunctionDeclaration, Tool
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_google_cloud_sql_pg import PostgresVectorStore, PostgresEngine


LOCATION = "us-central1"
EMBEDDING_MODEL = "text-multilingual-embedding-002" #"text-embedding-004"
TABLE_NAME = os.getenv("TABLE_NAME", "documents")

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