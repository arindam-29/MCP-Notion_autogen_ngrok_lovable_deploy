import asyncio
import os
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from pyngrok import ngrok

load_dotenv()
# Load environment variables
NGROK_AUTH_TOKEN = os.getenv('NGROK_AUTH_TOKEN')
NOTION_API_KEY = os.getenv('NOTION_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# System message for the agent
SYSTEM_MESSAGE = "You are a helpful assistant that can search and summarize content from the user's Notion workspace and also list what is asked.Try to assume the tool and call the same and get the answer. Say TERMINATE when you are done with the task."


async def setup_team():
    params = StdioServerParams(
        command="npx",
        args=['-y','mcp-remote','https://mcp.notion.com/mcp'],
        env={
            'NOTION_API_KEY':NOTION_API_KEY
        },
        read_timeout_seconds=20
    )

    model = OpenAIChatCompletionClient(
        model="o4-mini",
        api_key=os.getenv('OPENAI_API_KEY')
    )

    mcp_tools= await mcp_server_tools(server_params=params)

    agent= AssistantAgent(
        name='notion_agent',
        system_message=SYSTEM_MESSAGE,
        model_client=model,
        tools=mcp_tools,
        reflect_on_tool_use=True
    )

    team = RoundRobinGroupChat(
        participants=[agent],
        max_turns=5,
        termination_condition=TextMentionTermination('TERMINATE')
    )

    return team
