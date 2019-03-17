import { Component, OnInit } from '@angular/core';

import { HistoryService, Samples } from "../history.service";

@Component({
  selector: 'app-temperature',
  templateUrl: './temperature.component.html',
  styleUrls: ['./temperature.component.css']
})
export class TemperatureComponent implements OnInit {

  constructor(private historyService : HistoryService) { }

  ngOnInit() {
    this.historyService.getSamples().subscribe(
      samples => {
      samples.time.forEach(element => {
        console.log(element);
      });
      }
    )
  }

}
