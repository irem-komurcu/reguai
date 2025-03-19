import functions_framework

import io
import os
import json
from pdf_loader import load_pdf
from google.cloud import storage
from get_metadata import get_metadata
from documentai_loader import load_pdf as documentai_load_pdf
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.docstore.document import Document
from google.cloud.secretmanager import SecretManagerServiceClient
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_cloud_sql_pg import PostgresEngine, PostgresVectorStore, Column


PROJECT_ID = get_metadata("project_id")

BUCKET = os.getenv("BUCKET")
DOCUMENTS_FOLDER = os.getenv("DOCUMENTS_FOLDER")
SECRET_ID = os.getenv("SECRET_ID")
SECRET_VERSION = os.getenv("SECRET_VERSION", "latest")
TABLE_NAME = os.getenv("TABLE_NAME", "documents")
MODEL_NAME = os.getenv("MODEL_NAME", "text-multilingual-embedding-002")#"text-embedding-004")

@functions_framework.cloud_event
def vectorization(cloud_event):
    data = cloud_event.data
    file_name = data['name']
    metageneration = data["metageneration"]
    timeCreated = data["timeCreated"]
    updated = data["updated"]
    

    if DOCUMENTS_FOLDER in file_name:
        
        file_name = file_name.replace(DOCUMENTS_FOLDER, "")
        print(f"upload request recieved for {file_name}")

        print("accessing bucket")
        bucket_accessor = BucketAccessor(BUCKET)

        if not bucket_accessor.file_exists(prefix=DOCUMENTS_FOLDER, item=file_name):
            print(f"File {file_name} does not exist in bucket {BUCKET}")
            return "file not found"
        bytes, buffer = bucket_accessor.read(prefix=DOCUMENTS_FOLDER, item=file_name)
        print("read file")
        try:
            pages = documentai_load_pdf(bytes)
        except:
            pages = load_pdf(buffer)
        texts, metadatas = split(file_name, pages)

        print("reading secrets...")
        client = SecretManagerServiceClient()
        response = client.access_secret_version(request={"name": f"projects/{PROJECT_ID}/secrets/{SECRET_ID}/versions/{SECRET_VERSION}"})
        secrets = json.loads(response.payload.data.decode("UTF-8"))
        
        region = secrets["REGION"]
        instance_name = secrets["INSTANCE_NAME"]
        database_name = secrets["DB_NAME"]
        database_user = secrets["DB_USER"]
        database_password = secrets["DB_PASS"]
        print("secrets read")

        embedding_service = VertexAIEmbeddings(model_name=MODEL_NAME)

        engine = PostgresEngine.from_instance(
            project_id=PROJECT_ID,
            region=region,
            instance=instance_name,
            database=database_name,
            user=database_user,
            password=database_password
        )

        try:
            engine.init_vectorstore_table(
                table_name=TABLE_NAME,
                vector_size=768,
                overwrite_existing=False,
                metadata_columns=[
                    Column("file_name", "VARCHAR", nullable=True),
                    Column("page", "INTEGER", nullable=True),
                ]
            )
        except Exception as e:
            print("table probably exist")

        vector_store = PostgresVectorStore.create_sync(
            engine,
            table_name=TABLE_NAME,
            embedding_service=embedding_service,
            metadata_columns=["file_name", "page"],
        )

        

        vector_store.add_texts(texts, metadatas=metadatas)

        
    
    return "done"



class BucketAccessor:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.storage_client = storage.Client()
    
    def read(self, prefix, item, delimiter='/'):
        
        bucket = self.storage_client.bucket(self.bucket_name)
        blob = bucket.blob(prefix + item)

        bytes = blob.download_as_bytes()
        buffer = io.BytesIO(bytes)
        return bytes, buffer

    def file_exists(self, prefix, item):
        bucket = self.storage_client.bucket(self.bucket_name)
        blob = bucket.blob(prefix + item)
        return blob.exists()
    
def split(file_name, pages, separators=["\n\n", "\n \n", "\n", ".", " "]):
        text_splitter = RecursiveCharacterTextSplitter(
            separators=separators,
            chunk_size=500,
            chunk_overlap=0,
            length_function=len,
        )
        docs = [Document(page_content=text, metadata={"file_name": file_name, "page": c}) for c, text in pages.items()]
        splits = text_splitter.split_documents(docs)
        
        texts = []
        metadatas = []
        for s in splits:
            texts.append(s.page_content.strip())
            metadatas.append(s.metadata)

        return texts, metadatas
