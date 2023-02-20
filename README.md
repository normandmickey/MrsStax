# MrsStax

## Introduction
This application is a Slack Bot that uses OpenAI's language model to provide domain specific answers.  You provide the documents. 

## Features
- GPT3 based Slack Bot using your own documents (PDF or docx). 
- Uses remote vector database  Weaviate (https://weaviate.io)

## Usage
To use the Assistant Slack Bot, the following environment variables need to be set:
- SLACK_BOT_TOKEN: Token for the Slack Bot.
- SLACK_APP_TOKEN: Token for the Slack app.
- OPENAI_API_TOKEN: Token for OpenAi
- WEAVIATE_URL: URL for Weaviate instance. 

## Installation
Requires Python3
Run the follwoing commands 

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp env.example .env
nano .env (to update API tokens for Slack, OpenAI and Weaviate URL)
