import time

import requests

from config import (
    CONTROL_PLANE_URL,
    HEARTBEAT_INTERVAL_SECONDS,
    RUNNER_NAME,
    RUNNER_TOKEN,
)


def send_heartbeat() -> None:
    url = f"{CONTROL_PLANE_URL}/v1/runners/heartbeat"

    headers = {
        "Authorization": f"Bearer {RUNNER_TOKEN}",
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            timeout=10,
        )

        print(
            "heartbeat",
            response.status_code,
            response.text,
        )

    except requests.RequestException as exc:
        print(
            "heartbeat_error",
            str(exc),
        )


def main() -> None:
    print(f"Starting runner: {RUNNER_NAME}")
    print(f"Control plane URL: {CONTROL_PLANE_URL}")

    while True:
        send_heartbeat()
        time.sleep(HEARTBEAT_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()