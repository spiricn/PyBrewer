package com.brewer.backend

import io.reactivex.Observable
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.adapter.rxjava2.RxJava2CallAdapterFactory
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.GET

/**
 * Pybrewer /rest/log API implementation
 */
interface LogApiService {
    @GET("clear")
    fun clear() : Observable<BaseResult<Any>>

    @GET("test")
    fun test() : Observable<BaseResult<Any>>

    @GET("getLogs")
    fun getLogs() : Observable<BaseResult<List<LogEntry>>>

    @GET("getMessages")
    fun getMessages() : Observable<BaseResult<List<Message>>>

    companion object {
        /**
         * Create log API service
         */
        fun create(endpoint : String, client: OkHttpClient) : LogApiService {
            val retrofit : Retrofit = Retrofit.Builder()
                .addCallAdapterFactory(
                    RxJava2CallAdapterFactory.create())
                .client(client)
                .addConverterFactory(
                    GsonConverterFactory.create())
                .baseUrl("$endpoint/log/")
                .build()

            return retrofit.create(LogApiService::class.java)
        }
    }
}