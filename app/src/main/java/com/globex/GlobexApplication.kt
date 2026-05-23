package com.globex

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

/**
 * Main Application class for Globex
 */
@HiltAndroidApp
class GlobexApplication : Application() {

    override fun onCreate() {
        super.onCreate()
        // Initialize any global components here
    }
}
