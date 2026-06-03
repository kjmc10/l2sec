import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ScanJobs } from './scan-jobs';

describe('ScanJobs', () => {
  let component: ScanJobs;
  let fixture: ComponentFixture<ScanJobs>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ScanJobs]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ScanJobs);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
