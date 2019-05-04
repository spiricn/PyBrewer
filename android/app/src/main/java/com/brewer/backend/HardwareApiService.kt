package com.brewer.backend

import io.reactivex.Observable
import retrofit2.Retrofit
import retrofit2.adapter.rxjava2.RxJava2CallAdapterFactory
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.GET
import okhttp3.OkHttpClient
import retrofit2.http.Query


/**
 * PyBrewer /rest/hardware implementation
 */
interface HardwareApiService {
    @GET("getComponents")
    fun getComponents() : Observable<BaseResult<List<Component>>>

    @GET("readValue")
    fun readValue(@Query("id") id : String) : Observable<BaseResult<Float>>

    @GET("toggleSwitch")
    fun toggleSwitch(@Query("id") id : String) : Observable<BaseResult<Any>>

    companion object {
        /**
         * Create hardware API service
         */
        fun create(endpoint : String, client: OkHttpClient) : HardwareApiService {
            val retrofit : Retrofit = Retrofit.Builder()
                .addCallAdapterFactory(
                    RxJava2CallAdapterFactory.create())
                .client(client)
                .addConverterFactory(
                    GsonConverterFactory.create())
                .baseUrl("$endpoint/hardware/")
                .build()

            return retrofit.create(HardwareApiService::class.java)
        }
    }
}
