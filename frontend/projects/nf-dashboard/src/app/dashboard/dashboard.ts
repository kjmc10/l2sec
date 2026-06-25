import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ApiService, DashboardSummary } from 'shared';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
  ],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})
export class DashboardComponent implements OnInit {
  summary?: DashboardSummary;

  loading = false;
  error = '';

  constructor(private readonly api: ApiService) { }

  ngOnInit(): void {
    this.loadDashboard();
  }

  loadDashboard(): void {
    this.loading = true;
    this.error = '';

    this.api.getDashboardSummary().subscribe({
      next: (summary) => {
        this.summary = summary;
        this.loading = false;
      },
      error: () => {
        this.error = 'No se pudo cargar el dashboard.';
        this.loading = false;
      },
    });
  }

  getScoreClass(): string {
    if (!this.summary) {
      return 'score neutral';
    }

    const score = this.summary.security_score;

    if (score >= 85) {
      return 'score good';
    }

    if (score >= 60) {
      return 'score warning';
    }

    return 'score bad';
  }

  getQualityGateClass(): string {
    if (!this.summary) {
      return 'gate neutral';
    }

    return `gate ${this.summary.quality_gate}`;
  }

  getScanStatusClass(status: string): string {
    return `scan-status ${status}`;
  }
}