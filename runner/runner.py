import time
from urllib.parse import urlparse

import requests

from config import (
    CONTROL_PLANE_URL,
    HEARTBEAT_INTERVAL_SECONDS,
    RUNNER_NAME,
    RUNNER_TOKEN,
)

from zap_executor import run_zap_baseline


def headers():
    return {"Authorization": f"Bearer {RUNNER_TOKEN}"}


def send_heartbeat():
    requests.post(f"{CONTROL_PLANE_URL}/v1/runners/heartbeat", headers=headers())


def get_next_job():
    r = requests.get(
        f"{CONTROL_PLANE_URL}/v1/runner/jobs/next",
        headers=headers(),
    )

    if r.status_code != 200 or r.text == "null":
        return None

    return r.json()


def update_status(job_id, status):
    requests.post(
        f"{CONTROL_PLANE_URL}/v1/runner/jobs/{job_id}/status",
        headers=headers(),
        json={"status": status},
    )


def send_results(job_id, findings):
    requests.post(
        f"{CONTROL_PLANE_URL}/v1/runner/jobs/{job_id}/results",
        headers=headers(),
        json={"findings": findings},   # ✅ IMPORTANTE
    )


def validate_host(url, allowed_host):
    return urlparse(url).hostname == allowed_host


def process_job(job):
    job_id = job["id"]
    target = job["target"]

    url = target["url"]
    allowed_host = target["allowed_host"]

    if not validate_host(url, allowed_host):
        update_status(job_id, "failed")
        return

    update_status(job_id, "running")

    findings = run_zap_baseline(url)

    send_results(job_id, findings)

    update_status(job_id, "completed")


def main():
    print(f"Runner started: {RUNNER_NAME}")

    while True:
        try:
            send_heartbeat()
            job = get_next_job()

            if job:
                process_job(job)
            else:
                print("no jobs")

        except Exception as e:
            print("error:", e)

        time.sleep(HEARTBEAT_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()