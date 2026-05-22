package com.globex.core.data.api

import com.globex.core.data.dto.*
import retrofit2.Response
import retrofit2.http.*

/**
 * Retrofit API interface for Globex blockchain operations
 */
interface GlobexApi {

    /**
     * Get the full blockchain
     * GET /chain
     */
    @GET("chain")
    suspend fun getChain(): Response<ChainResponse>

    /**
     * Mine a new block
     * POST /mine
     */
    @POST("mine")
    suspend fun mineBlock(@Body request: MineRequest): Response<MineResponse>

    /**
     * Create a new transaction
     * POST /transactions/new
     */
    @POST("transactions/new")
    suspend fun createTransaction(@Body request: TransactionRequest): Response<TransactionResponse>

    /**
     * Register a new node
     * POST /nodes/register
     */
    @POST("nodes/register")
    suspend fun registerNode(@Body request: NodeRegisterRequest): Response<NodeRegisterResponse>

    /**
     * Resolve consensus - get the longest chain
     * GET /nodes/resolve
     */
    @GET("nodes/resolve")
    suspend fun resolveChain(): Response<NodesResolveResponse>

    /**
     * Get balance for an address
     * GET /addresses/{address}/balance
     */
    @GET("addresses/{address}/balance")
    suspend fun getBalance(@Path("address") address: String): Response<ApiResponse<BalanceDto>>

    /**
     * Get transactions for an address
     * GET /addresses/{address}/transactions
     */
    @GET("addresses/{address}/transactions")
    suspend fun getTransactions(
        @Path("address") address: String,
        @Query("page") page: Int = 0,
        @Query("limit") limit: Int = 20
    ): Response<ApiResponse<List<TransactionDto>>>

    /**
     * Get block by height
     * GET /blocks/{height}
     */
    @GET("blocks/{height}")
    suspend fun getBlockByHeight(@Path("height") height: Long): Response<ApiResponse<BlockDto>>

    /**
     * Get block by hash
     * GET /blocks/hash/{hash}
     */
    @GET("blocks/hash/{hash}")
    suspend fun getBlockByHash(@Path("hash") hash: String): Response<ApiResponse<BlockDto>>

    /**
     * Get transaction by ID
     * GET /transactions/{id}
     */
    @GET("transactions/{id}")
    suspend fun getTransaction(@Path("id") id: String): Response<ApiResponse<TransactionDto>>

    /**
     * Get network stats
     * GET /stats
     */
    @GET("stats")
    suspend fun getNetworkStats(): Response<ApiResponse<NetworkStatsDto>>

    /**
     * Get connected nodes
     * GET /nodes
     */
    @GET("nodes")
    suspend fun getNodes(): Response<ApiResponse<List<NodeDto>>>

    /**
     * Get staking info for an address
     * GET /staking/{address}
     */
    @GET("staking/{address}")
    suspend fun getStakingInfo(@Path("address") address: String): Response<ApiResponse<StakingInfoDto>>

    /**
     * Get validator info
     * GET /validators/{address}
     */
    @GET("validators/{address}")
    suspend fun getValidatorInfo(@Path("address") address: String): Response<ApiResponse<ValidatorDto>>

    /**
     * Get fund info
     * GET /fund
     */
    @GET("fund")
    suspend fun getFundInfo(): Response<ApiResponse<FundDto>>
}

/**
 * Additional DTOs for extended API endpoints
 */
@kotlinx.serialization.Serializable
data class BalanceDto(
    @kotlinx.serialization.SerialName("address") val address: String,
    @kotlinx.serialization.SerialName("balance") val balance: Long,
    @kotlinx.serialization.SerialName("pendingBalance") val pendingBalance: Long = 0,
    @kotlinx.serialization.SerialName("nonce") val nonce: Int = 0
)

@kotlinx.serialization.Serializable
data class NetworkStatsDto(
    @kotlinx.serialization.SerialName("blockHeight") val blockHeight: Long,
    @kotlinx.serialization.SerialName("difficulty") val difficulty: Long,
    @kotlinx.serialization.SerialName("peerCount") val peerCount: Int,
    @kotlinx.serialization.SerialName("hashRate") val hashRate: Double,
    @kotlinx.serialization.SerialName("totalSupply") val totalSupply: Long,
    @kotlinx.serialization.SerialName("circulatingSupply") val circulatingSupply: Long
)

@kotlinx.serialization.Serializable
data class StakingInfoDto(
    @kotlinx.serialization.SerialName("address") val address: String,
    @kotlinx.serialization.SerialName("stakedAmount") val stakedAmount: Long,
    @kotlinx.serialization.SerialName("rewards") val rewards: Long,
    @kotlinx.serialization.SerialName("lockPeriod") val lockPeriod: Long,
    @kotlinx.serialization.SerialName("endTime") val endTime: Long
)

@kotlinx.serialization.Serializable
data class ValidatorDto(
    @kotlinx.serialization.SerialName("address") val address: String,
    @kotlinx.serialization.SerialName("stakeAmount") val stakeAmount: Long,
    @kotlinx.serialization.SerialName("uptime") val uptime: Double,
    @kotlinx.serialization.SerialName("blocksValidated") val blocksValidated: Int,
    @kotlinx.serialization.SerialName("rewards") val rewards: Long,
    @kotlinx.serialization.SerialName("isActive") val isActive: Boolean
)

@kotlinx.serialization.Serializable
data class FundDto(
    @kotlinx.serialization.SerialName("address") val address: String,
    @kotlinx.serialization.SerialName("balance") val balance: Long,
    @kotlinx.serialization.SerialName("vestingTotal") val vestingTotal: Long,
    @kotlinx.serialization.SerialName("vestingReleased") val vestingReleased: Long,
    @kotlinx.serialization.SerialName("treasuryBalance") val treasuryBalance: Long
)
