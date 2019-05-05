package com.brewer.ui.main

import androidx.lifecycle.ViewModelProviders
import android.os.Bundle
import androidx.fragment.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.ProgressBar
import androidx.lifecycle.Observer
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView

import com.brewer.R
import com.brewer.backend.BackendApi
import com.brewer.com.brewer.viewmodels.HistoryViewModel
import com.brewer.com.brewer.viewmodels.HistoryViewModelFactory
import com.brewer.com.brewer.viewmodels.LogViewModel
import com.brewer.com.brewer.viewmodels.LogViewModelFactory
import com.brewer.ui.main.LogListAdapter as LogListAdapter1

class LogFragment : Fragment() {

    companion object {
        fun newInstance() = LogFragment()
    }


    /**
     * Recycler view used to display components
     */
    private lateinit var mComponentListRecyclerView: RecyclerView

    /**
     * Component recycler view adapter
     */
    private lateinit var mLogListAdapter: com.brewer.ui.main.LogListAdapter

    /**
     * Main layout
     */
    private lateinit var mViewManager: RecyclerView.LayoutManager

    private lateinit var mViewModel: LogViewModel

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.log_fragment, container, false)
    }

    override fun onActivityCreated(savedInstanceState: Bundle?) {
        super.onActivityCreated(savedInstanceState)

        // Find views
        mViewManager = LinearLayoutManager(this.context);
        mComponentListRecyclerView = view?.findViewById(R.id.logList)!!;

        // Create MV factory
        val factory = LogViewModelFactory(BackendApi.getInstance())


        // Create component list adapter
        mLogListAdapter = LogListAdapter1();

        // Initialize recycler view
        mComponentListRecyclerView.apply {
            layoutManager = mViewManager;
            adapter = mLogListAdapter;
        }



        view!!.findViewById<Button>(R.id.logButtonClear).setOnClickListener(
            View.OnClickListener {
                mViewModel.clearLogs()
            }
        )

        // Create MV
        mViewModel = ViewModelProviders.of(this, factory).get(LogViewModel::class.java)

        mViewModel.logs.observe(this, Observer {
            result ->

            mLogListAdapter.setItems(result)

            view!!.findViewById<ProgressBar>(R.id.logLoadingProgress).visibility = View.GONE
            view!!.findViewById<RecyclerView>(R.id.logList).visibility = View.VISIBLE
        })
    }

}
