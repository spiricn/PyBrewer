import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { HardwareComponent } from './hardware/hardware.component';
import {
  MatListModule,
  MatCheckboxModule,
  MatTabsModule,
  MatToolbarModule,
  MatButtonModule,
  MatChipsModule,
  MatSlideToggleModule,
  MatTableModule,
  MatProgressSpinnerModule,
} from '@angular/material';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { NavigationComponent } from './navigation/navigation.component';
import { LoggingComponent } from './logging/logging.component';
import { TemperatureComponent } from './temperature/temperature.component';

import { ZingChartDirective } from './zing-chart.directive';

@NgModule({
  declarations: [
    AppComponent,
    HardwareComponent,
    NavigationComponent,
    LoggingComponent,
    TemperatureComponent,
    ZingChartDirective
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,

    HttpClientModule,
    MatCheckboxModule,
    MatListModule,
    MatTabsModule,
    BrowserAnimationsModule,
    MatToolbarModule,
    MatButtonModule,
    MatChipsModule,
    MatSlideToggleModule,
    MatTableModule,
    MatProgressSpinnerModule,
  ],
  exports: [MatListModule, MatCheckboxModule, MatTabsModule, MatToolbarModule, MatButtonModule],

  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
