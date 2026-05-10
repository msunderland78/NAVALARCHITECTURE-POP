# POP Web Application

This directory contains the Linux-native replacement for the legacy POP desktop application.

Planned layout:

- `backend`: calculation engine and API
- `frontend`: browser interface
- `nginx`: deployment configuration

The production application must not depend on files from `POP-OLD`.

Run locally without containers:

```sh
PYTHONPATH=POP-NEW/app/backend python3 POP-NEW/app/backend/pop_http.py --host 127.0.0.1 --port 8080
```

Run with Docker Compose from `POP-NEW/app`:

```sh
docker-compose up --build
```

The default host port is `8080`. Open the application at:

```text
http://SERVER_IP:8080/
```

To use a different host port, set `POP_HOST_PORT` before starting Compose:

```sh
POP_HOST_PORT=9090 docker-compose up --build
```

Then open:

```text
http://SERVER_IP:9090/
```

For a persistent local setting, copy `.env.example` to `.env` and edit `POP_HOST_PORT`. Docker Compose reads `.env` automatically from this directory.

For HTTPS/TLS deployments, keep this application running HTTP inside Docker and terminate TLS outside the app with a solution selected by the deployer, such as a host NGINX proxy, Caddy, Traefik, NGINX Proxy Manager, Let’s Encrypt, or OpenSSL-managed certificates. The outer TLS proxy should forward requests to the published POP port, for example `http://127.0.0.1:8080`.

`POP_HOST_PORT` can also include a bind address if the deployer wants POP reachable only from a local TLS proxy:

```sh
POP_HOST_PORT=127.0.0.1:8080 docker-compose up --build
```

Do not commit certificates or private keys. Local certificate material should be kept outside git, or under `POP-NEW/app/certs/`, which is ignored.

Check container status and health:

```sh
docker-compose ps
```

If the host has Docker Compose v2, this equivalent command also works:

```sh
docker compose up --build
```

If Docker reports permission denied for `/var/run/docker.sock`, add the user to the `docker` group and start a new login session:

```sh
sudo usermod -aG docker $USER
```
