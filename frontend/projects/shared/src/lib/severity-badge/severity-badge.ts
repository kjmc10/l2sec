import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'shared-severity-badge',
  standalone: true,
  imports: [CommonModule],
  template: `
    <span [class]="getClass()">
      {{ severity }}
    </span>
  `,
  styleUrls: ['./severity-badge.css'],
})
export class SeverityBadgeComponent {
  @Input() severity = '';

  getClass() {
    return 'badge ' + this.severity;
  }
}