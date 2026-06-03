import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ApiService, FindingsSummary } from 'shared';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})
export class DashboardComponent implements OnInit {
  summary: FindingsSummary | null = null;
  loading = false;
  error = '';

  constructor(private readonly api: ApiService) {}

  ngOnInit(): void {
    this.loadSummary();
  }

  loadSummary(): void {
    this.loading = true;
    this.error = '';

    this.api.getFindingsSummary().subscribe({
      next: (summary: FindingsSummary) => {
        this.summary = summary;
        this.loading = false;
      },
      error: () => {
        this.error = 'No se pudo cargar el resumen de findings.';
        this.loading = false;
      },
    });
  }
}