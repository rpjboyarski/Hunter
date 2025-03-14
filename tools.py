from agents import function_tool
import subprocess

from database import add_host
from utils import console
from utils import HUNTER_API_KEY
import base64
import requests
from datetime import datetime
from rich.table import Table
from rich import box


@function_tool
def rustscan(host: str) -> str:
    """
    Scan the host for open ports. This function uses the rustscan tool, and offers excellent speed.
    Note that it is unable to penetrate the Windows Defender firewall.
    :param host: The host to scan.
    :return: The result of the scan.
    """
    console.print(f"[bold blue][*][/bold blue] Scanning host {host} with Rustscan")
    result = subprocess.run(f"rustscan -a {host} --ulimit 5000 --greppable", shell=True, capture_output=True)
    console.print(f"[bold green][+][/bold green] Scan complete")
    result = result.stdout.decode("utf-8")
    print(result.stdout.decode("utf-8"))
    return result.stdout.decode("utf-8")

@function_tool
def nmapscan(host: str, args: str) -> str:
    """
    Uses nmap to scan the target, accepting any arguments that nmap would accept.
    If you are passing multiple hosts, do it with the hyphenated syntax, e.g. "10.10.10.0-255".
    A good baseline would be something like "-sS -sV -T4 -Pn -A -v -oN scan.txt"
    :param host: The host to scan.
    :param args: The arguments to pass to nmap.
    :return: The result of the scan.
    """
    command = f"nmap -v {args} {host}"
    console.print(f"[bold blue][*][/bold blue] Scanning host {host} with: {command}")
    result = subprocess.run(command, shell=True, capture_output=True)
    console.print(f"[bold green][+][/bold green] Scan complete")
    if result.stdout:
        result = result.stdout.decode("utf-8")
    else:
        result = result.stderr.decode("utf-8")
    print(result)
    return result

@function_tool
def ping_network(subnet: str) -> [str]:
    """
    Pings the entire subnet to determine which hosts are up.
    If a host is running a firewall, it may not respond to pings.
    :param subnet: The subnet to ping.
    :return: A list of each identified host on the subnet.
    """
    console.print(f"[bold blue][*][/bold blue] Pinging subnet {subnet}")
    result = subprocess.run("nmap -n -sn " + subnet + " -T5 -oG - | awk '/Up$/{print $2}'", shell=True,
                            capture_output=True)
    print(result.stdout.decode("utf-8"))
    result = result.stdout.decode("utf-8").split("\n")
    for i in range(len(result)):
        if result[i] == "":
            result.pop(i)
    console.print(f"[bold green][+][/bold green] Ping complete")

    for ip in result:
        add_host(ip)

    console.print(f"[bold green][+][/bold green] Added {len(result)} hosts to the database")
    return result


# User Function
def hunter(query: str, page=1, page_size=100, start_time="2025-01-01", end_time="2025-12-01") -> str:
    """
    Execute a hunter.how query to scan the entire internet using the given query.

    Queries must follow this format:

    # General
    - IPv4 address: ip=="1.1.1.1"
    - Port: ip.port=="443
    - Domain: domain=="example.com"
    - Web Title: web.title=="Google"
    - Web Body: web.body=="Cyber"
    - CIDR: ip=="220.181.111.0/24"
    - Protocol: protocol=="http"
    - Transport Protocol: protocol.transport=="udp"

    # Geolocation
    - Country: ip.country="US
    - State/Province: ip.state="California"
    - City: ip.city=="Los Angeles"

    # Product
    - Product name: product.name="WordPress"
    - Product version: product.version=="6.0"

    # Autonomous System
    - ASN: as.number=="136800"
    - ASN Name: as.name="CLOUDFLARENET"
    - ASN Registry: as.org="PDR"

    # Special
    - IPs port count: ip.port_count>"2"
    - Protocol in the response banner: protocol.banner="nginx"

    # Querying
    - Exact queries: ==
    - Fuzzy queries: =
    - Negative exact queries: !==
    - Negative fuzzy queries: !=
    - Compound queries: and, &&, or, ||

    ALL DATA FOR HUNTER QUERIES MUST BE ENCLOSED IN QUOTES. THIS REQUIRES ESCAPING YOUR JSON.

    :param query: The query to execute.
    :param page: (OPTIONAL) The page of results to return.
    :param page_size: (OPTIONAL) The number of results per page.
    :param start_time: (OPTIONAL) Ignore hosts last seen before this time.
    :param end_time: (OPTIONAL) Ignore hosts last seen after this time.
    :return: The result of the query.
    """
    console.print(f"[bold blue][*][/bold blue] Executing Hunter query: {query}")
    try:
        # base64 url-safe
        encoded_query = base64.urlsafe_b64encode(query.encode()).decode()
        url = f"https://api.hunter.how/search?api-key={HUNTER_API_KEY}&query={encoded_query}&page={page}&page_size={page_size}&start_time={start_time}&end_time={end_time}"
        result = requests.get(url).json()
    except Exception as e:
        console.print(f"[bold red][!][/bold red] Error executing Hunter query: {str(e)}")
        return str(e)

    with open(f"logs/hunter_query_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json", "w") as f:
        f.write(str(result))
        console.print(f"[bold green][+][/bold green] Query complete. Result saved to {f.name}")

    return result

