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
