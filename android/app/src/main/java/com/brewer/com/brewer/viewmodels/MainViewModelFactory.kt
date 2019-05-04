package com.brewer.com.brewer.viewmodels

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import com.brewer.backend.HardwareApiService

class MainViewModelFactory(private val hardwareApiService: HardwareApiService ): ViewModelProvider.NewInstanceFactory() {
    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        return MainViewModel(hardwareApiService) as T
    }
}
