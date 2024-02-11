import logging
import os
import sys

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
import utils

from openai import OpenAI

from zenpy import Zenpy
import uuid

import tiktoken

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

load_dotenv()

pinecone_api_key = os.getenv("PINECONE_API_KEY")

pc = Pinecone(api_key=pinecone_api_key)
active_indexes = [i["name"] for i in pc.list_indexes()]
index_name = "gartner"

if index_name not in active_indexes:
    print(f"Creating index {index_name}")
    pc.create_index(
        name=index_name,
        dimension=1536, # Replace with your model dimensions
        metric="euclidean", # Replace with your model metric
        spec=ServerlessSpec(
            cloud="aws",
            region="us-west-2"
        ) 
    )

pinecone_index = pc.Index(index_name)

print(f"Index statistics pre-deletion: {pinecone_index.describe_index_stats()}\n")
pinecone_index.delete(deleteAll=True,)
print(f"Index statistics post-deletion: {pinecone_index.describe_index_stats()}\n")

# Create a Zenpy instance
credentials = {
    # "domain":"support.pointsbet",
    "email": "",
    "password": "",
    "subdomain": "rippe",
}


client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)


zenpy_client = Zenpy(**credentials)
articles = [i for i in zenpy_client.help_center.articles()]


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

article_data = []
# # Create LlamaIndex Documents
for article in articles:
    article = article.to_dict()

    if article['body'] and article['title']:
        if len(article['body']) <= 15_000:
            print(f"Title: {article['title']} | Length {len(article['body'])}: | Tokens: {num_tokens_from_string(article['body'], 'cl100k_base')}")

            body = utils.strip_html(article["body"])

            response = client.embeddings.create(
                input=body,
                model="text-embedding-ada-002"
            )            

            embedding = response.data[0].embedding

            data = {'id': str(uuid.uuid1()), 'values': embedding, 'metadata': {'source': 'zendesk', 'title': article["title"], 'text': body}}

            pinecone_index.upsert([data])