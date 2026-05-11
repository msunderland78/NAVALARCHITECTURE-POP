import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DeploymentFileTests(unittest.TestCase):
    def test_dockerfile_does_not_copy_legacy_folder(self):
        dockerfile = (ROOT / "app/backend/Dockerfile").read_text()

        self.assertIn("python:3.12.8-slim", dockerfile)
        self.assertIn("COPY --chown=pop:pop backend", dockerfile)
        self.assertIn("COPY --chown=pop:pop frontend", dockerfile)
        self.assertIn("USER pop:pop", dockerfile)
        self.assertIn("useradd", dockerfile)
        self.assertIn("HEALTHCHECK", dockerfile)
        self.assertIn("/health", dockerfile)
        self.assertNotIn("POP-OLD", dockerfile)

    def test_compose_uses_nginx_and_backend(self):
        compose = (ROOT / "app/docker-compose.yml").read_text()

        self.assertIn("pop-backend", compose)
        self.assertIn("nginx:1.27-alpine", compose)
        self.assertIn("${POP_HOST_PORT:-8080}:80", compose)
        self.assertIn("healthcheck", compose)
        self.assertIn("/health", compose)

    def test_docs_include_standalone_compose_command(self):
        readme = (ROOT / "app/README.md").read_text()

        self.assertIn("docker-compose up --build", readme)
        self.assertIn("POP_HOST_PORT", readme)
        self.assertIn("SERVER_IP", readme)
        self.assertIn("HTTPS/TLS", readme)
        self.assertIn("Let", readme)
        self.assertIn("OpenSSL", readme)
        self.assertIn("127.0.0.1:8080", readme)
        self.assertIn("docker-compose ps", readme)
        self.assertIn("usermod -aG docker", readme)

    def test_top_level_readme_describes_public_pop_release(self):
        readme = (ROOT.parent / "README.md").read_text()

        self.assertIn("Propeller Optimization Program (POP) for the Web", readme)
        self.assertIn("Version 1.0, May 2026", readme)
        self.assertIn("Wageningen B-Series", readme)
        self.assertIn("Advance coefficient", readme)
        self.assertIn("docker-compose up --build", readme)
        self.assertIn("POP_HOST_PORT", readme)
        self.assertIn("HTTPS", readme)

    def test_env_example_documents_public_port(self):
        env_example = (ROOT / "app/.env.example").read_text()

        self.assertIn("POP_HOST_PORT=8080", env_example)

    def test_local_env_file_is_ignored(self):
        gitignore = (ROOT.parent / ".gitignore").read_text()

        self.assertIn("POP-NEW/app/.env", gitignore)
        self.assertIn("POP-NEW/app/certs/", gitignore)

    def test_nginx_proxies_to_backend(self):
        config = (ROOT / "app/nginx/nginx.conf").read_text()

        self.assertIn("server pop-backend:8080", config)
        self.assertIn("proxy_pass http://pop_backend", config)
        self.assertIn("client_max_body_size 2m", config)

    def test_nginx_hardening_directives(self):
        config = (ROOT / "app/nginx/nginx.conf").read_text()

        self.assertIn("server_tokens off", config)
        self.assertIn("listen [::]:80", config)
        self.assertIn("proxy_connect_timeout", config)
        self.assertIn("proxy_read_timeout", config)
        self.assertIn("limit_req_zone", config)
        self.assertIn("location /api/run", config)
        self.assertIn("limit_req zone=pop_run", config)

    def test_pyproject_declares_numpy_runtime_dep(self):
        text = (ROOT / "pyproject.toml").read_text()

        self.assertIn("name = \"pop\"", text)
        self.assertIn("requires-python = \">=3.12\"", text)
        self.assertIn("numpy~=2.2", text)

    def test_dockerfile_installs_numpy(self):
        dockerfile = (ROOT / "app/backend/Dockerfile").read_text()

        self.assertIn("pip install --no-cache-dir", dockerfile)
        self.assertIn("numpy~=2.2", dockerfile)

    def test_ci_workflow_runs_tests_and_builds_image(self):
        workflow = (ROOT.parent / ".github/workflows/ci.yml").read_text()

        self.assertIn("python-version-file: POP-NEW/.python-version", workflow)
        self.assertIn("python -m unittest discover -s tests", workflow)
        self.assertIn("docker build -f POP-NEW/app/backend/Dockerfile", workflow)
        self.assertIn("docker compose -f POP-NEW/app/docker-compose.yml config", workflow)

    def test_python_version_pin_present(self):
        text = (ROOT / ".python-version").read_text().strip()

        self.assertTrue(text.startswith("3.12"))

    def test_dockerignore_excludes_old_folders(self):
        dockerignore = (ROOT / "app/.dockerignore").read_text()

        self.assertIn("*-OLD/", dockerignore)
        self.assertIn("certs/", dockerignore)
        self.assertIn("*.key", dockerignore)
        self.assertIn("*.pem", dockerignore)


if __name__ == "__main__":
    unittest.main()
