from database import init_db
from utils import console, OPENAI_API_KEY, HUNTER_API_KEY, AGENTOPS_API_KEY
import os
from rich import print
from rich.markdown import Markdown
from rich.panel import Panel
from prompting import *
from agents import Agent, Runner
from openai import chat
import readline
from database import init_db


from tools import rustscan, nmapscan, ping_network, hunter_llm, shodan_get_host_data
from ui import print_banner
import agentops
agentops.init(api_key=AGENTOPS_API_KEY)
system_prompt = system_prompt_from_template(system_prompt_template, user_system_prompt)

ai_name = "Hunter"
show_thinking = False

agent = Agent(
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

def query_model(query: str, messages: [], stream=False) -> str:
    console.print(messages)

    # result = Runner.run_sync(
    #     agent,
    #     input = query,
    #     context = messages
    # )
    result = Runner.run_sync(agent, query)

    return result.final_output


def chat_interface():
    # Initial greeting
    global show_thinking
    username = os.getenv("USER", "user")
    initial_greeting = f"Hello, {username}. Ready to cause some [bold red]chaos[/bold red]?"
    messages = get_initial_messages()
    query = []

    # Display initial greeting
    console.print(Panel(initial_greeting, title=ai_name, border_style="green", padding=(1, 2)))
    console.print("[bold cyan]Type 'quit' to exit the chatbot[/bold cyan]")
    console.print("[bold cyan]Type 'reset' to start a new conversation[/bold cyan]")
    console.print(f"[bold cyan]Type 'thinking' to toggle thinking window (currently [{'green' if show_thinking else 'red'}]{'ON' if show_thinking else 'OFF'}[/{'green' if show_thinking else 'red'}])[/bold cyan]")

    query = console.input("[bold blue]You:[/bold blue] ")
    result = Runner.run_sync(agent, query)
    while True:
        new_query = console.input("[bold blue]You:[/bold blue] ")
        new_input = result.to_input_list() + [{"role": "user", "content": new_query}]
        result = Runner.run_sync(agent, new_input)
        console.print(result.final_output)

    while True:
        try:
            query = console.input("[bold blue]You:[/bold blue] ")
        except (EOFError, KeyboardInterrupt):
            print("")
            leave_chat()
            break

        if query.lower() == "quit":
            leave_chat()
            break

        if query.lower() == "reset":
            # Reset conversation
            messages = get_initial_messages()
            console.print("[bold yellow]Conversation reset. Starting new session on Groq.[/bold yellow]")
            # Re-print greeting
            console.print(Panel(initial_greeting, title=ai_name, border_style="green", padding=(1, 2)))
            continue

        if query.lower() == "thinking":
            show_thinking = not show_thinking
            status = f"[{'green' if show_thinking else 'red'}]{'ON' if show_thinking else 'OFF'}[/{'green' if show_thinking else 'red'}]"
            console.print(f"[bold yellow]Thinking window is now {status}[/bold yellow]")
            continue

        if query.strip() == "":
            continue

        # Add user message to history

        # Stream response with or without thinking indicators
        response_content = ""
        if show_thinking:
            console.print(f"[bold green]{ai_name} is thinking...[/bold green]")
            with console.status("[bold green]Processing...[/bold green]", spinner="dots"):
                response_content = query_model(query=query, messages=messages, stream=False)
            console.print(response_content)
        else:
            # TODO does not turn off thinking
            response_content = query_model(query=query, messages=messages, stream=False)
            console.print(response_content)

        if show_thinking:
            # Display the complete response
            console.print(Panel(Markdown(response_content),
                                title=ai_name,
                                border_style="green",
                                padding=(1, 2)))

        # Add user message to history
        messages.append({"role": "user", "content": query})
        # Add AI message to history
        messages.append({"role": "assistant", "content": response_content})

def main():
    if not os.path.exists("logs"):
        console.print("[bold blue][*][/bold blue] Creating logs directory")
        os.mkdir("logs")
    chat_interface()

def leave_chat():
    console.print(Panel("[bold]Be seeing you[/bold]",
                        title=ai_name,
                        border_style="green",
                        padding=(1, 2)))
    exit()


def get_initial_messages():
    initial_messages = [
        { 'role': 'system', 'content': system_prompt},
    ]

    return initial_messages


def init_env_variables():
    os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
    os.environ['HUNTER_API_KEY'] = HUNTER_API_KEY

if __name__ == "__main__":
    init_env_variables()
    print_banner()
    console.print("[bold]Welcome to [red]HUNTER[/red] - Autonomous network reconnaissance agent[/bold]",
                  justify="center")
    engagement = console.input("[bold]Enter the engagement name:[/bold] ")
    init_db(engagement)
    main()
    leave_chat()