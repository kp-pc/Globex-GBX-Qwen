package com.globex.wallet.api

import com.globex.wallet.model.*
import retrofit2.Response
import retrofit2.http.*

/**
 * Retrofit API interface for Globex Blockchain Node
 * 
 * Provides type-safe access to all blockchain endpoints
 */
interface GlobexApi {

    // ==================== Wallet Operations ====================

    /**
     * Create a new wallet with ECDSA keys
     * POST /api/create-wallet
     */
    @POST("api/create-wallet")
    suspend fun createWallet(): Response<WalletResponse>

    /**
     * Get balance for an address
     * GET /api/balance/{address}
     */
    @GET("api/balance/{address}")
    suspend fun getBalance(@Path("address") address: String): Response<BalanceResponse>

    /**
     * Get UTXOs for an address
     * GET /api/utxo/{address}
     */
    @GET("api/utxo/{address}")
    suspend fun getUTXOs(@Path("address") address: String): Response<List<UTXO>>

    // ==================== Mining Operations ====================

    /**
     * Mine a new block
     * POST /api/mine
     */
    @POST("api/mine")
    suspend fun mineBlock(@Body params: MineParams = MineParams()): Response<MineResponse>

    /**
     * Mine multiple blocks continuously
     * POST /api/mine/continuous
     */
    @POST("api/mine/continuous")
    suspend fun mineContinuous(@Body params: MineContinuousParams): Response<MineResponse>

    /**
     * Get current mining stats
     * GET /api/mining/stats
     */
    @GET("api/mining/stats")
    suspend fun getMiningStats(): Response<MiningStats>

    // ==================== Transaction Operations ====================

    /**
     * Send a new transaction
     * POST /api/send
     */
    @POST("api/send")
    suspend fun sendTransaction(@Body params: SendTransactionParams): Response<TransactionResponse>

    /**
     * Get transaction by ID
     * GET /api/transaction/{txid}
     */
    @GET("api/transaction/{txid}")
    suspend fun getTransaction(@Path("txid") txid: String): Response<Transaction>

    /**
     * Get pending transactions (mempool)
     * GET /api/mempool
     */
    @GET("api/mempool")
    suspend fun getMempool(): Response<List<Transaction>>

    // ==================== Blockchain Operations ====================

    /**
     * Get blockchain info
     * GET /api/info
     */
    @GET("api/info")
    suspend fun getBlockchainInfo(): Response<BlockchainInfo>

    /**
     * Get full blockchain
     * GET /api/chain
     */
    @GET("api/chain")
    suspend fun getChain(): Response<ChainResponse>

    /**
     * Get specific block by index
     * GET /api/block/{index}
     */
    @GET("api/block/{index}")
    suspend fun getBlock(@Path("index") index: Int): Response<Block>

    /**
     * Get latest block
     * GET /api/block/latest
     */
    @GET("api/block/latest")
    suspend fun getLatestBlock(): Response<Block>

    /**
     * Validate the entire blockchain
     * POST /api/validate
     */
    @POST("api/validate")
    suspend fun validateChain(): Response<ValidateResponse>

    // ==================== Node/Network Operations ====================

    /**
     * Get connected nodes
     * GET /api/nodes
     */
    @GET("api/nodes")
    suspend fun getNodes(): Response<NodesResponse>

    /**
     * Register a new node
     * POST /api/nodes/register
     */
    @POST("api/nodes/register")
    suspend fun registerNode(@Body params: RegisterNodeParams): Response<NodesResponse>

    /**
     * Resolve conflicts (longest chain consensus)
     * POST /api/nodes/resolve
     */
    @POST("api/nodes/resolve")
    suspend fun resolveConflicts(): Response<ResolveConflictsResponse>

    // ==================== Staking/PoS Operations ====================

    /**
     * Register as a validator (stake)
     * POST /api/stake
     */
    @POST("api/stake")
    suspend fun stake(@Body params: StakeParams): Response<StakeResponse>

    /**
     * Get validator info
     * GET /api/validator/{address}
     */
    @GET("api/validator/{address}")
    suspend fun getValidatorInfo(@Path("address") address: String): Response<ValidatorInfo>

    /**
     * Get all validators
     * GET /api/validators
     */
    @GET("api/validators")
    suspend fun getAllValidators(): Response<List<ValidatorInfo>>

    // ==================== Development Fund Operations ====================

    /**
     * Get development fund status
     * GET /api/devfund/status
     */
    @GET("api/devfund/status")
    suspend fun getDevFundStatus(): Response<DevFundStatus>

    /**
     * Propose a development fund expenditure
     * POST /api/devfund/propose
     */
    @POST("api/devfund/propose")
    suspend fun proposeDevFund(@Body params: DevFundProposalParams): Response<DevFundProposal>

    /**
     * Sign a development fund proposal
     * POST /api/devfund/sign/{proposal_id}
     */
    @POST("api/devfund/sign/{proposal_id}")
    suspend fun signDevFundProposal(
        @Path("proposal_id") proposalId: String,
        @Body params: SignProposalParams
    ): Response<DevFundProposal>

    // ==================== Checkpoint Operations ====================

    /**
     * Get finality checkpoints
     * GET /api/checkpoints
     */
    @GET("api/checkpoints")
    suspend fun getCheckpoints(): Response<List<Checkpoint>>

    /**
     * Get latest checkpoint
     * GET /api/checkpoint/latest
     */
    @GET("api/checkpoint/latest")
    suspend fun getLatestCheckpoint(): Response<Checkpoint>
}

// ==================== Request Parameter Classes ====================

/**
 * Parameters for mining operation
 */
data class MineParams(
    val address: String? = null,
    val threads: Int = 1
)

/**
 * Parameters for continuous mining
 */
data class MineContinuousParams(
    val address: String,
    val count: Int = 10,
    val threads: Int = 1
)

/**
 * Parameters for sending a transaction
 */
data class SendTransactionParams(
    val from: String,
    val to: String,
    val amount: Double,
    val fee: Double = 0.01,
    val data: String? = null
)

/**
 * Parameters for registering a node
 */
data class RegisterNodeParams(
    val address: String,
    val port: Int
)

/**
 * Response for resolving conflicts
 */
data class ResolveConflictsResponse(
    val replaced: Boolean,
    val length: Int,
    val message: String
)

/**
 * Parameters for staking
 */
data class StakeParams(
    val address: String,
    val amount: Double,
    val lockup_blocks: Long = 43200 // ~30 days at 60s blocks
)

/**
 * Validator information
 */
data class ValidatorInfo(
    val address: String,
    val stakedAmount: Double,
    val rewards: Double,
    val blocksValidated: Int,
    val isActive: Boolean,
    val lastActiveTimestamp: Long
)

/**
 * Parameters for dev fund proposal
 */
data class DevFundProposalParams(
    val description: String,
    val amount: Double,
    val recipient: String,
    val proposer: String
)

/**
 * Parameters for signing a proposal
 */
data class SignProposalParams(
    val signer: String,
    val signature: String
)

/**
 * Checkpoint data
 */
data class Checkpoint(
    val blockIndex: Int,
    val blockHash: String,
    val timestamp: Long,
    val validatorCount: Int,
    val signatures: Int,
    val isFinalized: Boolean
)

/**
 * Mining statistics
 */
data class MiningStats(
    val hashRate: String,
    val blocksMined: Int,
    val totalRewards: Double,
    val difficulty: Int,
    val networkDifficulty: Int
)
