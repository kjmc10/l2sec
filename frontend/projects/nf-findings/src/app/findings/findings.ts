import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { forkJoin } from 'rxjs';

import {
  ApiService,
  Finding,
  SeverityBadgeComponent,
  StatusBadgeComponent,
} from 'shared';

@Component({
  selector: 'app-findings',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    SeverityBadgeComponent,
    StatusBadgeComponent,
  ],
  templateUrl: './findings.html',
  styleUrl: './findings.scss',
})
export class FindingsComponent implements OnInit {
  findings: Finding[] = [];
  filtered: Finding[] = [];

  loading = false;
  error = '';

  severityFilter = '';
  statusFilter = '';
  search = '';

  selected?: Finding;
  updating = false;

  selectedIds = new Set<string>();

  toastMessage = '';
  toastType: 'success' | 'error' | '' = '';

  constructor(private readonly api: ApiService) {}

  ngOnInit(): void {
    this.loadFindings();
  }

  loadFindings(): void {
    this.loading = true;
    this.error = '';

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
    const normalizedSearch = this.search.trim().toLowerCase();

    this.filtered = this.findings.filter((f) => {
      const matchesSeverity =
        !this.severityFilter || f.severity === this.severityFilter;

      const matchesStatus =
        !this.statusFilter || f.status === this.statusFilter;

      const matchesSearch =
        !normalizedSearch ||
        f.name.toLowerCase().includes(normalizedSearch) ||
        (f.url ?? '').toLowerCase().includes(normalizedSearch);

      return matchesSeverity && matchesStatus && matchesSearch;
    });

    this.sortBySeverity();
  }

  sortBySeverity(): void {
    const order = ['high', 'medium', 'low', 'info'];

    this.filtered.sort((a, b) => {
      const severityA = order.indexOf(a.severity);
      const severityB = order.indexOf(b.severity);

      const safeSeverityA = severityA === -1 ? order.length : severityA;
      const safeSeverityB = severityB === -1 ? order.length : severityB;

      return safeSeverityA - safeSeverityB;
    });
  }

  clearFilters(): void {
    this.search = '';
    this.severityFilter = '';
    this.statusFilter = '';
    this.applyFilters();
  }

  openDetail(finding: Finding): void {
    this.selected = { ...finding };
  }

  closeDetail(): void {
    this.selected = undefined;
  }

  updateStatus(status: string): void {
    if (!this.selected) {
      return;
    }

    const selectedId = this.selected.id;
    const previousSelected = { ...this.selected };

    const index = this.findings.findIndex((f) => f.id === selectedId);
    const previousFinding = index !== -1 ? { ...this.findings[index] } : undefined;

    this.updating = true;
    this.error = '';

    /**
     * Optimistic update:
     * Actualizamos la UI antes de que responda el backend.
     */
    this.patchLocalFindingStatus(selectedId, status);

    this.api.updateFindingStatus(selectedId, status).subscribe({
      next: (updated) => {
        const nextStatus = updated.status ?? status;

        this.patchLocalFindingStatus(selectedId, nextStatus);

        this.updating = false;
        this.showToast('Finding status updated', 'success');
      },
      error: () => {
        /**
         * Rollback:
         * Si falla backend, devolvemos el estado anterior.
         */
        if (previousFinding && index !== -1) {
          this.findings[index] = previousFinding;
        }

        if (this.selected && this.selected.id === selectedId) {
          this.selected = previousSelected;
        }

        this.applyFilters();
        this.updating = false;
        this.showToast('Error updating finding status', 'error');
      },
    });
  }

  patchLocalFindingStatus(id: string, status: string): void {
    const index = this.findings.findIndex((f) => f.id === id);

    if (index !== -1) {
      this.findings[index] = {
        ...this.findings[index],
        status,
      };
    }

    if (this.selected && this.selected.id === id) {
      this.selected = {
        ...this.selected,
        status,
      };
    }

    this.applyFilters();
  }

  toggleSelect(id: string): void {
    if (this.selectedIds.has(id)) {
      this.selectedIds.delete(id);
    } else {
      this.selectedIds.add(id);
    }
  }

  isSelected(id: string): boolean {
    return this.selectedIds.has(id);
  }

  allFilteredSelected(): boolean {
    return (
      this.filtered.length > 0 &&
      this.filtered.every((finding) => this.selectedIds.has(finding.id))
    );
  }

  toggleSelectAllFiltered(): void {
    if (this.allFilteredSelected()) {
      this.filtered.forEach((finding) => this.selectedIds.delete(finding.id));
    } else {
      this.filtered.forEach((finding) => this.selectedIds.add(finding.id));
    }
  }

  clearSelection(): void {
    this.selectedIds.clear();
  }

  bulkUpdate(status: string): void {
    const ids = Array.from(this.selectedIds);

    if (ids.length === 0) {
      return;
    }

    const previousFindings = this.findings.map((f) => ({ ...f }));
    const previousSelected = this.selected ? { ...this.selected } : undefined;

    this.updating = true;
    this.error = '';

    /**
     * Optimistic bulk update.
     */
    ids.forEach((id) => {
      this.patchLocalFindingStatus(id, status);
    });

    const requests = ids.map((id) =>
      this.api.updateFindingStatus(id, status)
    );

    forkJoin(requests).subscribe({
      next: (updatedFindings) => {
        for (const updated of updatedFindings) {
          const nextStatus = updated.status ?? status;
          this.patchLocalFindingStatus(updated.id, nextStatus);
        }

        this.selectedIds.clear();
        this.updating = false;
        this.showToast(`${ids.length} findings updated`, 'success');
      },
      error: () => {
        /**
         * Rollback completo si falla algún request.
         */
        this.findings = previousFindings;

        if (previousSelected) {
          this.selected = previousSelected;
        }

        this.applyFilters();
        this.updating = false;
        this.showToast('Error updating selected findings', 'error');
      },
    });
  }

  getRowClass(finding: Finding): string {
    return `row severity-${finding.severity} status-${finding.status}`;
  }

  showToast(message: string, type: 'success' | 'error'): void {
    this.toastMessage = message;
    this.toastType = type;

    setTimeout(() => {
      this.toastMessage = '';
      this.toastType = '';
    }, 2500);
  }
}