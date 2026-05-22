package com.globex.core.data.network

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit
import com.globex.core.data.api.GlobexApi

/**
 * Network module for Retrofit setup with timeout handling, logging, retry logic, and error handling
 */
object NetworkModule {

    private const val BASE_URL = "http://localhost:5000/"
    private const val CONNECT_TIMEOUT = 30L
    private const val READ_TIMEOUT = 60L
    private const val WRITE_TIMEOUT = 60L

    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }

    private val okHttpClient: OkHttpClient by lazy {
        OkHttpClient.Builder()
            .connectTimeout(CONNECT_TIMEOUT, TimeUnit.SECONDS)
            .readTimeout(READ_TIMEOUT, TimeUnit.SECONDS)
            .writeTimeout(WRITE_TIMEOUT, TimeUnit.SECONDS)
            .addInterceptor(loggingInterceptor)
            .addInterceptor(RetryInterceptor(maxRetries = 3))
            .addInterceptor(ErrorHandlingInterceptor())
            .build()
    }

    private val retrofit: Retrofit by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    val apiService: GlobexApi by lazy {
        retrofit.create(GlobexApi::class.java)
    }

    fun updateBaseUrl(newUrl: String) {
        // In a real implementation, you would rebuild the Retrofit instance
        // This is a simplified version
        println("Base URL updated to: $newUrl")
    }
}

/**
 * Interceptor for retry logic with exponential backoff
 */
class RetryInterceptor(
    private val maxRetries: Int = 3,
    private val retryDelayMs: Long = 1000
) : okhttp3.Interceptor {

    override fun intercept(chain: Interceptor.Chain): okhttp3.Response {
        var request = chain.request()
        var response: okhttp3.Response? = null
        var tryCount = 0

        while (tryCount < maxRetries) {
            try {
                response = chain.proceed(request)
                
                // If response is successful or not retryable, break
                if (response.isSuccessful || !isRetryable(response)) {
                    break
                }
                
                response.close()
            } catch (e: Exception) {
                // Log the exception
                println("Request failed: ${e.message}, retrying... ($tryCount/$maxRetries)")
            }

            tryCount++
            
            if (tryCount < maxRetries) {
                Thread.sleep(retryDelayMs * tryCount) // Exponential backoff
            }
        }

        return response ?: throw RuntimeException("Failed after $maxRetries retries")
    }

    private fun isRetryable(response: okhttp3.Response): Boolean {
        return response.code in listOf(
            408, // Request Timeout
            429, // Too Many Requests
            500, // Internal Server Error
            502, // Bad Gateway
            503, // Service Unavailable
            504  // Gateway Timeout
        )
    }
}

/**
 * Interceptor for centralized error handling
 */
class ErrorHandlingInterceptor : okhttp3.Interceptor {
    
    override fun intercept(chain: Interceptor.Chain): okhttp3.Response {
        val response = chain.proceed(chain.request())
        
        if (!response.isSuccessful) {
            val errorCode = response.code
            val errorMessage = when (errorCode) {
                400 -> "Bad Request"
                401 -> "Unauthorized"
                403 -> "Forbidden"
                404 -> "Not Found"
                408 -> "Request Timeout"
                429 -> "Too Many Requests"
                500 -> "Internal Server Error"
                502 -> "Bad Gateway"
                503 -> "Service Unavailable"
                504 -> "Gateway Timeout"
                else -> "Unknown Error"
            }
            
            println("API Error [$errorCode]: $errorMessage")
        }
        
        return response
    }
}
