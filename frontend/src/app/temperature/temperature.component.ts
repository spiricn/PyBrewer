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

  chart : Object = {
      id : 'chart-1',

      data : {
        "gui": {
           "contextMenu": {
              "position": "right",
              "docked": true,
              "alpha": 0.9,
              "item": {
                 "textAlpha": 1
              },
              "button": {
                 "visible": true
              }
           }
        },
        "graphset": [
           {
              "type": "line",
              "backgroundColor": "#333",
              "borderColor": "#cccccc",
              "borderWidth": 1,
              "borderRadius": 2,
              "plot": {
                 "aspect": "spline",
                 "marker": {
                    "visible": false
                 }
              },
              "plotarea": {
                 "margin": "dynamic"
              },
              "utc": true,
              "timezone": 1,
              "legend": {
                 "draggable": true,
                 "backgroundColor": "transparent",
                 "marker": {
                    "visible": false
                 },
                 "item": {
                    "margin": "5 17 2 0",
                    "padding": "3 3 3 3",
                    "fontColor": "#fff",
                    "cursor": "hand"
                 },
                 "verticalAlign": "middle",
                 "borderWidth": 0
              },
              "scaleX": {
                 "zooming": true,
                 "transform": {
                    "type": "date",
                    "all": "%m/%d/%y  %h:%i %A"
                 },
                 "values": []
              },
              "preview": {
                 "adjustLayout": true,
                 "live": true
              },
              "scaleY": {
                 "step": 25,
                 "label": {
                    "text": "Sensor"
                 },
                 "guide": {
                    "lineStyle": "solid"
                 },
                 "zooming": true
              },
              "crosshairX": {
                 "lineColor": "#555",
                 "plotLabel": {
                    "backgroundColor": "#fff",
                    "multiple": true,
                    "borderWidth": 2,
                    "borderRadius": 2
                 },
                 "marker": {
                    "size": 5,
                    "borderWidth": 1,
                    "borderColor": "#fff"
                 }
              },
              "tooltip": {
                 "visible": false
              },
              "series": []
           }
        ]
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

            this.chart['data']['graphset'][0]['series'].push({
              values : samples.samples[component],
              'text' : component
            });
          });

          this.isLoading = false;

          this.someElement.render();


        });
    }
}
