package com.brewer.ui.main

import android.graphics.Color
import androidx.lifecycle.ViewModelProviders
import android.os.Bundle
import androidx.fragment.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ProgressBar
import androidx.lifecycle.Observer
import com.brewer.Logger
import com.brewer.R
import com.brewer.backend.BackendApi
import com.brewer.backend.Samples
import com.brewer.com.brewer.viewmodels.HistoryViewModel
import com.brewer.com.brewer.viewmodels.HistoryViewModelFactory
import com.brewer.com.brewer.viewmodels.MainViewModel
import com.brewer.com.brewer.viewmodels.MainViewModelFactory
import com.github.mikephil.charting.charts.LineChart
import com.github.mikephil.charting.data.Entry
import com.github.mikephil.charting.data.LineData
import com.github.mikephil.charting.data.LineDataSet
import com.github.mikephil.charting.interfaces.datasets.ILineDataSet
import java.text.SimpleDateFormat
import java.util.ArrayList


class HistoryFragment : Fragment() {
    val mLog : Logger = Logger.create(HistoryFragment::class.java)

    companion object {
        fun newInstance() = HistoryFragment()
    }

    private lateinit var mViewModel: HistoryViewModel

    private var mChart: LineChart? = null

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.history_fragment, container, false)
    }

    override fun onActivityCreated(savedInstanceState: Bundle?) {
        super.onActivityCreated(savedInstanceState)

        // Create MV factory
        val factory = HistoryViewModelFactory(BackendApi.getInstance())

        // Create MV
        mViewModel = ViewModelProviders.of(this, factory).get(HistoryViewModel::class.java)

        mChart = view!!.findViewById<LineChart>(R.id.chart)

        // enable touch gestures
        mChart!!.setTouchEnabled(true)

        // enable scaling and dragging
        mChart!!.setDragEnabled(true)
        mChart!!.setScaleEnabled(true)
        mChart!!.setPinchZoom(false)


        mViewModel.samples.observe(this, Observer {samples ->
            onSamplesReceived(samples)
        })
    }

    private fun onSamplesReceived(samples : Samples) {
        val dataSets = ArrayList<ILineDataSet>()


        val dateFormat = SimpleDateFormat("YYYY-MM-DD'T'HH:mm:ss")


        val timestamps = ArrayList<Long>()

        for(timestamp in samples.time) {
            timestamps.add(dateFormat.parse(timestamp).time)
        }

        for (componentEntry in samples.samples.entries) {
            val values = ArrayList<Entry>()

            var idx = 0

            for(value in componentEntry.value) {
                mLog.d("" + timestamps[idx].toFloat() + " "   + value)

                values.add(Entry(timestamps[idx].toFloat(), value))


                idx++
            }

            val d = LineDataSet(values, componentEntry.key)

            // TODO
            d.color = Color.RED

            dataSets.add(d)
        }

        val data = LineData(dataSets)
        mChart!!.setData(data)
        mChart!!.invalidate()


        view!!.findViewById<ProgressBar>(R.id.historyLoadingSpinner).visibility = View.GONE
        mChart!!.visibility = View.VISIBLE
    }

}
