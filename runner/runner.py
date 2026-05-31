import time
from urllib.parse import urlparse

import requests

from config import (
    CONTROL_PLANE_URL,
    HEARTBEAT_INTERVAL_SECONDS,
    RUNNER_NAME,
    RUNNER_TOKEN,
)


def get_headers():
    return {
        "Authorization": f"Bearer {RUNNER_TOKEN}",
    }


def send_heartbeat():
    url = f"{CONTROL_PLANE_URL}/v1/runners/heartbeat"

    try:
        response = requests.post(
            url,
            headers=get_headers(),
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


def get_next_job():
    url = f"{CONTROL_PLANE_URL}/v1/runner/jobs/next"

    try:
        response = requests.get(
            url,
            headers=get_headers(),
            timeout=10,
        )

        if response.status_code != 200:
            print(
                "get_next_job_error",
                response.status_code,
                response.text,
            )
            return None

        if not response.text or response.text == "null":
            return None

        return response.json()

    except requests.RequestException as exc:
        print(
            "get_next_job_exception",
            str(exc),
        )
        return None


def update_job_status(scan_job_id, status, message=None):
    url = f"{CONTROL_PLANE_URL}/v1/runner/jobs/{scan_job_id}/status"

    payload = {
        "status": status,
        "message": message,
    }

    try:
        response = requests.post(
            url,
            headers=get_headers(),
            json=payload,
            timeout=10,
        )

        print(
            "update_job_status",
            status,
            response.status_code,
            response.text,
        )

        return response.status_code == 200

    except requests.RequestException as exc:
        print(
            "update_job_status_exception",
            str(exc),
        )
        return False


def validate_allowed_host(target_url, allowed_host):
    parsed_url = urlparse(target_url)

    if not parsed_url.hostname:
        return False

    return parsed_url.hostname == allowed_host


def process_job(job):
    scan_job_id = job["id"]
    target = job["target"]

    target_url = target["url"]
    allowed_host = target["allowed_host"]
    scan_type = job["scan_type"]

    print(f"picked_job id={scan_job_id} scan_type={scan_type} target={target_url}")

    if not validate_allowed_host(
        target_url=target_url,
        allowed_host=allowed_host,
    ):
        update_job_status(
            scan_job_id=scan_job_id,
            status="failed",
            message="Target URL hostname does not match allowed_host.",
        )
        return

    update_job_status(
        scan_job_id=scan_job_id,
        status="running",
        message="Runner started simulated scan.",
    )

    print(f"simulating_scan target={target_url}")

    time.sleep(5)

    update_job_status(
        scan_job_id=scan_job_id,
        status="completed",
        message="Simulated scan completed successfully.",
    )


def main():
    print(f"Starting runner: {RUNNER_NAME}")
    print(f"Control plane URL: {CONTROL_PLANE_URL}")

    while True:
        send_heartbeat()

        job = get_next_job()

        if job:
            process_job(job)
        else:
            print("no_pending_jobs")

        time.sleep(HEARTBEAT_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()