import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { ApiService, Finding } from 'shared';

@Component({
  selector: 'app-findings',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './findings.html',
  styleUrl: './findings.scss',
})
export class FindingsComponent implements OnInit {
  findings: Finding[] = [];
  severity = '';
  loading = false;
  error = '';

  constructor(private readonly api: ApiService) {}

  ngOnInit(): void {
    this.loadFindings();
  }

  loadFindings(): void {
    this.loading = true;
    this.error = '';

    this.api.getFindings(this.severity).subscribe({
      next: (findings) => {
        this.findings = findings;
        this.loading = false;
      },
      error: () => {
        this.error = 'No se pudieron cargar los findings.';
        this.loading = false;
      },
    });
  }

  getSeverityClass(severity: string): string {
    return `severity ${severity}`;
  }
}