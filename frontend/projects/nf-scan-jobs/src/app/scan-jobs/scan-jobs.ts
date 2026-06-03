import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { ApiService, ScanJob, Target } from 'shared';

@Component({
  selector: 'app-scan-jobs',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './scan-jobs.html',
  styleUrl: './scan-jobs.scss',
})
export class ScanJobsComponent implements OnInit {
  jobs: ScanJob[] = [];
  targets: Target[] = [];
  selectedTargetId = '';
  loading = false;
  running = false;
  error = '';

  constructor(private readonly api: ApiService) {}

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.loading = true;
    this.error = '';

    this.api.getTargets().subscribe({
      next: (targets) => {
        this.targets = targets;

        if (!this.selectedTargetId && targets.length > 0) {
          this.selectedTargetId = targets[0].id;
        }

        this.loadJobs();
      },
      error: () => {
        this.error = 'No se pudieron cargar los targets.';
        this.loading = false;
      },
    });
  }

  loadJobs(): void {
    this.api.getScanJobs().subscribe({
      next: (jobs) => {
        this.jobs = jobs;
        this.loading = false;
      },
      error: () => {
        this.error = 'No se pudieron cargar los scan jobs.';
        this.loading = false;
      },
    });
  }

  runScan(): void {
    if (!this.selectedTargetId) {
      this.error = 'Selecciona un target antes de ejecutar el scan.';
      return;
    }

    this.running = true;
    this.error = '';

    this.api.createScanJob(this.selectedTargetId).subscribe({
      next: () => {
        this.running = false;
        this.loadJobs();
      },
      error: () => {
        this.running = false;
        this.error = 'No se pudo crear el scan job.';
      },
    });
  }

  getStatusClass(status: string): string {
    return `status ${status}`;
  }
}