import asyncio
from utils import console, OPENAI_API_KEY
import os

# TODO add this later
#import agentops
#agentops.init()

from agents import Agent, Runner, WebSearchTool, trace

async def main():
    agent = Agent(
        name = "Hunter",
        instructions = "Respond in detail to the question:",
        tools = [
            WebSearchTool(
            )
        ]
    )

    result = await Runner.run(
        agent,
        "What's 77 * 3?"
    )

    print(result.final_output)

if __name__ == "__main__":
    os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
    asyncio.run(main())