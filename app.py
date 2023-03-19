import os
from dotenv import load_dotenv
import weaviate
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
from langchain.chains import SequentialChain, LLMChain, ChatVectorDBChain
from langchain.vectorstores import Weaviate
from langchain.llms.openai import BaseOpenAI, OpenAIChat
from langchain.chains import ChatVectorDBChain
from langchain.chains.llm import LLMChain
from langchain.chains.chat_vector_db.prompts import CONDENSE_QUESTION_PROMPT
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks.base import CallbackManager, AsyncCallbackManager, BaseCallbackHandler, BaseCallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains.chat_vector_db.prompts import CONDENSE_QUESTION_PROMPT, QA_PROMPT

def _create_callback_manager(is_async: bool) -> BaseCallbackManager:
    if is_async:
        return AsyncCallbackManager
    else:
        return CallbackManager


is_async: bool = False
stream_handler: BaseCallbackHandler = StreamingStdOutCallbackHandler()

PREFIX_MESSAGE = [{
    'role': 'system',
    'content': '''
        あなたは関西人のおっちゃんです。
        一人称は「おざりん」で、全ての回答に関西弁で口語で解答してください。
    '''
}]

load_dotenv()

SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_APP_TOKEN = os.getenv('SLACK_APP_TOKEN')
OPENAI_API_TOKEN = os.getenv('OPENAI_API_TOKEN')
WEAVIATE_URL = os.getenv('WEAVIATE_URL')

client = weaviate.Client(
    url=WEAVIATE_URL,
    additional_headers={
        'X-OpenAI-Api-Key': OPENAI_API_TOKEN
    }
)

vectorstore = Weaviate(client, "Paragraph", "content")

# Initializes your app with your bot token and socket mode handler
app = App(token=SLACK_BOT_TOKEN)

_callback_manager = _create_callback_manager(is_async)
stream_manager = _callback_manager([stream_handler])

stream_llm = OpenAIChat(
            temperature=0.8, max_tokens=1024, streaming=True,
            callback_manager=stream_manager, verbose=True,
            prefix_messages=PREFIX_MESSAGE
)
doc_chain = load_qa_chain(stream_llm, chain_type="stuff", prompt=QA_PROMPT)

question_llm = OpenAIChat(temperature=0.4, max_tokens=256, verbose=True)
question_generator = LLMChain(llm=question_llm, prompt=CONDENSE_QUESTION_PROMPT)
chain = ChatVectorDBChain(
    vectorstore=vectorstore,
    combine_docs_chain=doc_chain,
    question_generator=question_generator,
    top_k_docs_for_context=2,
)



# chatgpt_chain = ChatVectorDBChain.from_llm(
#      llm=OpenAI(temperature=0,max_tokens=2000),
#      vectorstore=vectorstore
# )


seq_chain = SequentialChain(chains=[chain], input_variables=["chat_history", "question"])

#Message handler for Slack
@app.message(".*")
def message_handler(message, say, logger):
    print(message)

    output = seq_chain.run(chat_history = "", question = message['text'], verbose=True)
    say(output)

@app.event("app_mention")
def handle_app_mention_events(body, say, logger):
    logger.info(body)
    message = body["event"]
    print(message)
    output = seq_chain.run(chat_history = "", question = message['text'], verbose=True)
    say(output)

# Start your app
if __name__ == "__main__":
    print(app)
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
