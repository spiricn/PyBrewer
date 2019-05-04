package com.brewer.backend

import io.reactivex.Observable
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.adapter.rxjava2.RxJava2CallAdapterFactory
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.GET

data class Samples(
    val time : List<Float>,

    val samples : Map<String, List<Float>>
)

/**
 * Pybrewer /rest/log API implementation
 */
interface HistoryApiService {
    @GET("getSamples")
    fun getSamples() : Observable<BaseResult<Samples>>

    companion object {
        /**
         * Create log API service
         */
        fun create(endpoint : String, client: OkHttpClient) : HistoryApiService {
            val retrofit : Retrofit = Retrofit.Builder()
                .addCallAdapterFactory(
                    RxJava2CallAdapterFactory.create())
                .client(client)
                .addConverterFactory(
                    GsonConverterFactory.create())
                .baseUrl("$endpoint/history/")
                .build()

            return retrofit.create(HistoryApiService::class.java)
        }
    }
}