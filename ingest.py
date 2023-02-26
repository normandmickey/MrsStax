"""This is the logic for ingesting PDF and DOCX files into LangChain."""
import os
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pdfminer.high_level import extract_text
import weaviate
from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_TOKEN = os.getenv('OPENAI_API_TOKEN')
WEAVIATE_URL = os.getenv('WEAVIATE_URL')


# Here we extract the text from your pdf files.
files = list(Path("docs/").glob("**/*.pdf"))
count = 0
for file in files:
    count += 1
    filename = "docs/" + "pdf" + str(count) + ".txt"
    text = extract_text(file)
    with open(filename, 'w') as f:
         f.write(text)

# Here we extract the text from your docx files. 
files = list(Path("docs/").glob("**/*.docx"))
count = 0
for file in files:
    count += 1
    filename = "docs/" + "docx" + str(count) + ".txt"
    text = docx2txt.process(file)
    with open(filename, 'w') as f:
        f.write(text)

def check_batch_result(results: dict):
  """
  Check batch results for errors.
  Parameters
  ----------
  results : dict
      The Weaviate batch creation return value.
  """

  if results is not None:
    for result in results:
      if "result" in result and "errors" in result["result"]:
        if "error" in result["result"]["errors"]:
          print(result["result"])

# Here we load in the data from the text files created above. 
ps = list(Path("docs/").glob("**/*.txt"))

docs = []
metadatas = []
for p in ps:
    with open(p) as f:
        docs.append(f.read())
        metadatas.append({"source": p})

# Here we split the documents, as needed, into smaller chunks.
# We do this due to the context limits of the LLMs.
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,)

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

client.batch(
  batch_size=100,
  dynamic=True,
  creation_time=5,
  timeout_retries=3,
  connection_error_retries=3,
  callback=check_batch_result,
)

with client.batch as batch:
    for text in documents:
        batch.add_data_object(
            {"content": text.page_content, "source": str(text.metadata["source"])},
            "Paragraph",
        )
