import functions_framework

import os
import json
from get_metadata import get_metadata
import asyncio
import asyncpg
from google.cloud.sql.connector import Connector
from google.cloud.secretmanager import SecretManagerServiceClient

connector = Connector()

PROJECT_ID = get_metadata("project_id")

DOCUMENTS_FOLDER = os.getenv("DOCUMENTS_FOLDER")
SECRET_ID = os.getenv("SECRET_ID")
SECRET_VERSION = os.getenv("SECRET_VERSION", "latest")
TABLE_NAME = os.getenv("TABLE_NAME", "documents")

async def asyncpg_connection(project_id, database_password, region, instance_name, database_name, database_user):
    loop = asyncio.get_running_loop()
    async with Connector(loop=loop) as connector:
        conn = await connector.connect_async(
            f"{project_id}:{region}:{instance_name}",
            "asyncpg",
            user=database_user,
            password=database_password,
            db=database_name
        )
        return conn

class Database():
    def __init__(self, project_id, region, instance_name, database_name, database_user, database_password):
        self.project_id=project_id
        self.region=region
        self.instance_name=instance_name
        self.database_name=database_name
        self.database_user=database_user
        self.database_password=database_password
    
    async def _execute(self, query, *params, fetch=False):
        try:
            conn = await asyncpg_connection(
                self.project_id, self.database_password, self.region,
                self.instance_name, self.database_name, self.database_user
            )
            if fetch:
                result = await conn.fetch(query, *params)
            else:
                result = await conn.execute(query, *params)
            return result
        except Exception as e:
            print(f"An error occurred: {e}")
    
    async def remove_file(self, file_name):
        await self._execute(
            f"DELETE FROM {TABLE_NAME} WHERE file_name = $1",
            file_name
        )
    def remove(self, file_name):
        asyncio.run(self.remove_file(file_name))


@functions_framework.cloud_event
def vectorization(cloud_event):
    data = cloud_event.data
    file_name = data['name']

    if DOCUMENTS_FOLDER in file_name:
        file_name = file_name.replace(DOCUMENTS_FOLDER, "")
        print(f"delete request recieved for {file_name}")

        print("reading secrets...")
        client = SecretManagerServiceClient()
        response = client.access_secret_version(request={"name": f"projects/{PROJECT_ID}/secrets/{SECRET_ID}/versions/{SECRET_VERSION}"})
        secrets = json.loads(response.payload.data.decode("UTF-8"))
        
        print(secrets)

        region = secrets["REGION"]
        instance_name = secrets["INSTANCE_NAME"]
        database_name = secrets["DB_NAME"]
        database_user = secrets["DB_USER"]
        database_password = secrets["DB_PASS"]
        print("secrets read")

        print("connecting to db")
        db = Database(project_id=PROJECT_ID, region=region, instance_name=instance_name, database_name=database_name, database_user=database_user, database_password=database_password)
        db.remove(file_name=file_name)
        print(f"{file_name} removed from database")      
    
    return "done"


