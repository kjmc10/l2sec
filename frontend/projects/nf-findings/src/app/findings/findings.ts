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
  filtered: Finding[] = [];

  loading = false;
  error = '';

  // filtros
  severityFilter = '';
  statusFilter = '';
  search = '';

  // drawer
  selected?: Finding;
  updating = false;

  constructor(private readonly api: ApiService) {}

  ngOnInit(): void {
    this.loadFindings();
  }

  loadFindings(): void {
    this.loading = true;

    this.api.getFindings().subscribe({
      next: (data) => {
        this.findings = data;
        this.applyFilters();
        this.loading = false;
      },
      error: () => {
        this.error = 'Error loading findings';
        this.loading = false;
      },
    });
  }

  applyFilters(): void {
    this.filtered = this.findings.filter((f) => {
      const matchesSeverity =
        !this.severityFilter || f.severity === this.severityFilter;

      const matchesStatus =
        !this.statusFilter || f.status === this.statusFilter;

      const matchesSearch =
        !this.search ||
        f.name.toLowerCase().includes(this.search.toLowerCase()) ||
        (f.url ?? '').toLowerCase().includes(this.search.toLowerCase());

      return matchesSeverity && matchesStatus && matchesSearch;
    });
  }

  openDetail(f: Finding) {
    this.selected = f;
  }

  closeDetail() {
    this.selected = undefined;
  }

  updateStatus(status: string) {
    if (!this.selected) return;

    this.updating = true;

    this.api.updateFindingStatus(this.selected.id, status).subscribe({
      next: (updated) => {
        this.selected = updated;

        // actualizar lista local
        const index = this.findings.findIndex(f => f.id === updated.id);
        if (index !== -1) this.findings[index] = updated;

        this.applyFilters();
        this.updating = false;
      },
      error: () => {
        this.updating = false;
      },
    });
  }
}