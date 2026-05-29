import time
import requests

from config import CONTROL_PLANE_URL, RUNNER_NAME


def main():
    print(f"Starting runner: {RUNNER_NAME}")
    print(f"Control plane: {CONTROL_PLANE_URL}")

    while True:
        try:
            response = requests.get(f"{CONTROL_PLANE_URL}/v1/health", timeout=5)
            print(f"Control plane health: {response.status_code} {response.text}")
        except Exception as exc:
            print(f"Error connecting to control plane: {exc}")

        time.sleep(10)


if __name__ == "__main__":
    main()