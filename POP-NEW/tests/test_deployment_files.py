import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DeploymentFileTests(unittest.TestCase):
    def test_dockerfile_does_not_copy_legacy_folder(self):
        dockerfile = (ROOT / "app/backend/Dockerfile").read_text()

        self.assertIn("python:3.12-slim", dockerfile)
        self.assertIn("COPY backend", dockerfile)
        self.assertIn("COPY frontend", dockerfile)
        self.assertNotIn("POP-OLD", dockerfile)

    def test_compose_uses_nginx_and_backend(self):
        compose = (ROOT / "app/docker-compose.yml").read_text()

        self.assertIn("pop-backend", compose)
        self.assertIn("nginx:1.27-alpine", compose)
        self.assertIn("8080:80", compose)

    def test_nginx_proxies_to_backend(self):
        config = (ROOT / "app/nginx/nginx.conf").read_text()

        self.assertIn("server pop-backend:8080", config)
        self.assertIn("proxy_pass http://pop_backend", config)

    def test_dockerignore_excludes_old_folders(self):
        dockerignore = (ROOT / "app/.dockerignore").read_text()

        self.assertIn("*-OLD/", dockerignore)


if __name__ == "__main__":
    unittest.main()
