import { Component, OnInit, ViewChild } from '@angular/core';

import { HistoryService, Samples } from "../history.service";

import { ZingChartDirective } from '../zing-chart.directive';
import { ZingChartModel } from '../zing-chart.model';

@Component({
  selector: 'app-temperature',
  templateUrl: './temperature.component.html',
  styleUrls: ['./temperature.component.css']
})
export class TemperatureComponent implements OnInit {

  chart : ZingChartModel = {
      id : 'chart-1',

      data : {
        type : 'line',
        series : [],
      },
      height : '100%',
      width : '100%'
    };

  isLoading : boolean = true;

  @ViewChild(ZingChartDirective) someElement : ZingChartDirective;

  constructor(private historyService : HistoryService) { }

  ngOnInit() {

    this.historyService.getSamples().subscribe(
      ( samples : Samples ) => {


          Object.keys(samples.samples).forEach((component: string) => {

            this.chart.data['series'].push({
              values : samples.samples[component]
            });
          });

          this.isLoading = false;

          this.someElement.render();


        });
    }
}
