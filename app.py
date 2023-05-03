import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
from langchain.chains import SequentialChain, LLMChain, ChatVectorDBChain, VectorDBQAWithSourcesChain
import faiss, pickle

load_dotenv()

SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_APP_TOKEN = os.getenv('SLACK_APP_TOKEN')
OPENAI_API_TOKEN = os.getenv('OPENAI_API_TOKEN')

# Load the LangChain.
index = faiss.read_index("stax_docs.index")

with open("stax_faiss_store.pkl", "rb") as f:
    store = pickle.load(f)

store.index = index

# Initializes your app with your bot token and socket mode handler
app = App(token=SLACK_BOT_TOKEN)

chatgpt_chain = VectorDBQAWithSourcesChain.from_chain_type(OpenAI(temperature=0.2, max_tokens=300), chain_type="stuff", vectorstore=store)

# Initializes your app with your bot token and socket mode handler
app = App(token=SLACK_BOT_TOKEN)

#Langchain implementation
template = """
    Using only the following context answer the question at the end. If you can't find the answer in the context below, just say that you don't know. Do not make up an answer.
    {chat_history}
    Human: {question}
    Assistant:"""

prompt = PromptTemplate(
    input_variables=["chat_history", "question"], 
    template=template
)


chatgpt_chain = ChatVectorDBChain.from_llm(
     llm=OpenAI(temperature=0,max_tokens=500),
     vectorstore=store
)


seq_chain = SequentialChain(chains=[chatgpt_chain], input_variables=["chat_history", "question"])

#Message handler for Slack
@app.message(".*")
def message_handler(message, say, logger):
    print(message)

    output = seq_chain.run(chat_history = "", question = message['text'], verbose=True)
    say(output)


# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
