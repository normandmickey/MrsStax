import os
import weaviate
import json
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_TOKEN = os.getenv('OPENAI_API_TOKEN')
WEAVIATE_URL = os.getenv('WEAVIATE_URL')

client = weaviate.Client(
    url=WEAVIATE_URL,
    additional_headers={
        'X-OpenAI-Api-Key': OPENAI_API_TOKEN
    }
)

nearText = {"concepts": input("Enter Keyword: ")}

result = (
    client.query
    .get("Paragraph", [ "content", "source"])
    .with_near_text(nearText)
    .with_limit(2)
    .do()
)

print(json.dumps(result, indent=4))
