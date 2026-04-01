#!/usr/bin/env python3
import os
import socket
import time
import requests
import miniupnpc

PANEL_URL = os.environ.get("PANEL_URL", "http://localhost")
API_KEY = os.environ.get("API_KEY", "")
IGNORE_ALIAS = {"ignore", "local"}
IGNORE_IP = {"127.0.0.1"}
UPNP_DURATION = 600  # 10 minutes


def api_get(path: str) -> dict:
    response = requests.get(
        f"{PANEL_URL}/api/application/{path}",
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        },
    )
    response.raise_for_status()
    return response.json()


def get_nodes() -> list[dict]:
    return [entry["attributes"] for entry in api_get("nodes")["data"]]


def get_allocations(node_id: int) -> list[dict]:
    return [entry["attributes"] for entry in api_get(f"nodes/{node_id}/allocations")["data"]]


def get_local_ip() -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]


def resolve_ip(fqdn: str) -> str:
    return socket.gethostbyname(fqdn)


def find_current_node(nodes: list[dict], local_ip: str) -> dict | None:
    for node in nodes:
        if resolve_ip(node["fqdn"]) == local_ip:
            return node
    return None


def setup_upnp() -> miniupnpc.UPnP:
    upnp = miniupnpc.UPnP()
    upnp.discoverdelay = 200
    devices = upnp.discover()
    if not devices:
        raise RuntimeError("No UPnP devices found on the network")
    upnp.selectigd()
    print(f"UPnP gateway: {upnp.externalipaddress()}")
    return upnp


def add_port_mapping(upnp: miniupnpc.UPnP, node_ip: str, port: int, proto: str, label: str) -> None:
    result = upnp.addportmapping(
        port,                              # external port
        proto,                             # 'TCP' or 'UDP'
        node_ip,                           # internal IP (this node)
        port,                              # internal port
        f"[ptero-upnp] {proto} {label}",  # description
        "",                                # remote host (empty = any)
    )
    status = "OK" if result else "FAILED"
    print(f"    [{status}] {proto} {node_ip}:{port}")


def main() -> None:
    local_ip = get_local_ip()
    upnp = setup_upnp()

    nodes = get_nodes()
    node = find_current_node(nodes, local_ip)

    if node is None:
        raise RuntimeError(
            f"Could not find a Pterodactyl node matching this machine's IP ({local_ip}). "
            "Check that the node's FQDN resolves to this machine."
        )

    print(f"Identified as node: {node['name']} ({node['fqdn']} -> {local_ip})\n")

    for alloc in get_allocations(node["id"]):
        ip: str = alloc["ip"]
        alias: str = alloc["alias"]
        assigned: bool = alloc["assigned"]
        port: int = alloc["port"]

        if alias in IGNORE_ALIAS:
            continue
        if ip in IGNORE_IP:
            continue
        if not assigned:
            continue

        label = f"{ip}:{port} ({alias})"
        print(f"  {label} is assigned")

        first_word = (alias or "").split()[0] if alias else ""
        protos = [first_word] if first_word in ("TCP", "UDP") else ["TCP", "UDP"]

        for proto in protos:
            add_port_mapping(upnp, local_ip, port, proto, label)

    print()


if __name__ == "__main__":
    while True:
        main()
        print("Sleeping for 5 minutes...\n")
        time.sleep(300)