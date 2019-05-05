package com.brewer.com.brewer.viewmodels

import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel;
import com.brewer.backend.BackendApi
import com.brewer.backend.Samples
import io.reactivex.android.schedulers.AndroidSchedulers
import io.reactivex.schedulers.Schedulers

class HistoryViewModel(backendApi: BackendApi) : ViewModel() {
    private val mBackend = backendApi

    var samples : MutableLiveData<Samples> = MutableLiveData()

    init {
        mBackend.getHistoryApi().getSamples()
            .subscribeOn(Schedulers.io())
            .observeOn(AndroidSchedulers.mainThread())
            .subscribe{result -> samples.value = result.result}
    }
}
