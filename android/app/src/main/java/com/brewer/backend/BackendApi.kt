package com.brewer.backend

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor

/**
 * PyBrewer REST API
 */
class BackendApi {

    /**
     * HTTP client instance shared between ali APIs
     */
    private var mHttpClient : OkHttpClient

    /**
     * Hardware API service
     */
    private var mHardwareApiService : HardwareApiService

    /**
     * System API service
     */
    private var mSystemApiService : SystemApiService

    /**
     * Log API service
     */
    private var mLogApiService : LogApiService

    /**
     * History API service
     */
    private var mHistoryApiService : HistoryApiService

    constructor(mEndpoint : String)  {
        // Initialize logging interceptor
        val interceptor = HttpLoggingInterceptor()
        interceptor.level = HttpLoggingInterceptor.Level.BODY

        // Create HTTP client
        mHttpClient = OkHttpClient.Builder().addInterceptor(interceptor).build()

        // Create hardware API
        mHardwareApiService = HardwareApiService.create(mEndpoint, mHttpClient)

        // Create system API
        mSystemApiService = SystemApiService.create(mEndpoint, mHttpClient);

        // Create log API
        mLogApiService = LogApiService.create(mEndpoint, mHttpClient);

        // Create history API
        mHistoryApiService = HistoryApiService.create(mEndpoint, mHttpClient)
    }

    /**
     * Hardware API service
     */
    fun getHardwareApi() = mHardwareApiService

    /**
     * System API service
     */
    fun getSystemApi() = mSystemApiService;

    companion object {
        @Volatile private var instance : BackendApi? = null;

        /**
         * Create backend API
         */
        fun getInstance() =
            // TODO Make endpoitn configurable
            instance ?: synchronized(this) {
                instance ?: BackendApi("http://spiricn.ddns.net:8080/rest").also { instance = it }
            }
    }
}