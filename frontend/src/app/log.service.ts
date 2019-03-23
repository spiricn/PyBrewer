import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { BaseResponse, ResultResponse, kREST_ENDPOINT } from "./BaseResponse";
import { catchError, map, tap } from 'rxjs/operators';


const kLOG_REST_ENDPOINT = kREST_ENDPOINT + "/log";

@Injectable({
  providedIn: 'root'
})
export class LogService {
  constructor(private http : HttpClient) {
  }

  /**
   * Get list of logs
   */
  getLogs() : Observable<LogMessage[]> {
    return this.http.get<ResultResponse<LogMessage[]>>(kLOG_REST_ENDPOINT + "/getLogs")
    .pipe(
      map((response : ResultResponse<LogMessage[]>) => response.result)
    );
  }

  /**
   *
   */
  clear() : Observable<boolean> {
    return this.http.get<BaseResponse>(kLOG_REST_ENDPOINT + "/clear")
    .pipe(
      map(response => response.success)
    );
  }

  /**
   *
   */
  test() : Observable<boolean> {
    return this.http.get<BaseResponse>(kLOG_REST_ENDPOINT + "/test")
    .pipe(
      map(response => response.success)
    );
  }
}

/**
 * Log message
 */
export class LogMessage {
  /**
   * Log module
   */
  module : string;

  /**
   * Log message
   */
  message : string;

  /**
   * Log timestamp
   */
  time : string;

  /**
   * Log level
   */
  level : number;
}