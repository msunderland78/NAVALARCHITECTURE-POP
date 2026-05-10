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

Open `http://127.0.0.1:8080/`.

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
