# HUNTER
## Agentic Autonomous Network Reconaissance Tool
**Hunter** is an AI agent designed for autonomous network reconaissance of both external and internal networks. 
It uses OpenAI's Agents SDK and AgentOps for tool calling.

## 🛠️ Supported Tools
**Nmap**: For scanning internal networks

**Hunter.how**: A free alternative to Shodan, allows for searching of devices on the internet

**Shodan**: The free endpoint for IP enrichment

**Rustscan**: A blazingly fast alternative to nmap, lacks versatility but makes up for it with speed

**Ping sweep**: A special case of nmap, designed for quickly identifying hosts on a network

## Database Integration
Certain tools (currently the ping sweep) will automatically save the results to a NoSQL database, which is human readable and LLM-readable.

## Installation
This tool will not function without a few necessary components:
1. OpenAI API Key
2. AgentOps API Key
3. Hunter.how API Key (Free!)
4. Kali Linux tools (nmap & rustscan)

The API keys must be placed in a .env file in the root directory of the project with the following format:
```
OPENAI_API_KEY=REDACTED
HUNTER_API_KEY=REDACTED
AGENTOPS_API_KEY=REDACTED
```

## Usage
Enter the virtualenv with `source .venv/bin/activate`. Then, usage is as easy as `python3 main.py`.
You will be prompted to enter an engagement name - this can be whatever you want, it exists solely to track actions in the database.
