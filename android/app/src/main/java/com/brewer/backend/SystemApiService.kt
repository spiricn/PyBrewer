package com.brewer.backend

import io.reactivex.Observable
import retrofit2.Retrofit
import retrofit2.adapter.rxjava2.RxJava2CallAdapterFactory
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.GET
import okhttp3.OkHttpClient


/**
 * PyBrewer /rest/system implementation
 */
interface SystemApiService {
    @GET("stop")
    fun stop() : Observable<BaseResult<Any>>

    @GET("restart")
    fun restart() : Observable<BaseResult<Any>>

    @GET("backup")
    fun backup() : Observable<BaseResult<Any>>

    companion object {
        /**
         * Create hardware API service
         */
        fun create(endpoint : String, client: OkHttpClient) : SystemApiService {
            val retrofit : Retrofit = Retrofit.Builder()
                .addCallAdapterFactory(
                    RxJava2CallAdapterFactory.create())
                .client(client)
                .addConverterFactory(
                    GsonConverterFactory.create())
                .baseUrl("$endpoint/system/")
                .build()

            return retrofit.create(SystemApiService::class.java)
        }
    }
}
