import asyncio
import agentops

agentops.init()

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
    asyncio.run(main())