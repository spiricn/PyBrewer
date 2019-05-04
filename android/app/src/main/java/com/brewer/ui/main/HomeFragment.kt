package com.brewer.ui.main

import androidx.lifecycle.ViewModelProviders
import android.os.Bundle
import androidx.fragment.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import com.brewer.R
import com.brewer.backend.BackendApi
import com.brewer.com.brewer.viewmodels.HomeViewModel
import com.brewer.com.brewer.viewmodels.HomeViewModelFactory
import com.brewer.com.brewer.viewmodels.SystemViewModel
import com.brewer.com.brewer.viewmodels.SystemViewModelFactory


class HomeFragment : Fragment() {

    companion object {
        fun newInstance() = HomeFragment()
    }

    private lateinit var mViewModel: HomeViewModel

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.home_fragment, container, false)
    }

    override fun onActivityCreated(savedInstanceState: Bundle?) {
        super.onActivityCreated(savedInstanceState)


        // Create MV factory
        val factory = HomeViewModelFactory(BackendApi.getInstance());

        // Create MV
        mViewModel = ViewModelProviders.of(this, factory).get(HomeViewModel::class.java)
    }

}
