package com.brewer.com.brewer.viewmodels

import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.Observer
import androidx.lifecycle.ViewModel;
import com.brewer.backend.BackendApi
import com.brewer.backend.LogEntry
import io.reactivex.android.schedulers.AndroidSchedulers
import io.reactivex.schedulers.Schedulers

class LogViewModel(backendApi: BackendApi) : ViewModel() {

    var logs : MutableLiveData<List<LogEntry>> = MutableLiveData()


    private val mBackendApi = backendApi

    init {
        refresh()
    }


    fun refresh() {
        mBackendApi.getLogApi().getLogs()
            .subscribeOn(Schedulers.io())
            .observeOn(AndroidSchedulers.mainThread())
            .subscribe{result -> logs.value = result.result }
    }

    fun clearLogs() {
        mBackendApi.getLogApi().clear()
            .subscribeOn(Schedulers.io())
            .observeOn(AndroidSchedulers.mainThread())
            .doOnNext {
                refresh()
            }
            .subscribe()
    }
}
