package com.brewer.com.brewer.viewmodels

import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import com.brewer.Logger
import com.brewer.backend.Component
import com.brewer.backend.HardwareApiService
import io.reactivex.android.schedulers.AndroidSchedulers
import io.reactivex.schedulers.Schedulers

class MainViewModel  constructor(
    hardwareApiService : HardwareApiService) : ViewModel() {

    var mLog : Logger = Logger.create(MainViewModel::class.java);

    var hardwareApiService : HardwareApiService;
    private var mComponents : MutableLiveData<List<Component>> = MutableLiveData<List<Component>>();

    init {
        this.hardwareApiService = hardwareApiService;

        refresh();
    }

    /**
     * Get list of components
     */
    fun getComponents() : MutableLiveData<List<Component>> {
        return mComponents;
    }

    /**
     * Refresh data
     */
    fun refresh() {
        // Get a list of components
        hardwareApiService.getComponents()
            .observeOn(AndroidSchedulers.mainThread())
            .subscribeOn(Schedulers.io())
            .subscribe(
                {result -> onComponentsRetreived(result.result) },
                {error -> mLog.e("Error fetching components $error")}
            )
    }

    /**
     * Set new copmponents and update their values
     */
    private fun onComponentsRetreived(components : List<Component> ) {
        for(component in components) {
            component.value = -1.0f;
        }

        // Update live data
        mComponents.setValue(components);

        // Fetch values for every component
        // TODO This can probably be done in a single chain
        for(component in components) {
            updateComponentValue(component);
        }
    }

    /**
     * Update value for given component
     */
    private fun updateComponentValue(component : Component) {
        hardwareApiService.readValue(component.id)
            .subscribeOn(Schedulers.newThread())
            .observeOn(AndroidSchedulers.mainThread())
            .subscribe(
                {result ->
                    run {

                        // Set value for this component
                        component.value = result.result

                        // Update live data
                        mComponents.setValue(mComponents.value)
                    }
                },
                {error -> mLog.e("Error reading value: $error")}
            )
    }


}
