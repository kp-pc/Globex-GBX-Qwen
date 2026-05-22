package com.globex.wallet.api

import android.content.Context
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

/**
 * Retrofit Client Builder for Globex API
 * 
 * Provides a singleton instance of the Retrofit client with proper configuration
 */
object RetrofitClient {

    private var instance: GlobexApi? = null
    private var baseUrl: String = "http://10.0.2.2:5001/" // Default Android emulator localhost

    /**
     * Get or create the GlobexApi instance
     * @param context Android context
     * @param customBaseUrl Optional custom base URL (defaults to emulator localhost)
     * @return Configured GlobexApi instance
     */
    fun getInstance(context: Context, customBaseUrl: String? = null): GlobexApi {
        val url = customBaseUrl ?: baseUrl
        
        if (instance == null || getBaseUrl() != url) {
            instance = createRetrofitClient(url)
            setBaseUrl(url)
        }
        
        return instance!!
    }

    /**
     * Create a new Retrofit client with the specified base URL
     */
    private fun createRetrofitClient(baseUrl: String): GlobexApi {
        // Logging interceptor for debugging
        val loggingInterceptor = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }

        // HTTP client with timeouts
        val okHttpClient = OkHttpClient.Builder()
            .addInterceptor(loggingInterceptor)
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .retryOnConnectionFailure(true)
            .build()

        // Build Retrofit instance
        val retrofit = Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        // Create and return API service
        return retrofit.create(GlobexApi::class.java)
    }

    /**
     * Update the base URL (useful for switching between dev/prod environments)
     */
    fun updateBaseUrl(newBaseUrl: String, context: Context) {
        instance = createRetrofitClient(newBaseUrl)
        setBaseUrl(newBaseUrl)
    }

    /**
     * Get current base URL
     */
    fun getBaseUrl(): String {
        return baseUrl
    }

    /**
     * Set base URL (internal use)
     */
    private fun setBaseUrl(url: String) {
        baseUrl = url
    }

    /**
     * Create a custom OkHttpClient with specific configurations
     * Useful for advanced scenarios
     */
    fun createCustomClient(
        connectTimeout: Long = 30,
        readTimeout: Long = 30,
        writeTimeout: Long = 30,
        enableLogging: Boolean = true
    ): OkHttpClient {
        val builder = OkHttpClient.Builder()
            .connectTimeout(connectTimeout, TimeUnit.SECONDS)
            .readTimeout(readTimeout, TimeUnit.SECONDS)
            .writeTimeout(writeTimeout, TimeUnit.SECONDS)
            .retryOnConnectionFailure(true)

        if (enableLogging) {
            builder.addInterceptor(HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            })
        }

        return builder.build()
    }

    /**
     * Create a Retrofit instance with custom OkHttpClient
     */
    fun createWithCustomClient(
        baseUrl: String,
        client: OkHttpClient
    ): GlobexApi {
        val retrofit = Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        return retrofit.create(GlobexApi::class.java)
    }

    /**
     * Clear the cached instance (useful for testing or reconfiguration)
     */
    fun clearInstance() {
        instance = null
    }

    /**
     * Common base URLs for different environments
     */
    object Environments {
        const val EMULATOR_LOCALHOST = "http://10.0.2.2:5001/"
        const val PHYSICAL_DEVICE_LOCALHOST = "http://192.168.1.100:5001/" // Replace with your PC IP
        const val DEVELOPMENT_SERVER = "http://dev.globex.network:5001/"
        const val PRODUCTION_SERVER = "https://api.globex.network/"
        const val TESTNET_SERVER = "https://testnet.globex.network/"
    }
}
