from database import init_db
from utils import console, OPENAI_API_KEY, HUNTER_API_KEY, AGENTOPS_API_KEY
import os
from rich import print
from rich.markdown import Markdown
from rich.panel import Panel
from prompting import *
from agents import Agent, Runner, set_default_openai_key
import readline
from database import init_db


from tools import rustscan, nmapscan, ping_network, hunter_llm, shodan_get_host_data
from ui import print_banner
import agentops
agentops.init(api_key=AGENTOPS_API_KEY)
system_prompt = system_prompt_from_template(system_prompt_template, user_system_prompt)

ai_name = "Hunter"

class Hunter():
    def __init__(self):
        self.agent = Agent(
            name = "Hunter",
            instructions = system_prompt,
            tools = [
                rustscan,
                nmapscan,
                ping_network,
                hunter_llm,
                shodan_get_host_data,
            ],
        )

        self.initial_messages = [
            {'role': 'system', 'content': system_prompt},
        ]

        self.result = None

    def start_run(self):
        username = os.getenv("USER", "user")
        self.initial_greeting = f"Hello, {username}. Ready to cause some [bold red]chaos[/bold red]?"

        # Display initial greeting
        console.print(Panel(self.initial_greeting, title=ai_name, border_style="green", padding=(1, 2)))
        console.print("[bold cyan]Type 'quit' to exit the chatbot[/bold cyan]")
        console.print("[bold cyan]Type 'reset' to start a new conversation[/bold cyan]")

        query = console.input("[bold blue]You:[/bold blue] ")
        if query.lower() == "quit":
            self.leave_chat()
        self.result = Runner.run_sync(self.agent, query)

        self.run()

    def run(self):
        if not self.result:
            self.start_run()

        while True:
            new_query = console.input("[bold blue]You:[/bold blue] ")
            if new_query.strip() == "":
                continue
            if new_query.lower() == "quit":
                self.leave_chat()
            if new_query.lower() == "reset":
                # Reset conversation
                console.print("[bold yellow]Conversation reset. Starting new session on Groq.[/bold yellow]")
                # Re-print greeting
                console.print(Panel(self.initial_greeting, title=ai_name, border_style="green", padding=(1, 2)))
                self.start_run()
                self.leave_chat()
            new_input = self.result.to_input_list() + [{"role": "user", "content": new_query}]
            result = Runner.run_sync(self.agent, new_input)
            console.print(result.final_output)

    def leave_chat(self):
        console.print(Panel("[bold]Be seeing you[/bold]",
                            title=ai_name,
                            border_style="green",
                            padding=(1, 2)))
        exit()


def init_env_variables():
    os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
    os.environ['HUNTER_API_KEY'] = HUNTER_API_KEY
    set_default_openai_key(OPENAI_API_KEY)

if __name__ == "__main__":
    init_env_variables()
    print_banner()
    console.print("[bold]Welcome to [red]HUNTER[/red] - Autonomous network reconnaissance agent[/bold]",
                  justify="center")
    engagement = console.input("[bold]Enter the engagement name:[/bold] ")
    init_db(engagement)
    hunter = Hunter()
    hunter.start_run()
