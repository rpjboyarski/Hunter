from rich.console import Console
import os
from dotenv import dotenv_values

config = dotenv_values(".env")

console = Console()
# Read .env to get API keys
HUNTER_API_KEY = config["HUNTER_API_KEY"]
OPENAI_API_KEY = config["OPENAI_API_KEY"]