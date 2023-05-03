"""This is the logic for ingesting PDF and DOCX files into LangChain."""
import os
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pdfminer.high_level import extract_text
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from dotenv import load_dotenv
import faiss, pickle, docx2txt

load_dotenv()

OPENAI_API_TOKEN = os.getenv('OPENAI_API_TOKEN')


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

# Here we load in the data from the text files created above. 
ps = list(Path("docs/").glob("**/*.txt"))

data = []
sources = []
for p in ps:
    with open(p) as f:
        data.append(f.read())
    sources.append(p)

# Here we split the documents, as needed, into smaller chunks.
# We do this due to the context limits of the LLMs.
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=500, length_function=len)

docs = []
metadatas = []

for i, d in enumerate(data):
    splits = text_splitter.split_text(d)
    docs.extend(splits)
    metadatas.extend([{"source": sources[i]}] * len(splits))


# Here we create a vector store from the documents and save it to disk.
store = FAISS.from_texts(docs, OpenAIEmbeddings(), metadatas=metadatas)
faiss.write_index(store.index, "stax_docs.index")
store.index = None
with open("stax_faiss_store.pkl", "wb") as f:
    pickle.dump(store, f)
