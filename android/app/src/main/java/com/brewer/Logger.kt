package com.brewer


import android.util.Log

class Logger constructor(val tag: String, private val mOutputLevel: LogLevel) {
    enum class LogLevel private constructor(val value: Int) {
        VERBOSE(0), DEBUG(1), INFO(2), WARN(3), ERROR(4)
    }

    fun d(text: String) {
        if (mOutputLevel.value <= LogLevel.DEBUG.value) {
            Log.d(tag, text)
        }
    }

    fun e(text: String) {
        if (mOutputLevel.value <= LogLevel.ERROR.value) {
            Log.e(tag, text)
        }
    }

    fun i(text: String) {
        if (mOutputLevel.value <= LogLevel.INFO.value) {
            Log.i(tag, text)
        }
    }

    fun v(text: String) {
        if (mOutputLevel.value <= LogLevel.VERBOSE.value) {
            Log.v(tag, text)
        }
    }

    fun w(text: String) {
        if (mOutputLevel.value <= LogLevel.WARN.value) {
            Log.w(tag, text)
        }
    }

    companion object {

        private val kLOG_SUFFIX = "PyBrewer-"

        @JvmOverloads
        fun create(cls: Class<*>, outputLevel: LogLevel = LogLevel.VERBOSE): Logger {
            return Logger(kLOG_SUFFIX + cls.simpleName, outputLevel)
        }
    }
}