package com.brewer.com.brewer.viewmodels

import androidx.lifecycle.ViewModel;
import com.brewer.backend.SystemApiService
import io.reactivex.Observable
import io.reactivex.Single
import io.reactivex.android.schedulers.AndroidSchedulers
import io.reactivex.schedulers.Schedulers

class SystemViewModel (systemApiService: SystemApiService) : ViewModel() {
    var mSystemApiService = systemApiService;

    /**
     * Backup server
     */
    fun backup() : Observable<Boolean> {
        return mSystemApiService.backup()
            .subscribeOn(Schedulers.io())
            .observeOn(AndroidSchedulers.mainThread())
            .map { result -> result.success }
    }

    /**
     * Stop server
     */
    fun stop() : Observable<Boolean> {
        return mSystemApiService.stop()
            .subscribeOn(Schedulers.io())
            .observeOn(AndroidSchedulers.mainThread())
            .map { result -> result.success }
    }

    /**
     * Restart server
     */
    fun restart() : Observable<Boolean> {
        return mSystemApiService.restart()
            .subscribeOn(Schedulers.io())
            .observeOn(AndroidSchedulers.mainThread())
            .map { result -> result.success }
    }
}
