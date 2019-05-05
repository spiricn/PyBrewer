package com.brewer.ui.main

import android.graphics.Color
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

class ComponentListAdapter :
    RecyclerView.Adapter<ComponentListAdapter.MyViewHolder>() {

    val mLog : Logger = Logger.create(ComponentListAdapter::class.java);

    private var mComponents : List<Component>? = null;

    // Provide a reference to the views for each data item
    // Complex data items may need more than one view per item, and
    // you provide access to all the views for a data item in a view holder.
    // Each data item is just a string in this case that is shown in a TextView.
    class MyViewHolder(val layout: LinearLayout) : RecyclerView.ViewHolder(layout)


    // Create new views (invoked by the layout manager)
    override fun onCreateViewHolder(parent: ViewGroup,
                                    viewType: Int): ComponentListAdapter.MyViewHolder {
        // create a new view
        val textView = LayoutInflater.from(parent.context)
            .inflate(R.layout.component_list_item, parent, false) as LinearLayout
        // set the view's size, margins, paddings and layout parameters
        return MyViewHolder(textView)
    }

    // Replace the contents of a view (invoked by the layout manager)
    override fun onBindViewHolder(holder: MyViewHolder, position: Int) {

        // Get component name text
        val componentNameText = holder.layout.findViewById<TextView>(R.id.componentName);

        // Get component value text
        val componentValueText = holder.layout.findViewById<TextView>(R.id.componentValue);

        val loadingSpinner = holder.layout.findViewById<ProgressBar>(R.id.progressBar);

        // Get component
        var component = mComponents?.get(position);

        if(component == null){
            return;
        }

        var drawableId : Int = -1;


        when(component.componentType) {
            "SWITCH" -> drawableId = R.drawable.button
            "SENSOR" -> drawableId = R.drawable.sensor
        }
        holder.layout.findViewById<ImageView>(R.id.componentIcon).setImageResource(drawableId)

        // Set name
        componentNameText.text = component?.name ?: "???";

        // Set color
        var color : Int = Color.BLACK;

        try {
            color = Color.parseColor(component?.color);
        } catch(e : IllegalArgumentException) {
            mLog.e("Invalid color: " + component?.color);
        }

        componentNameText.setTextColor(color);

        val valueSet : Boolean = component.value >= 0.0f;

        componentValueText.visibility = if(valueSet) View.VISIBLE else View.GONE
        loadingSpinner.visibility = if(valueSet) View.GONE else View.VISIBLE

        componentValueText.text = String.format("%.2f", component?.value);
    }

    // Return the size of your dataset (invoked by the layout manager)
    override fun getItemCount() = mComponents?.size ?: 0;

    fun setItems(components : List<Component> ) {
        mComponents = components;
        notifyDataSetChanged();
    }
}