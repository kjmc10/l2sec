import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import {
  ApiService,
  Runner,
  RunnerCreated,
  RunnerRotateTokenResponse,
} from 'shared';

@Component({
  selector: 'app-runners',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
  ],
  templateUrl: './runners.html',
  styleUrl: './runners.scss',
})
export class RunnersComponent implements OnInit {
  runners: Runner[] = [];

  loading = false;
  creating = false;
  rotatingId = '';

  error = '';
  success = '';

  runnerName = 'local-runner-01';

  latestSecret: RunnerCreated | RunnerRotateTokenResponse | null = null;
  revealSecret = false;

  constructor(private readonly api: ApiService) {}

  ngOnInit(): void {
    this.loadRunners();
  }

  loadRunners(): void {
    this.loading = true;
    this.error = '';
    this.success = '';

    this.api.getRunners().subscribe({
      next: (runners) => {
        this.runners = runners;
        this.loading = false;
      },
      error: () => {
        this.error = 'No se pudieron cargar los runners.';
        this.loading = false;
      },
    });
  }

  createRunner(): void {
    if (!this.runnerName.trim()) {
      this.error = 'Ingresa un nombre para el runner.';
      return;
    }

    this.creating = true;
    this.error = '';
    this.success = '';
    this.latestSecret = null;
    this.revealSecret = false;

    this.api.createRunner({
      name: this.runnerName.trim(),
    }).subscribe({
      next: (runner) => {
        this.creating = false;
        this.latestSecret = runner;
        this.success = 'Runner creado. Copia el client secret y úsalo como RUNNER_TOKEN.';
        this.loadRunners();
      },
      error: () => {
        this.creating = false;
        this.error = 'No se pudo crear el runner.';
      },
    });
  }

  rotateToken(runner: Runner): void {
    this.rotatingId = runner.id;
    this.error = '';
    this.success = '';
    this.latestSecret = null;
    this.revealSecret = false;

    this.api.rotateRunnerToken(runner.id).subscribe({
      next: (response) => {
        this.rotatingId = '';
        this.latestSecret = response;
        this.success = `Nuevo client secret generado para ${response.name}.`;
        this.loadRunners();
      },
      error: () => {
        this.rotatingId = '';
        this.error = 'No se pudo rotar el token.';
      },
    });
  }

  toggleReveal(): void {
    this.revealSecret = !this.revealSecret;
  }

  copySecret(): void {
    if (!this.latestSecret?.token) {
      return;
    }

    navigator.clipboard.writeText(this.latestSecret.token);
    this.success = 'Client secret copiado al portapapeles.';
  }

  getRunnerCommand(): string {
    if (!this.latestSecret?.token) {
      return '';
    }

    return `export CONTROL_PLANE_URL="http://localhost:8000"
export RUNNER_NAME="${this.latestSecret.name}"
export RUNNER_TOKEN="${this.latestSecret.token}"
export HEARTBEAT_INTERVAL_SECONDS="5"
python3 runner.py`;
  }
}