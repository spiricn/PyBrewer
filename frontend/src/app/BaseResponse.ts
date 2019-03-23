
export const kREST_ENDPOINT : string = "http://spiricn.ddns.net:8080/rest";

export class BaseResponse {
    /**
     * Error message in case the API call failed, may be null
     */
    errorMessage : string;

    /**
     * API call execution time in seconds
     */
    executionTime : number;

    /**
     * Success flag
     */
    success : boolean;
};


export class ResultResponse<T> extends BaseResponse {
  /**
   * Result object
   */
  result : T;
}