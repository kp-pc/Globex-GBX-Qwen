package com.globex.wallet.data.remote.api

import com.globex.wallet.domain.model.Transaction
import com.globex.wallet.domain.model.Wallet
import retrofit2.Response
import retrofit2.http.*

interface GlobexApiService {
    
    // Wallet endpoints
    @GET("api/v1/wallets/{address}")
    suspend fun getWallet(@Path("address") address: String): Response<Wallet>
    
    @GET("api/v1/wallets/{address}/balance")
    suspend fun getWalletBalance(@Path("address") address: String): Response<Map<String, Any>>
    
    @GET("api/v1/wallets/{address}/transactions")
    suspend fun getWalletTransactions(
        @Path("address") address: String,
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 50
    ): Response<List<Transaction>>
    
    // Transaction endpoints
    @POST("api/v1/transactions/send")
    suspend fun sendTransaction(@Body transaction: Map<String, Any>): Response<Map<String, Any>>
    
    @GET("api/v1/transactions/{txHash}")
    suspend fun getTransaction(@Path("txHash") txHash: String): Response<Transaction>
    
    // Mining endpoints
    @GET("api/v1/mining/stats")
    suspend fun getMiningStats(): Response<Map<String, Any>>
    
    @POST("api/v1/mining/start")
    suspend fun startMining(@Body params: Map<String, Any>): Response<Map<String, Any>>
    
    @POST("api/v1/mining/stop")
    suspend fun stopMining(@Body params: Map<String, Any>): Response<Map<String, Any>>
    
    // Staking endpoints
    @POST("api/v1/staking/stake")
    suspend fun stake(@Body params: Map<String, Any>): Response<Map<String, Any>>
    
    @POST("api/v1/staking/unstake")
    suspend fun unstake(@Body params: Map<String, Any>): Response<Map<String, Any>>
    
    @GET("api/v1/staking/rewards/{address}")
    suspend fun getStakingRewards(@Path("address") address: String): Response<Map<String, Any>>
    
    // Node endpoints
    @GET("api/v1/nodes")
    suspend fun getNodes(): Response<List<Map<String, Any>>>
    
    @GET("api/v1/nodes/status")
    suspend fun getNodeStatus(): Response<Map<String, Any>>
    
    // Explorer endpoints
    @GET("api/v1/blocks/latest")
    suspend fun getLatestBlock(): Response<Map<String, Any>>
    
    @GET("api/v1/blocks/{height}")
    suspend fun getBlockByHeight(@Path("height") height: Long): Response<Map<String, Any>>
    
    @GET("api/v1/supply")
    suspend fun getTotalSupply(): Response<Map<String, Any>>
}
