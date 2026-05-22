package com.globex.wallet.data.remote.interceptor

import okhttp3.Interceptor
import okhttp3.Response
import timber.log.Timber
import java.io.IOException

class LoggingInterceptor : Interceptor {

    @Throws(IOException::class)
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        
        val startTime = System.currentTimeMillis()
        Timber.d("→ ${request.method} ${request.url}")
        Timber.d("→ Headers: ${request.headers}")
        
        val response = chain.proceed(request)
        
        val endTime = System.currentTimeMillis()
        val duration = endTime - startTime
        
        Timber.d("← ${response.code} ${request.url} (${duration}ms)")
        Timber.d("← Headers: ${response.headers}")
        
        return response
    }
}
