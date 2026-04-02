# PteroUPnP

Automatically creates UPnP port mappings for [Pterodactyl Panel](https://pterodactyl.io/) node allocations. Discovers which node it's running on, fetches all assigned port allocations from the panel API, and maps them on your router via UPnP.

## How It Works

1. Detects the local IP and discovers the UPnP gateway (router)
2. Queries the Pterodactyl API to find which node matches this machine's IP
3. Fetches all port allocations assigned to that node
4. Creates UPnP port mappings for each allocation
5. Repeats every 5 minutes

### Allocation Filtering

- Only **assigned** allocations (those linked to a server) are mapped
- Allocations with aliases `ignore` or `local` are skipped
- Allocations on `127.0.0.1` are skipped
- The first word of an alias sets the protocol: `tcp`, `udp`, or both if unspecified

## Setup

### Requirements

- A UPnP-enabled router
- A [Pterodactyl Panel](https://pterodactyl.io/) Application API key
- The node's FQDN must resolve to its local or external IP (can also be set directly to an IP address)

### Environment Variables

| Variable    | Description                          | Default            |
|-------------|--------------------------------------|--------------------|
| `PANEL_URL` | URL of your Pterodactyl Panel        | `http://localhost`  |
| `API_KEY`   | Pterodactyl Application API key      | (none)             |

### Docker (Recommended)

Copy the example compose file and configure it:

```bash
cp docker-compose.example.yml docker-compose.yml
```

Edit `docker-compose.yml` to set your `PANEL_URL` and `API_KEY`, then:

```bash
docker compose up -d
```

> **Note:** `network_mode: host` is required so the container can reach the UPnP gateway.

The image is also available on Docker Hub as [`strangewill/pteroupnp`](https://hub.docker.com/r/strangewill/pteroupnp).

### Manual

```bash
pip install -r requirements.txt
PANEL_URL=http://your-panel.com API_KEY=your_key python main.py
```

## License

[MIT](LICENSE)
