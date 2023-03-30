# QA Slack Bot - MrsStax

## Introduction
This application is a Slack Bot that uses Langchain and OpenAI's GPT3 language model to provide domain specific answers. You provide the documents. 

This app includes the [OpenStax](https://openstax.org) textbook "Principles of Macroeconomics 3e" for demonstration purposes.

Principles of Macroeconomics 3e is licensed under a Creative Commons Attribution 4.0 International (CC BY) license, which means that you can distribute, remix, and build upon the content, as long as you provide attribution to OpenStax and its content contributors.  

## Features
- GPT3 based Slack Bot using your own documents (PDF or docx) for added context and increased accuracy. 
- Utilizes a remote vector database from Weaviate (https://weaviate.io) for faster speed and scaling. 

## Usage
To use the MrsStax Slack Bot, the following environment variables need to be set in your .env file:
- SLACK_BOT_TOKEN: Token for the Slack Bot.
- SLACK_APP_TOKEN: Token for the Slack app.
- OPENAI_API_TOKEN: Token for OpenAi
- WEAVIATE_URL: URL for Weaviate instance. 

## Installation
Requires Python3.10 or higher

Clone this repo and run the following commands 

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp env.example .env
```

1. Set your OPENAI_API_TOKEN in the .env file.

2. Register with [Weaviate](https://auth.wcs.api.weaviate.io/auth/realms/SeMI/protocol/openid-connect/registrations?client_id=wcs&response_type=code&redirect_uri=https://console.weaviate.io/registration-login). 
   - Click on "Create a Weaviate Cluster". 
     - Name - Give your cluster a name or leave blank to be assigned a random one. 
     - Subscription Tier - "Sandbox Free". 
     - Weaviate Version - Leave as default. 
     - Enable OIDC Authentication - Set to "disabled" as long as your documents are not confidential.  If you enable OIDC Auth additional configuration is required in your Python app.   
     - Click on "Create".
     - Set your "WEAVIATE_URL" in your .env file.  You can find your URL by clicking on the connection icon at the top of the page. It will be https://Your-Cluster-Id.weaviate.network.

3. Create new Slack App - https://api.slack.com

4. Click on "Basic Information"
   - Click on "Generate Token and Scopes"
     - Token Name = "App Token"
     - App Scope = "connections:write"

   - Copy "App Token" and paste it into your .env file as "SLACK_APP_TOKEN". 

5. Click on "Socket Mode"
   - Click on "Enable"

6. Click on "OAuth & Permissions" and add the following permissions. 
   - app_mentions:read
   - chat:write
   - chat:write.public
   - im:history

   - Copy "Bot User OAuth Token" and paste it into your .env file as "SLACK_BOT_TOKEN". 
   

7. Click on "App Home" and make sure "Messages Tab" is enabled and check the box for "Allow users to send Slash commands and messages from the messages tab". 

8. Click on "Event Subscriptions" then "Enable Events" and add the following events under "Subscribe to Bot Events". 
   - app_mention
   - message.im

9. Install App into your Slack. 

10. Upload or copy your .pdf or .docx files to the "docs" folder. 

11. Run the following commands.
 
   ```
   python ingest.py
   python app.py
   ```

12. Visit your Slack and send direct message to your bot. 

If you left the two original files (Macroeconomics3e-WEB.pdf, pdf1.txt) in your docs directory you should be able to ask your bot economics related questions. 
For example. 

  - Q1. Residents of the town of Smithfield like to consume hams, but each ham requires 10 people to produce it and takes a month. If the town has a total of 100 people, what is the maximum amount of ham the residents can consume in a month?

  - Q2. Why might Belgium, France, Italy, and Sweden have a higher export to GDP ratio than the United States? 

  - Q3. What is dumping? Why does prohibiting it often work better in theory than in practice?

13. Your vector database needs to be re-indexed each time you add or remove documents from your docs folder. To do this simply run 
```python ingest.py```. 

14. You can test your Weaviate database with the following command 
    ```python neartext.py``` 
    and entering a keyword related to your documents.  
