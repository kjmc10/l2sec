import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';

export interface DashboardSeveritySummary {
  high: number;
  medium: number;
  low: number;
  info: number;
  total: number;
}

export interface DashboardStatusSummary {
  open: number;
  false_positive: number;
  accepted_risk: number;
  fixed: number;
}

export interface DashboardLatestScan {
  id: string;
  target_id: string;
  runner_id?: string | null;
  scan_type: string;
  status: string;
  upload_mode: string;
  created_at: string;
  started_at?: string | null;
  finished_at?: string | null;
}

export interface DashboardSummary {
  security_score: number;
  quality_gate: string;
  findings: {
    severity: DashboardSeveritySummary;
    status: DashboardStatusSummary;
  };
  scan_jobs: {
    summary: {
      total: number;
      queued: number;
      running: number;
      completed: number;
      failed: number;
    };
    latest: DashboardLatestScan[];
  };
  runners: {
    online: number;
    total: number;
  };
  targets: {
    total: number;
  };
}
export interface Finding {
  id: string;
  scan_job_id: string;
  target_id: string;
  name: string;
  severity: string;
  confidence?: string | null;
  url?: string | null;
  method?: string | null;
  cwe?: string | null;
  owasp_category?: string | null;
  evidence?: string | null;
  remediation?: string | null;
  status: string;
  created_at: string;
}

export interface FindingsSummary {
  high: number;
  medium: number;
  low: number;
  info: number;
  total: number;
}

export interface ScanJob {
  id: string;
  target_id: string;
  runner_id?: string | null;
  scan_type: string;
  status: string;
  upload_mode: string;
  created_at: string;
  started_at?: string | null;
  finished_at?: string | null;
}

export interface Target {
  id: string;
  name: string;
  url: string;
  environment: string;
  allowed_host: string;
  created_at: string;
}

export interface TargetCreatePayload {
  name: string;
  url: string;
  environment: string;
}

export interface Runner {
  id: string;
  name: string;
  is_online: boolean;
  last_seen_at?: string | null;
  created_at: string;
}

export interface RunnerCreated {
  id: string;
  name: string;
  token: string;
  is_online: boolean;
  created_at: string;
}

export interface RunnerRotateTokenResponse {
  id: string;
  name: string;
  token: string;
  is_online: boolean;
  last_seen_at?: string | null;
  created_at: string;
}

export interface RunnerCreatePayload {
  name: string;
}

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private readonly baseUrl = 'http://localhost:8000/v1';

  constructor(private readonly http: HttpClient) { }

  getDashboardSummary() {
    return this.http.get<DashboardSummary>(`${this.baseUrl}/dashboard/summary`);
  }
  
  getRunners() {
    return this.http.get<Runner[]>(`${this.baseUrl}/runners`);
  }

  createRunner(payload: RunnerCreatePayload) {
    return this.http.post<RunnerCreated>(`${this.baseUrl}/runners`, payload);
  }

  rotateRunnerToken(runnerId: string) {
    return this.http.post<RunnerRotateTokenResponse>(
      `${this.baseUrl}/runners/${runnerId}/rotate-token`,
      {}
    );
  }

  getFindings(severity?: string) {
    let params = new HttpParams();

    if (severity) {
      params = params.set('severity', severity);
    }

    return this.http.get<Finding[]>(`${this.baseUrl}/findings`, {
      params,
    });
  }

  getFindingsSummary() {
    return this.http.get<FindingsSummary>(`${this.baseUrl}/findings/summary`);
  }


  updateFindingStatus(id: string, status: string) {
    return this.http.patch<Finding>(
      `${this.baseUrl}/findings/${id}/status`,
      { status }
    );
  }

  getScanJobs() {
    return this.http.get<ScanJob[]>(`${this.baseUrl}/scan-jobs`);
  }

  createScanJob(targetId: string) {
    return this.http.post<ScanJob>(`${this.baseUrl}/scan-jobs`, {
      target_id: targetId,
      scan_type: 'baseline',
      upload_mode: 'sanitized',
    });
  }

  getTargets() {
    return this.http.get<Target[]>(`${this.baseUrl}/targets`);
  }

  createTarget(payload: TargetCreatePayload) {
    return this.http.post<Target>(`${this.baseUrl}/targets`, payload);
  }

}