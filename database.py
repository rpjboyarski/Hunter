from dataclasses import dataclass, asdict
from typing import Self
import os
import json

# Host data structure
# Store the IP address, hostname (can be null), open ports (if any), responds to pings (if any)
# Also store the last time the host was interacted with, the operating system version (if known), and an array of known CVEs (if any)
# Also store known software versions that are tied to ports (if any). For example, if we know port 80 is running Apache 2.4.7, store that in the port, and XREF the version here to that port

# Actions data structure
# Log all tool calls, including arguments and raw results. Include a FOREIGN KEY reference to hosts that were interacted with

# Engagement context data structure
# This is like a repository for the current set of actions we're taking. The actions and hosts are "children" of this object
# For example, I could create a UIUC engagement context, where I want to find live hosts in UIUC but do nothing illegal
# Then, all actions taken and identified hosts should be "children" of this context
# This will also optionally a string for rules of engagement, like an additional system prompt

# Create a datatype for a service, which includes port, name, protocol, version, and a list of known vulnerabilities


@dataclass
class Service:
    port: int
    name: str = None
    protocol: str = None
    version: str = None
    vulnerabilities: list = None

@dataclass
class Host:
    ip: str
    hostname: str = None
    services: list = None
    last_interaction: str = None
    os_version: str = None

@dataclass
class Action:
    tool: str
    arguments: dict
    raw_results: str
    host: Host


@dataclass
class EngagementContext:
    name: str
    actions: list[Action]
    hosts: list[Host]

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return EngagementContext(
            name=data["name"],
            actions=[Action(**action) for action in data["actions"]],
            hosts=[Host(**host) for host in data["hosts"]]
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "actions": list(map(asdict, self.actions)),
            "hosts": list(map(asdict, self.hosts))
        }

database = {}
current_engagement = ""

def load_db():
    with open("targets.json", "r") as file:
        return {k: EngagementContext.from_dict(v) for k, v in json.load(file).items()}

def save_db():
    with open("targets.json", "w") as file:
        json.dump({k:v.to_dict() for k,v in database.items()}, file, indent=4)

def add_host(ip: str, hostname: str = None, services: list = None, os_version: str = None):
    global current_engagement
    if current_engagement not in database:
        raise ValueError("Engagement context not initialized")

    host = None

    for h in database[current_engagement].hosts:
        if h.ip == ip:
            host = h
            break

    if not host:
        database[current_engagement].hosts.append(Host(ip=ip))
        host = database[current_engagement].hosts[-1]

    if hostname:
        host.hostname = hostname
    if services:
        host.services = services
    if os_version:
        host.os_version = os_version
    save_db()

def init_db(name):
    global current_engagement
    current_engagement = name
    if not os.path.exists("targets.json"):
        with open("targets.json", "w") as file:
            json.dump({k:asdict(v) for k, v in database.items()}, file)

    load_db()
    if name not in database:
        database[name] = EngagementContext(name=name, actions=[], hosts=[])
    save_db()
