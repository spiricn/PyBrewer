package com.brewer.backend

data class LogEntry (
    val level : Int,

    val module : String,

    val message : String,

    val time : Int
)