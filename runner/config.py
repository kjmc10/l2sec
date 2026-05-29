import os


CONTROL_PLANE_URL = os.getenv(
    "CONTROL_PLANE_URL",
    "http://localhost:8000",
)

RUNNER_TOKEN = os.getenv(
    "RUNNER_TOKEN",
    "dev-runner-token",
)

RUNNER_NAME = os.getenv(
    "RUNNER_NAME",
    "local-runner-01",
)

HEARTBEAT_INTERVAL_SECONDS = int(
    os.getenv(
        "HEARTBEAT_INTERVAL_SECONDS",
        "10",
    )
)