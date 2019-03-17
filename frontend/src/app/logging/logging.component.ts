import { Component, AfterViewInit } from '@angular/core';

import { LogService, LogMessage } from "../log.service";
import { refreshDescendantViews } from '@angular/core/src/render3/instructions';

@Component({
  selector: 'app-logging',
  templateUrl: './logging.component.html',
  styleUrls: ['./logging.component.css']
})
export class LoggingComponent implements AfterViewInit {

  constructor(private logService : LogService) { }

  data : LogMessage[] = [];
  displayedColumns: string[] = ['module', 'message'];

  ngAfterViewInit() {
    this.refresh();
  }

  /**
   *
   */
  refresh() : void {
    this.logService.getLogs().subscribe(logs => {
      this.data = logs;
    });
  }

  /**
   *
   */
  clear() : void {
    this.logService.clear().subscribe(
      () => this.refresh()
    );
  }

  /**
   *
   */
  test() : void {
    this.logService.test().subscribe(
    );
  }

}
