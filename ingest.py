import os
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
import weaviate
from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_TOKEN = os.getenv('OPENAI_API_TOKEN')
WEAVIATE_URL = os.getenv('WEAVIATE_URL')

# Here we load in the data from the text files.
txt_files = list(Path("docs/").glob("**/*.txt"))

docs = []
metadatas = []
for txt_file in txt_files:
    with open(txt_file) as f:
        docs.append(f.read())
        metadatas.append({"source": txt_file})

# Here we split the documents, as needed, into smaller chunks.
# We do this due to the context limits of the LLMs.
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000)

documents = text_splitter.create_documents(docs, metadatas=metadatas)

client = weaviate.Client(
    url=WEAVIATE_URL,
    additional_headers={"X-OpenAI-Api-Key": OPENAI_API_TOKEN},
)

client.schema.delete_all()
client.schema.get()
schema = {
    "classes": [
        {
            "class": "Paragraph",
            "description": "A written paragraph",
            "vectorizer": "text2vec-openai",
            "moduleConfig": {
                "text2vec-openai": {
                    "model": "ada",
                    "modelVersion": "001",
                    "type": "text",
                }
            },
            "properties": [
                {
                    "dataType": ["text"],
                    "description": "The content of the paragraph",
                    "moduleConfig": {
                        "text2vec-openai": {
                            "skip": False,
                            "vectorizePropertyName": False,
                        }
                    },
                    "name": "content",
                },
                {
                    "dataType": ["text"],
                    "description": "The link",
                    "moduleConfig": {
                        "text2vec-openai": {
                            "skip": True,
                            "vectorizePropertyName": False,
                        }
                    },
                    "name": "source",
                },
            ],
        },
    ]
}

client.schema.create(schema)

print("Ingesting data...")

# Batch ingestion with error handling callback.
def check_batch_result(results: dict):
    if results is not None:
        for result in results:
            if "result" in result and "errors" in result["result"]:
                if "error" in result["result"]["errors"]:
                    print(result["result"])

with client.batch as batch:
    for text in documents:
        batch.add_data_object(
            {"content": text.page_content, "source": str(text.metadata["source"])},
            "Paragraph",
        )

client.batch(
    batch_size=100,
    dynamic=True,
    creation_time=5,
    timeout_retries=3,
    connection_error_retries=3,
    callback=check_batch_result,
)
