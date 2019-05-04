package com.brewer.com.brewer.viewmodels

import com.brewer.backend.SystemApiService

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider

class SystemViewModelFactory(private val systemApiService: SystemApiService): ViewModelProvider.NewInstanceFactory() {
    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        return SystemViewModel(systemApiService) as T
    }
}
