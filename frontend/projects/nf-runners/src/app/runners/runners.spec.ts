import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Runners } from './runners';

describe('Runners', () => {
  let component: Runners;
  let fixture: ComponentFixture<Runners>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Runners]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Runners);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
