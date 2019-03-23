import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { BaseResponse, ResultResponse, kREST_ENDPOINT } from "./BaseResponse";
import { Component } from '@angular/compiler/src/core';
import { catchError, map, tap } from 'rxjs/operators';

const kHW_REST_ENDPOINT = kREST_ENDPOINT + "/hardware";

@Injectable({
  providedIn: 'root'
})
export class HardwareService {
  constructor(private http : HttpClient) {
  }

  /**
   * Get a list of components (i.e. switches/sensors)
   */
  getComponents() : Observable<ComponentEntry[]> {
    return this.http.get<ResultResponse<ComponentEntry[]>>(kHW_REST_ENDPOINT + "/getComponents")
    .pipe(map(response => response.success ? response.result : []));

  }

  /**
   * Toggle switch
   *
   * @param id Switch ID
   */
  toggleSwitch(id : string) : Observable<boolean> {
    return this.http.get<BaseResponse>(kHW_REST_ENDPOINT + "/toggleSwitch?id=" + id)
    .pipe(
      map(result => result.success)
      );

  }

  /**
   * Read component value
   *
   * @param id Component ID
   */
  readValue(id : string) : Observable<number> {
    return this.http.get<ResultResponse<number>>(kHW_REST_ENDPOINT + "/readValue?id=" + id)
    .pipe(
      map(response => response.success ? response.result : null)
    );
  }
};

export class ComponentEntry {
  color : string;
  id : string;
  graph : boolean;
  name : string;
  componentType : string;
  value : number;
};
