# Deploying Pexa

This guide covers how to deploy Pexa on your own server using Docker Compose and Caddy as a reverse proxy. Caddy handles HTTPS automatically via Let's Encrypt.

## Prerequisites

- A Linux server (VPS, home server, etc.) with Docker and Docker Compose installed
- A domain name pointed at your server's public IP
- Ports 80 and 443 open on your firewall

## 1. Clone the repository

```sh
git clone https://github.com/TiagoMauricio/pexa.git
cd pexa
```

## 2. Build the Docker image

```sh
make build
```

This creates the `pexa:latest` image locally.

## 3. Generate secret keys

Pexa requires three secret values. Run the following commands to generate them:

```sh
# SECRET_KEY and REFRESH_TOKEN_SECRET_KEY
openssl rand -hex 32
openssl rand -hex 32

# FERNET_KEY (requires the cryptography package)
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Keep these values — you'll put them in the `.env` file next.

## 4. Create the environment file

Copy the example file and fill in your values:

```sh
cp env.example .env
```

Edit `.env`:

```env
SECRET_KEY=<your-generated-secret-key>
REFRESH_TOKEN_SECRET_KEY=<your-generated-refresh-token-secret-key>
FERNET_KEY=<your-generated-fernet-key>
DATABASE_URL=sqlite:////app/data/db.sqlite3
DOMAIN=api.yourdomain.com
```

Replace `api.yourdomain.com` with the domain or subdomain pointing at your server.

> `CORS_ORIGINS` is optional. If you have a front-end app at a specific origin, set it to that URL (e.g. `CORS_ORIGINS=https://myapp.example.com`). Defaults to `*` (all origins).

## 5. Create the Caddyfile

Caddy uses a `Caddyfile` to configure the reverse proxy and provision TLS certificates. Create one in the project root:

```sh
touch Caddyfile
```

Add the following content, replacing the domain with your own:

```
api.yourdomain.com {
    reverse_proxy pexa:8000
}
```

Caddy will automatically obtain and renew a TLS certificate for that domain via Let's Encrypt. No further TLS configuration is needed.

## 6. Create the data directory

The database file is stored in `./data` on the host. Create the directory before starting the stack:

```sh
mkdir -p data
```

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
