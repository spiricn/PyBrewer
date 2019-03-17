import { TestBed } from '@angular/core/testing';

import { HardwareService } from './hardware.service';

describe('HardwareService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: HardwareService = TestBed.get(HardwareService);
    expect(service).toBeTruthy();
  });
});
