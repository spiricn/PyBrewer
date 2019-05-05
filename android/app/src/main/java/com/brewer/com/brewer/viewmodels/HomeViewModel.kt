package com.brewer.com.brewer.viewmodels

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel;
import com.brewer.Logger
import com.brewer.backend.BackendApi
import com.brewer.backend.Message
import io.reactivex.Observable
import io.reactivex.Scheduler
import io.reactivex.android.schedulers.AndroidSchedulers
import io.reactivex.schedulers.Schedulers

class HomeViewModel(backendApi: BackendApi) : ViewModel() {

    val mLog : Logger = Logger.create(HomeViewModel::class.java)

    val mBackendApi = backendApi

    val messages : MutableLiveData<List<Message>> = MutableLiveData<List<Message>>()


    /**
     *
     */
    init {
        refresh()
    }

    /**
     *
     */
    fun refresh () {
        mBackendApi.getLogApi().getMessages()
            .subscribeOn(Schedulers.io())
            .observeOn(AndroidSchedulers.mainThread())
            .subscribe (
                {result -> messages.value = result.result},
                {error -> mLog.e("Error refreshing")}
        )
    }
}
