import { Component, OnInit } from '@angular/core';
import { HardwareService, ComponentEntry } from "../hardware.service";
import { Observable, of, from, timer} from 'rxjs';
import { catchError, map, tap, flatMap, reduce, merge } from 'rxjs/operators';

@Component({
  selector: 'app-hardware',
  templateUrl: './hardware.component.html',
  styleUrls: ['./hardware.component.css']
})
export class HardwareComponent implements OnInit {

  constructor(private hardwareService : HardwareService) { }

  components : ComponentEntry[] = [];

  kUPDATE_PERIOD_MS : number = 1000;

  ngOnInit() {

    // Get component array
    this.hardwareService.getComponents().pipe(
      // Create a stream for individual elements
      flatMap(components => from(components)),

      // Add it to the list
      tap(component => this.components.push(component)),

      // Fetch component value
      flatMap(component => this.readComponentValue(component)),

      // Reduce result
      reduce( c => c)
    ).subscribe( () => {

      // Update values periodically
      timer(this.kUPDATE_PERIOD_MS, this.kUPDATE_PERIOD_MS).subscribe(
        () => from(this.components).pipe(
          flatMap(component => this.readComponentValue(component))
          ).subscribe()
      );
    });
  }

  /**
   * Create observer which reads the value for given component, and pipes it out
   *
   * @param component  Component
   */
  readComponentValue(component : ComponentEntry) : Observable<ComponentEntry> {
    return this.hardwareService.readValue(component.id).pipe(
      tap(value => component.value = value),
      map(value => component));
  }


  onClick(component : ComponentEntry) : void {
    this.hardwareService.toggleSwitch(component.id).subscribe(isOn => component.value = isOn ? 1.0 : 0.0);
  }
}
