package com.brewer.backend

/**
 * Base REST result class shared for all APIs
 */
data class BaseResult<ResultType>(
    /**
     * Actual result
     */
    val result : ResultType,

    /**
     * Success indication
     */
    val success : Boolean,

    /**
     * Execution time in seconds
     */
    val executionTime : Float
)