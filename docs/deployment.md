# Deploying Pexa

This guide covers how to deploy Pexa on your own server using Docker Compose and Caddy as a reverse proxy. Caddy handles HTTPS automatically via Let's Encrypt.


## Considerations

This guide will get you going with a simple sqlite3 database through a volume mount and Caddy with a self signed certificate. For more complex setups, feel free to explore using Pexa behind any proxy of your choosing! :D

## Prerequisites

- A Linux server (VPS, home server, etc.)
- A domain name pointed at your server's public IP
- Ports 80 and 443 open on your firewall

## 1. Install dependencies

You'll need `git`, `make`, and Docker (with the Compose plugin).

**Ubuntu:**

```sh
sudo apt install -y git make
```

For Docker, follow the [official Docker installation guide for Ubuntu](https://docs.docker.com/engine/install/ubuntu/#installation-methods) to install Docker and the Compose plugin.

Allow your user to run Docker without `sudo`:

```sh
sudo usermod -aG docker $USER
newgrp docker
```

**Arch:**

```sh
sudo pacman -Sy --noconfirm git make docker docker-compose
sudo systemctl enable --now docker

# Allow your user to run Docker without sudo
sudo usermod -aG docker $USER
newgrp docker
```

## 2. Clone the repository

```sh
git clone https://github.com/TiagoMauricio/pexa.git
cd pexa
```

## 3. Build the Docker image

```sh
make build
```

This creates the `pexa:latest` image locally.

## 4. Create the environment file

Copy the example file:

```sh
cp env.example .env
```

Edit `.env` with your values:

```env
SECRET_KEY=<your-secret-key>
REFRESH_TOKEN_SECRET_KEY=<your-refresh-token-secret-key>
DATABASE_URL=sqlite:////app/data/db.sqlite3
DOMAIN=api.yourdomain.com
```

Replace `api.yourdomain.com` with the domain or subdomain pointing at your server.

> `CORS_ORIGINS` is optional. If you have a front-end app at a specific origin, set it to that URL (e.g. `CORS_ORIGINS=https://myapp.example.com`). Defaults to `*` (all origins).

To generate values for `SECRET_KEY` and `REFRESH_TOKEN_SECRET_KEY`, run:

```sh
openssl rand -hex 32
```

Run it twice — once for each value.

## 5. Create the Caddyfile

Caddy uses a `Caddyfile` to configure the reverse proxy and provision TLS certificates.

There's already a Caddyfile in the repo. Replace the domain to match your own:

```
api.yourdomain.com {
    reverse_proxy pexa:8000
}
```

Caddy will automatically obtain and renew a TLS certificate for that domain via Let's Encrypt. No further TLS configuration is needed.

## 6. Create the data directory

The database file is stored in `./data` on the host. Create the directory and set the correct ownership before starting the stack:

```sh
mkdir -p data
sudo chown -R 100:100 data
```

The container runs as a non-root user with UID/GID `1000`. Without the correct ownership Docker will mount the directory as `root` and the container won't be able to write the database file.

## 7. Start the stack

```sh
make run
```

This runs `docker compose up -d`, starting both the `pexa` and `caddy` containers.

On first start, Pexa automatically applies all database migrations before the API becomes available.

## 8. Verify the deployment

Check that the API is healthy:

```sh
curl https://api.yourdomain.com/api/health
# {"status":"ok"}
```

## Useful commands

```sh
make logs      # Tail logs from all services
make status    # Show container status
make restart   # Restart all containers
make stop      # Stop the stack
```

## Updating

When a new version is released, pull the latest code, rebuild the image, and restart:

```sh
git pull
make build
make restart
```

Migrations are applied automatically on each container start.
