package com.brewer.ui.main

import androidx.recyclerview.widget.RecyclerView
import android.view.LayoutInflater
import android.view.ViewGroup
import android.widget.LinearLayout
import android.widget.TextView
import com.brewer.Logger
import com.brewer.R
import com.brewer.backend.LogEntry

class LogListAdapter :
    RecyclerView.Adapter<LogListAdapter.MyViewHolder>() {

    val mLog : Logger = Logger.create(LogListAdapter::class.java);

    private var mLogs : List<LogEntry>? = null;

    // Provide a reference to the views for each data item
    // Complex data items may need more than one view per item, and
    // you provide access to all the views for a data item in a view holder.
    // Each data item is just a string in this case that is shown in a TextView.
    class MyViewHolder(val layout: LinearLayout) : RecyclerView.ViewHolder(layout)


    // Create new views (invoked by the layout manager)
    override fun onCreateViewHolder(parent: ViewGroup,
                                    viewType: Int): LogListAdapter.MyViewHolder {
        // create a new view
        val textView = LayoutInflater.from(parent.context)
            .inflate(R.layout.log_list_item, parent, false) as LinearLayout
        // set the view's size, margins, paddings and layout parameters
        return MyViewHolder(textView)
    }

    // Replace the contents of a view (invoked by the layout manager)
    override fun onBindViewHolder(holder: MyViewHolder, position: Int) {

        // Get component name text
        val logBody = holder.layout.findViewById<TextView>(R.id.logBody);

        val logEntry = mLogs?.get(position)

        if(logEntry == null) {
            return
        }

        logBody.text = logEntry.message


    }

    // Return the size of your dataset (invoked by the layout manager)
    override fun getItemCount() = mLogs?.size ?: 0;

    fun setItems(components : List<LogEntry> ) {
        mLogs = components;
        notifyDataSetChanged();
    }
}