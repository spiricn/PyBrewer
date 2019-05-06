package com.brewer.ui.main

import androidx.lifecycle.Observer
import androidx.lifecycle.ViewModelProviders
import android.os.Bundle
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ProgressBar
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout
import com.brewer.Logger
import com.brewer.R
import com.brewer.backend.BackendApi
import com.brewer.com.brewer.viewmodels.MainViewModel
import com.brewer.com.brewer.viewmodels.MainViewModelFactory

class ComponentListFragment : Fragment() {
    /**
     * Logger object
     */
    var mLog : Logger = Logger.create(ComponentListFragment::class.java);

    /**
     * Recycler view used to display components
     */
    private lateinit var mComponentListRecyclerView: RecyclerView;

    /**
     * Component recycler view adapter
     */
    private lateinit var mComponentListAdapter: ComponentListAdapter;

    /**
     * Main layout
     */
    private lateinit var mViewManager: RecyclerView.LayoutManager;


    private lateinit var mLoadingSpinner: ProgressBar;

    companion object {
        fun newInstance() = ComponentListFragment()
    }

    private lateinit var mViewModel: MainViewModel

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        return inflater.inflate(R.layout.component_list_fragment, container, false)
    }

    override fun onActivityCreated(savedInstanceState: Bundle?) {
        super.onActivityCreated(savedInstanceState)

        view!!.findViewById<SwipeRefreshLayout>(R.id.componentSwipeRefresh).setOnRefreshListener {
            mViewModel.refresh()
        }

        // Find views
        mViewManager = LinearLayoutManager(this.context);
        mComponentListRecyclerView = view?.findViewById(R.id.componentList)!!;


        mLoadingSpinner= view?.findViewById(R.id.componentsLoadingProgress)!!;


        // Create component list adapter
        mComponentListAdapter = ComponentListAdapter();

        // Initialize recycler view
        mComponentListRecyclerView.apply {
            layoutManager = mViewManager;
            adapter = mComponentListAdapter;
        }

        // Create MV factory
        val factory = MainViewModelFactory(BackendApi.getInstance().getHardwareApi());

        // Create MV
        mViewModel = ViewModelProviders.of(this, factory).get(MainViewModel::class.java)

        // Start listening for component updates
        mViewModel.getComponents().observe(this, Observer {
                result ->
            result?.let {
                mComponentListAdapter.setItems(it)
                mLoadingSpinner.visibility = View.GONE;
                mComponentListRecyclerView.visibility = View.VISIBLE;

                view!!.findViewById<SwipeRefreshLayout>(R.id.componentSwipeRefresh).isRefreshing = false
            }
        });
    }
}
