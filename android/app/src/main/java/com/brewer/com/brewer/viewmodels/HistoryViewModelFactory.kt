package com.brewer.com.brewer.viewmodels

import com.brewer.backend.SystemApiService

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import com.brewer.backend.BackendApi

class HistoryViewModelFactory(private val backendApi: BackendApi): ViewModelProvider.NewInstanceFactory() {
    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        return HistoryViewModel(backendApi) as T
    }
}
