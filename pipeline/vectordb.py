import logging
import os
import sys

from dotenv import load_dotenv

from pinecone import Pinecone, ServerlessSpec

from openai import OpenAI

import uuid

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

load_dotenv()

pinecone_api_key = os.getenv("PINECONE_API_KEY")

pc = Pinecone(api_key=pinecone_api_key)

def check_index_exists(index_name: str,) -> bool:
    active_indexes = [i["name"] for i in pc.list_indexes()]
    return index_name in active_indexes

def create_index(index_name: str) -> None:
    pc.create_index(
        name=index_name,
        dimension=1536, # Replace with your model dimensions
        metric="euclidean", # Replace with your model metric
        spec=ServerlessSpec(
            cloud="aws",
            region="us-west-2"
        ) 
    )

def delete_content(index_name: str) -> None:
    pinecone_index = pc.Index(index_name)
    pinecone_index.delete(deleteAll=True,)

def pinecone_stats(index_name: str) -> dict:
    pinecone_index = pc.Index(index_name)
    return pinecone_index.describe_index_stats()

def get_openai_embedding(text: str, model_name="text-embedding-ada-002") -> list:
    client = OpenAI() 
    response = client.embeddings.create(
        input=text,
        model=model_name
    )            
    embedding = response.data[0].embedding
    return embedding    

def upload_pinecone(index_name: str, embedding: list, metadata: dict, namespace: str) -> None:
    pinecone_index = pc.Index(index_name)
    data = {'id': str(uuid.uuid1()), 'values': embedding, 'metadata': metadata}
    pinecone_index.upsert(vectors = [data], namespace=namespace)