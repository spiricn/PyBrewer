package com.brewer.ui.main

import androidx.lifecycle.ViewModelProviders
import android.os.Bundle
import androidx.fragment.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import com.brewer.R
import com.brewer.backend.BackendApi
import com.brewer.com.brewer.viewmodels.SystemViewModel
import com.brewer.com.brewer.viewmodels.SystemViewModelFactory
import com.google.android.material.snackbar.Snackbar
import io.reactivex.Observable
import io.reactivex.android.schedulers.AndroidSchedulers
import io.reactivex.schedulers.Schedulers


class SystemFragment : Fragment() {

    companion object {
        fun newInstance() = SystemFragment()
    }

    private lateinit var mViewModel: SystemViewModel

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.system_fragment, container, false)
    }

    override fun onActivityCreated(savedInstanceState: Bundle?) {
        super.onActivityCreated(savedInstanceState)

        // Create MV factory
        val factory = SystemViewModelFactory(BackendApi.getInstance().getSystemApi());

        // Create MV
        mViewModel = ViewModelProviders.of(this, factory).get(SystemViewModel::class.java)

        // Backup command
        addCommand("Backup", view!!.findViewById<Button>(R.id.systemButtonBackup)!!, mViewModel.backup());

        // Stop command
        addCommand("Stop", view!!.findViewById<Button>(R.id.systemButtonStop)!!, mViewModel.stop());

        // Restart command
        addCommand("Restart", view!!.findViewById<Button>(R.id.systemButtonRestart)!!, mViewModel.restart());

    }

    /**
     * Add a simple button command
     *
     * @param name Command name
     * @param button Button which triggers the commmand
     * @param func Function which runs the command
     */
    private fun addCommand(name : String, button : Button, func : Observable<Boolean>) {
        button.setOnClickListener(View.OnClickListener {
            // Notify the user
            Snackbar.make(view!!, "$name start ..", Snackbar.LENGTH_SHORT).show()

            // Disable button click
            button.isClickable = false

            // Run command
            func.subscribe { result ->
                // Notify user
                Snackbar.make(view!!, "$name complete", Snackbar.LENGTH_SHORT).show()

                // Enable button click
                button.isClickable = true
            }
        })
    }


}
