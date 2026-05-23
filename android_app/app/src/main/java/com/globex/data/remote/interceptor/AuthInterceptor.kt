package com.globex.wallet.data.remote.interceptor

import okhttp3.Interceptor
import okhttp3.Response
import java.io.IOException

class AuthInterceptor : Interceptor {

    @Throws(IOException::class)
    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()
        
        // Add authentication token if available
        val authToken = getAuthToken()
        
        val requestBuilder = originalRequest.newBuilder()
            .header("Content-Type", "application/json")
            .header("Accept", "application/json")
        
        if (!authToken.isNullOrEmpty()) {
            requestBuilder.header("Authorization", "Bearer $authToken")
        }
        
        val request = requestBuilder.build()
        return chain.proceed(request)
    }
    
    private fun getAuthToken(): String? {
        // TODO: Retrieve token from secure storage
        // This should be implemented with EncryptedSharedPreferences
        return null
    }
}