@function_tool
def hunter_llm(ip: str = None,
               domain: str = None,
               port: int = None,
               protocol: str = None,
               protocol_transport: str = None,
               country: str = None,
               state: str = None,
               city: str = None,
               product_name: str = None,
               product_version: str = None,
               asn: int = None,
               asn_name: str = None,
               asn_registry: str = None,
               ips_port_count: int = None,
               protocol_banner: str = None) -> str:
    """
    Execute a hunter.how query to scan the entire internet using the given query.
    THIS FUNCTION DOES NOT WORK ON YOUR LOCAL NETWORK. IF YOU ARE PERFORMING AN INTERNAL ASSESSMENT, USE nmapscan INSTEAD!
    :param ip: (OPTIONAL) The IPv4 address to search for.
    :param domain: (OPTIONAL) The domain to search for.
    :param port: (OPTIONAL) The port to search for.
    :param protocol: (OPTIONAL) The protocol to search for.
    :param country: (OPTIONAL) The country to search for. If you're looking for the United States, pass US
    :param state: (OPTIONAL) The state to search for.
    :param city: (OPTIONAL) The city to search for.
    :param product_name: (OPTIONAL) The product name to search for.
    :param product_version: (OPTIONAL) The product version to search for.
    :param asn: (OPTIONAL) The ASN to search for.
    :param asn_name: (OPTIONAL) The ASN name to search for.
    :param asn_registry: (OPTIONAL) The ASN registry to search for.
    :param ips_port_count: (OPTIONAL) The IPs port count to search for.
    :param protocol_banner: (OPTIONAL) The protocol banner to search for.
    :return: The result of the query.
    """

    # Build the query
    query = ""
    def append_query(query, key, value):
        if query != "":
            query += " and "
        query += f"{key}==\"{value}\""
        return query

    if ip:
        query = append_query(query, "ip", ip)
    if domain:
        query = append_query(query, "domain", domain)
    if port:
        query = append_query(query, "ip.port", port)
    if protocol:
        query = append_query(query, "protocol", protocol)
    if protocol_transport:
        query = append_query(query, "protocol.transport", protocol_transport)
    if country:
        query = append_query(query, "ip.country", country)
    if state:
        query = append_query(query, "ip.state", state)
    if city:
        query = append_query(query, "ip.city", city)
    if product_name:
        query = append_query(query, "product.name", product_name)
    if product_version:
        query = append_query(query, "product.version", product_version)
    if asn:
        query = append_query(query, "as.number", asn)
    if asn_name:
        query = append_query(query, "as.name", asn_name)
    if asn_registry:
        query = append_query(query, "as.org", asn_registry)
    if ips_port_count:
        query = append_query(query, "ip.port_count", ips_port_count)
    if protocol_banner:
        query = append_query(query, "protocol.banner", protocol_banner)

    response = hunter(query)
    print_hunter_response(response)
    return response

# User Function
def print_hunter_response(response):
    # Table 1: Usage Metrics
    usage_table = Table(
        title="API Usage Metrics",
        title_style="bold magenta",
        show_header=True,
        header_style="bold cyan",
        box=box.ROUNDED,
        expand=True
    )
    usage_table.add_column("Metric", style="dim")
    usage_table.add_column("Value")

    metrics = {
        "Daily Search Limit": response["data"]["per_day_search_limit"],
        "Searches Used": response["data"]["per_day_search_count"],
        "API Pull Limit": response["data"]["per_day_api_pull_limit"],
        "API Pulls Used": response["data"]["per_day_api_pull_count"],
    }

    for key, value in metrics.items():
        usage_table.add_row(key, str(value))

    # Table 2: Domain List
    domain_table = Table(
        title="Domain/IP/Port List",
        title_style="bold magenta",
        show_header=True,
        header_style="bold cyan",
        box=box.ROUNDED,
        expand=True
    )
    domain_table.add_column("Domain", style="dim")
    domain_table.add_column("IP Address")
    domain_table.add_column("Port", justify="right")

    for entry in response["data"]["list"]:
        domain = entry.get("domain", "-")
        ip = entry["ip"]
        port = entry["port"]
        domain_table.add_row(domain, ip, str(port))

    # Print everything
    console.print(f"[bold green]API Status: {response['message']} (Code {response['code']})[/bold green]")
    console.print(usage_table)
    console.print(f"\n[bold]Total Entries Found: {response['data']['total']}[/bold]")
    console.print(domain_table)

@function_tool
def shodan_get_host_data(host: str) -> str:
    """
    Uses Shodan to get pre-existing data on a host, mostly ports and services.
    This will never work on a private IP address
    Uses the Shodan Internet Database.
    :param host: The host to get data on (hostname or IPv4)
    :return: The data on the host.
    """
    console.print(f"[bold blue][*][/bold blue] Getting existing data on host {host}")
    try:
        result = requests.get(f"https://internetdb.shodan.io/{host}").json()
    except Exception as e:
        console.print(f"[bold red][!][/bold red] Error getting existing data on host: {str(e)}")
        return str(e)
    console.print(f"[bold green][+][/bold green] Host data retrieval complete")
    print(result)
    return result
