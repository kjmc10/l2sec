import { Component, Input } from '@angular/core';

@Component({
  selector: 'shared-status-badge',
  standalone: true,
  template: `
    <span [class]="status">
      {{ status }}
    </span>
  `,
})
export class StatusBadgeComponent {
  @Input() status = '';
}
