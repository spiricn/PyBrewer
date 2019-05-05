package com.brewer.ui.main

import android.graphics.Color
import android.media.Image
import android.util.Log
import androidx.recyclerview.widget.RecyclerView
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.TextView
import com.brewer.Logger
import com.brewer.R
import com.brewer.backend.Component
import com.brewer.backend.Message

class MessageListAdapter :
    RecyclerView.Adapter<MessageListAdapter.MyViewHolder>() {

    val mLog : Logger = Logger.create(MessageListAdapter::class.java);

    private var mMessages : List<Message>? = null;

    // Provide a reference to the views for each data item
    // Complex data items may need more than one view per item, and
    // you provide access to all the views for a data item in a view holder.
    // Each data item is just a string in this case that is shown in a TextView.
    class MyViewHolder(val layout: LinearLayout) : RecyclerView.ViewHolder(layout)


    // Create new views (invoked by the layout manager)
    override fun onCreateViewHolder(parent: ViewGroup,
                                    viewType: Int): MessageListAdapter.MyViewHolder {
        // create a new view
        val textView = LayoutInflater.from(parent.context)
            .inflate(R.layout.message_list_item, parent, false) as LinearLayout
        // set the view's size, margins, paddings and layout parameters
        return MyViewHolder(textView)
    }

    // Replace the contents of a view (invoked by the layout manager)
    override fun onBindViewHolder(holder: MyViewHolder, position: Int) {

        // Get component name text
        val messageBodyText = holder.layout.findViewById<TextView>(R.id.homeMessageBody);

        val message = mMessages?.get(position)

        if(message == null) {
            return
        }

        messageBodyText.text = message.message

        var drawableId : Int = -1

        when(message.type) {
            "WARNING" -> drawableId = R.drawable.icon_warning
            "INFO" -> drawableId = R.drawable.sensor
        }

        holder.layout.findViewById<ImageView>(R.id.homeMessageIcon).setImageResource(drawableId)
    }

    // Return the size of your dataset (invoked by the layout manager)
    override fun getItemCount() = mMessages?.size ?: 0;

    fun setItems(components : List<Message> ) {
        mMessages = components;
        notifyDataSetChanged();
    }
}