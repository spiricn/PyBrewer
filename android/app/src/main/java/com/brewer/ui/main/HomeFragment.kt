package com.brewer.ui.main

import androidx.lifecycle.ViewModelProviders
import android.os.Bundle
import androidx.fragment.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ProgressBar
import androidx.lifecycle.Observer
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.brewer.Logger
import com.brewer.R
import com.brewer.backend.BackendApi
import com.brewer.com.brewer.viewmodels.HomeViewModel
import com.brewer.com.brewer.viewmodels.HomeViewModelFactory
import com.brewer.com.brewer.viewmodels.SystemViewModel
import com.brewer.com.brewer.viewmodels.SystemViewModelFactory


class HomeFragment : Fragment() {

    var mLog : Logger = Logger.create(HomeFragment::class.java);

    companion object {
        fun newInstance() = HomeFragment()
    }

    private lateinit var mViewModel: HomeViewModel

    /**
     * Recycler view used to display components
     */
    private lateinit var mComponentListRecyclerView: RecyclerView;

    /**
     * Main layout
     */
    private lateinit var mViewManager: RecyclerView.LayoutManager;

    private lateinit var mMessageAdapter : MessageListAdapter

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.home_fragment, container, false)
    }

    override fun onActivityCreated(savedInstanceState: Bundle?) {
        super.onActivityCreated(savedInstanceState)

        mViewManager = LinearLayoutManager(this.context);
        mComponentListRecyclerView = view?.findViewById(R.id.homeMessageList)!!;

        // Create component list adapter
        mMessageAdapter = MessageListAdapter();

        // Initialize recycler view
        mComponentListRecyclerView.apply {
            layoutManager = mViewManager;
            adapter = mMessageAdapter;
        }
        // Create MV factory
        val factory = HomeViewModelFactory(BackendApi.getInstance());

        // Create MV
        mViewModel = ViewModelProviders.of(this, factory).get(HomeViewModel::class.java)

        mViewModel.messages.observe(this, Observer {
            messages ->
            mMessageAdapter.setItems(messages)


            view?.findViewById<ProgressBar>(R.id.homeMessagesSpinner)!!.visibility = View.GONE
            view?.findViewById<RecyclerView>(R.id.homeMessageList)!!.visibility = View.VISIBLE

        })


    }

}
