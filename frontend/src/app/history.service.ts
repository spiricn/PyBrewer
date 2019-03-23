import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { BaseResponse, ResultResponse, kREST_ENDPOINT } from "./BaseResponse";
import { catchError, map, tap } from 'rxjs/operators';


const kHISTORY_REST_ENDPOINT = kREST_ENDPOINT + "/history";

@Injectable({
  providedIn: 'root'
})
export class HistoryService {
  constructor(private http : HttpClient) {
  }

  getSamples() : Observable<Samples> {
    return this.http.get<ResultResponse<Samples>>(kHISTORY_REST_ENDPOINT + "/getSamples")
    .pipe(
      map( (response : ResultResponse<Samples>) => response.result )
    );
  }
}

export class Samples {
  samples : Map<string, number[]>;
  time : Date[];
}