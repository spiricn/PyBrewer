import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { HardwareComponent } from "./hardware/hardware.component"
import { LoggingComponent } from "./logging/logging.component"
import { TemperatureComponent } from "./temperature/temperature.component"

const routes: Routes = [
  //{ path: '', redirectTo: '/hardware', pathMatch: 'full' },
  { path: 'hardware', component: HardwareComponent },
  { path: 'logging', component: LoggingComponent },
  { path: 'temperature', component: TemperatureComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
