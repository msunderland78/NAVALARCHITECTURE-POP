# POP NGINX

This directory contains the NGINX reverse-proxy configuration for the POP web application.

The NGINX container proxies all requests to the Python backend service. The backend serves both the static frontend and the JSON API.

Run from `POP-NEW/app`:

```sh
docker-compose up --build
```

The host port is selected by `POP_HOST_PORT` in `docker-compose.yml`. If it is not set, Compose publishes NGINX on port `8080`.
