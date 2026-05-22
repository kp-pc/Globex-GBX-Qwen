package com.globex.wallet

import android.app.Application
import com.globex.wallet.api.GlobexApi
import com.globex.wallet.api.RetrofitClient
import com.globex.wallet.repository.GlobexRepository

/**
 * Application class for Globex Wallet
 * 
 * Initializes singleton instances of API client and repository
 */
class GlobexApplication : Application() {

    // Singleton API instance
    lateinit var api: GlobexApi
        private set

    // Singleton Repository instance
    lateinit var repository: GlobexRepository
        private set

    override fun onCreate() {
        super.onCreate()
        
        // Initialize Retrofit API client
        api = RetrofitClient.getInstance(this)
        
        // Initialize Repository with API and context
        repository = GlobexRepository(api, this)
    }

    /**
     * Update the API base URL (e.g., for switching networks)
     */
    fun updateApiBaseUrl(newBaseUrl: String) {
        RetrofitClient.updateBaseUrl(newBaseUrl, this)
        api = RetrofitClient.getInstance(this)
        repository = GlobexRepository(api, this)
    }

    companion object {
        const val TAG = "GlobexApplication"
    }
}
