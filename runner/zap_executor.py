import json
import os
import subprocess
import uuid


ZAP_IMAGE = "zaproxy/zap-stable"


def run_zap_baseline(target_url):
    job_id = str(uuid.uuid4()).replace("-", "")

    report_filename = f"zap_report_{job_id}.json"
    report_host_path = f"/tmp/{report_filename}"

    cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        "/tmp:/zap/wrk",
        ZAP_IMAGE,
        "zap-baseline.py",
        "-t",
        target_url,
        "-J",
        report_filename,
    ]

    try:
        print("\n🚀 Starting ZAP scan...")
        print("CMD:", " ".join(cmd))

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        # 👇 imprime salida en vivo
        for line in process.stdout:
            print(line.strip())

        process.wait()

        # ✅ aceptar códigos 0, 1 y 2
        if process.returncode not in [0, 1, 2]:
            print("❌ ZAP failed with critical error:", process.returncode)
            return []

        print(f"✅ ZAP finished with code {process.returncode} (treated as success)")


        if not os.path.exists(report_host_path):
            print("❌ Report not found:", report_host_path)
            return []

        with open(report_host_path, "r") as f:
            data = json.load(f)

        print("✅ Report loaded")

        findings = parse_zap_findings(data)

        print(f"✅ Parsed findings: {len(findings)}")

        return findings

    except Exception as e:
        print("❌ Exception running ZAP:", e)
        return []


def parse_zap_findings(zap_json):
    findings = []

    sites = zap_json.get("site", [])

    for site in sites:
        alerts = site.get("alerts", [])

        for alert in alerts:
            instances = alert.get("instances", [])

            for instance in instances:
                findings.append({
                    "name": alert.get("name"),
                    "severity": map_risk(alert.get("risk")),
                    "confidence": alert.get("confidence"),
                    "url": instance.get("uri"),
                    "method": instance.get("method"),
                    "cwe": str(alert.get("cweid")),
                    "owasp_category": alert.get("alertRef"),
                    "evidence": "[SANITIZED]",
                    "remediation": alert.get("solution"),
                })

    return findings


def map_risk(risk):
    return {
        "High": "high",
        "Medium": "medium",
        "Low": "low",
        "Informational": "info",
    }.get(risk, "info")