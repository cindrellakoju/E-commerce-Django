import subprocess
import sys
import time
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerce.settings")

def is_docker_running():
    """Check if Docker is running by running 'docker info'."""
    try:
        subprocess.run(
            ["docker", "info"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        print("Docker is not installed or not in PATH.")
        sys.exit(1)

def run_docker_compose():
    """Start containers using docker-compose."""
    try:
        print("Starting Docker Compose services...")
        subprocess.run(["docker-compose", "up", "-d"], check=True)
    except subprocess.CalledProcessError:
        print("Failed to start Docker Compose services.")
        sys.exit(1)

def stop_docker_compose():
    """Stop containers using docker-compose."""
    try:
        print("\nStopping Docker Compose services...")
        subprocess.run(["docker-compose", "down"], check=True)
    except subprocess.CalledProcessError:
        print("Failed to stop Docker Compose services.")

def run_uvicorn_server():
    """Run Django ASGI server with Uvicorn."""
    try:
        print("Starting Django ASGI server with Uvicorn...")
        subprocess.run([
            sys.executable, "-m", "uvicorn", "ecommerce.asgi:application", "--reload", "--host", "0.0.0.0", "--port", "8000"
        ])
        # subprocess.run([
        #     sys.executable, "-m", "uvicorn", "ecommerce.asgi:application",
        #     "--reload",
        #     "--host", "0.0.0.0",
        #     "--port", "8000",
        #     "--ssl-keyfile", "key.pem",
        #     "--ssl-certfile", "cert.pem",
        # ])
    except subprocess.CalledProcessError:
        print("Failed to start Uvicorn server")
        stop_docker_compose()
        sys.exit(1)

if __name__ == "__main__":
    if not is_docker_running():
        print("Docker Desktop is OFF. Please start Docker and try again.")
        sys.exit(1)

    run_docker_compose()
    time.sleep(5)  # Give containers a few seconds to start

    try:
        run_uvicorn_server()
    except KeyboardInterrupt:
        # Catch Ctrl+C and stop Docker containers
        stop_docker_compose()
        print("Script stopped.")
        sys.exit(0)
