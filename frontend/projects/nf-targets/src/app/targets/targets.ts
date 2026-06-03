import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import {
  ApiService,
  Target,
  TargetCreatePayload,
} from 'shared';

@Component({
  selector: 'app-targets',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink,
  ],
  templateUrl: './targets.html',
  styleUrl: './targets.scss',
})
export class TargetsComponent implements OnInit {
  targets: Target[] = [];

  loading = false;
  creating = false;
  runningTargetId = '';
  error = '';
  success = '';

  form: TargetCreatePayload = {
    name: '',
    url: '',
    environment: 'staging',
  };

  constructor(private readonly api: ApiService) {}

  ngOnInit(): void {
    this.loadTargets();
  }

  loadTargets(): void {
    this.loading = true;
    this.error = '';
    this.success = '';

    this.api.getTargets().subscribe({
      next: (targets) => {
        this.targets = targets;
        this.loading = false;
      },
      error: () => {
        this.error = 'No se pudieron cargar los targets.';
        this.loading = false;
      },
    });
  }

  createTarget(): void {
    if (!this.form.name || !this.form.url || !this.form.environment) {
      this.error = 'Completa name, url y environment.';
      return;
    }

    this.creating = true;
    this.error = '';
    this.success = '';

    this.api.createTarget(this.form).subscribe({
      next: () => {
        this.creating = false;
        this.success = 'Target creado correctamente.';

        this.form = {
          name: '',
          url: '',
          environment: 'staging',
        };

        this.loadTargets();
      },
      error: () => {
        this.creating = false;
        this.error = 'No se pudo crear el target. Verifica que la URL sea válida.';
      },
    });
  }

  runScan(target: Target): void {
    this.runningTargetId = target.id;
    this.error = '';
    this.success = '';

    this.api.createScanJob(target.id).subscribe({
      next: () => {
        this.runningTargetId = '';
        this.success = `Scan baseline creado para ${target.name}.`;
      },
      error: () => {
        this.runningTargetId = '';
        this.error = 'No se pudo crear el scan job.';
      },
    });
  }

  getEnvironmentClass(environment: string): string {
    return `env ${environment}`;
  }
}