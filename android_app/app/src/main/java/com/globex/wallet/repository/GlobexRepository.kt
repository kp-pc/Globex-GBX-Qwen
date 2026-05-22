package com.globex.wallet.repository

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import com.globex.wallet.api.GlobexApi
import com.globex.wallet.model.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import retrofit2.Response
import java.io.IOException

/**
 * Repository pattern implementation for Globex Blockchain
 * 
 * Handles data operations between the API and local storage
 * Provides a clean abstraction layer for the UI
 */
class GlobexRepository(
    private val api: GlobexApi,
    private val context: Context
) {

    // Encrypted SharedPreferences for secure wallet storage
    private val sharedPreferences: SharedPreferences by lazy {
        val masterKey = MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()

        EncryptedSharedPreferences.create(
            context,
            "globex_wallet_prefs",
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    }

    // Local cache for blockchain info
    private var cachedBlockchainInfo: BlockchainInfo? = null
    private var cacheTimestamp: Long = 0
    private val CACHE_DURATION_MS = 30_000L // 30 seconds

    // ==================== Wallet Operations ====================

    /**
     * Create a new wallet and save it locally
     */
    suspend fun createWallet(): Result<WalletResponse> = withContext(Dispatchers.IO) {
        try {
            val response = api.createWallet()
            if (response.isSuccessful && response.body() != null) {
                val wallet = response.body()!!
                // Save wallet address to secure storage
                saveWalletAddress(wallet.address)
                Result.success(wallet)
            } else {
                Result.failure(IOException("Failed to create wallet: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Get balance for an address with optional caching
     */
    suspend fun getBalance(address: String, useCache: Boolean = true): Result<BalanceResponse> =
        withContext(Dispatchers.IO) {
            try {
                val response = api.getBalance(address)
                if (response.isSuccessful && response.body() != null) {
                    Result.success(response.body()!!)
                } else {
                    Result.failure(IOException("Failed to get balance: ${response.code()}"))
                }
            } catch (e: Exception) {
                Result.failure(e)
            }
        }

    /**
     * Get UTXOs for an address
     */
    suspend fun getUTXOs(address: String): Result<List<UTXO>> = withContext(Dispatchers.IO) {
        try {
            val response = api.getUTXOs(address)
            if (response.isSuccessful) {
                Result.success(response.body() ?: emptyList())
            } else {
                Result.failure(IOException("Failed to get UTXOs: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Save wallet address to encrypted storage
     */
    fun saveWalletAddress(address: String) {
        sharedPreferences.edit().putString("wallet_address", address).apply()
    }

    /**
     * Get saved wallet address from encrypted storage
     */
    fun getSavedWalletAddress(): String? {
        return sharedPreferences.getString("wallet_address", null)
    }

    /**
     * Clear saved wallet
     */
    fun clearSavedWallet() {
        sharedPreferences.edit().remove("wallet_address").apply()
    }

    // ==================== Mining Operations ====================

    /**
     * Mine a single block
     */
    suspend fun mineBlock(address: String? = null, threads: Int = 1): Result<MineResponse> =
        withContext(Dispatchers.IO) {
            try {
                val params = MineParams(address, threads)
                val response = api.mineBlock(params)
                if (response.isSuccessful && response.body() != null) {
                    // Refresh blockchain info after mining
                    refreshBlockchainInfo()
                    Result.success(response.body()!!)
                } else {
                    Result.failure(IOException("Mining failed: ${response.code()}"))
                }
            } catch (e: Exception) {
                Result.failure(e)
            }
        }

    /**
     * Mine multiple blocks continuously
     */
    suspend fun mineContinuous(
        address: String,
        count: Int = 10,
        threads: Int = 1
    ): Result<MineResponse> = withContext(Dispatchers.IO) {
        try {
            val params = MineContinuousParams(address, count, threads)
            val response = api.mineContinuous(params)
            if (response.isSuccessful && response.body() != null) {
                refreshBlockchainInfo()
                Result.success(response.body()!!)
            } else {
                Result.failure(IOException("Continuous mining failed: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Get current mining statistics
     */
    suspend fun getMiningStats(): Result<MiningStats> = withContext(Dispatchers.IO) {
        try {
            val response = api.getMiningStats()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(IOException("Failed to get mining stats: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // ==================== Transaction Operations ====================

    /**
     * Send a transaction
     */
    suspend fun sendTransaction(
        from: String,
        to: String,
        amount: Double,
        fee: Double = 0.01,
        data: String? = null
    ): Result<TransactionResponse> = withContext(Dispatchers.IO) {
        try {
            val params = SendTransactionParams(from, to, amount, fee, data)
            val response = api.sendTransaction(params)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(IOException("Transaction failed: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Get transaction by ID
     */
    suspend fun getTransaction(txid: String): Result<Transaction> = withContext(Dispatchers.IO) {
        try {
            val response = api.getTransaction(txid)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(IOException("Transaction not found: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Get pending transactions from mempool
     */
    suspend fun getMempool(): Result<List<Transaction>> = withContext(Dispatchers.IO) {
        try {
            val response = api.getMempool()
            if (response.isSuccessful) {
                Result.success(response.body() ?: emptyList())
            } else {
                Result.failure(IOException("Failed to get mempool: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // ==================== Blockchain Operations ====================

    /**
     * Get blockchain info with caching
     */
    suspend fun getBlockchainInfo(useCache: Boolean = true): Result<BlockchainInfo> =
        withContext(Dispatchers.IO) {
            // Check cache first
            if (useCache && cachedBlockchainInfo != null) {
                val now = System.currentTimeMillis()
                if (now - cacheTimestamp < CACHE_DURATION_MS) {
                    return@withContext Result.success(cachedBlockchainInfo!!)
                }
            }

            try {
                val response = api.getBlockchainInfo()
                if (response.isSuccessful && response.body() != null) {
                    val info = response.body()!!
                    cachedBlockchainInfo = info
                    cacheTimestamp = System.currentTimeMillis()
                    Result.success(info)
                } else {
                    Result.failure(IOException("Failed to get blockchain info: ${response.code()}"))
                }
            } catch (e: Exception) {
                Result.failure(e)
            }
        }

    /**
     * Force refresh blockchain info (bypass cache)
     */
    suspend fun refreshBlockchainInfo(): Result<BlockchainInfo> {
        return getBlockchainInfo(useCache = false)
    }

    /**
     * Get full blockchain
     */
    suspend fun getChain(): Result<ChainResponse> = withContext(Dispatchers.IO) {
        try {
            val response = api.getChain()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(IOException("Failed to get chain: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Get block by index
     */
    suspend fun getBlock(index: Int): Result<Block> = withContext(Dispatchers.IO) {
        try {
            val response = api.getBlock(index)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(IOException("Block not found: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Get latest block
     */
    suspend fun getLatestBlock(): Result<Block> = withContext(Dispatchers.IO) {
        try {
            val response = api.getLatestBlock()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(IOException("Failed to get latest block: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Validate the entire blockchain
     */
    suspend fun validateChain(): Result<ValidateResponse> = withContext(Dispatchers.IO) {
        try {
            val response = api.validateChain()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(IOException("Validation failed: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // ==================== Node/Network Operations ====================

    /**
     * Get connected nodes
     */
    suspend fun getNodes(): Result<NodesResponse> = withContext(Dispatchers.IO) {
        try {
            val response = api.getNodes()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(IOException("Failed to get nodes: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Register a new node
     */
    suspend fun registerNode(address: String, port: Int): Result<NodesResponse> =
        withContext(Dispatchers.IO) {
            try {
                val params = RegisterNodeParams(address, port)
                val response = api.registerNode(params)
                if (response.isSuccessful && response.body() != null) {
                    Result.success(response.body()!!)
                } else {
                    Result.failure(IOException("Failed to register node: ${response.code()}"))
                }
            } catch (e: Exception) {
                Result.failure(e)
            }
        }

    /**
     * Resolve conflicts using longest chain consensus
     */
    suspend fun resolveConflicts(): Result<ResolveConflictsResponse> =
        withContext(Dispatchers.IO) {
            try {
                val response = api.resolveConflicts()
                if (response.isSuccessful && response.body() != null) {
                    Result.success(response.body()!!)
                } else {
                    Result.failure(IOException("Conflict resolution failed: ${response.code()}"))
                }
            } catch (e: Exception) {
                Result.failure(e)
            }
        }

    // ==================== Staking/PoS Operations ====================

    /**
     * Register as a validator (stake)
     */
    suspend fun stake(
        address: String,
        amount: Double,
        lockupBlocks: Long = 43200
    ): Result<StakeResponse> = withContext(Dispatchers.IO) {
        try {
            val params = StakeParams(address, amount, lockupBlocks)
            val response = api.stake(params)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(IOException("Staking failed: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Get validator info by address
     */
    suspend fun getValidatorInfo(address: String): Result<ValidatorInfo> =
        withContext(Dispatchers.IO) {
            try {
                val response = api.getValidatorInfo(address)
                if (response.isSuccessful && response.body() != null) {
                    Result.success(response.body()!!)
                } else {
                    Result.failure(IOException("Validator not found: ${response.code()}"))
                }
            } catch (e: Exception) {
                Result.failure(e)
            }
        }

    /**
     * Get all validators
     */
    suspend fun getAllValidators(): Result<List<ValidatorInfo>> = withContext(Dispatchers.IO) {
        try {
            val response = api.getAllValidators()
            if (response.isSuccessful) {
                Result.success(response.body() ?: emptyList())
            } else {
                Result.failure(IOException("Failed to get validators: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // ==================== Development Fund Operations ====================

    /**
     * Get development fund status
     */
    suspend fun getDevFundStatus(): Result<DevFundStatus> = withContext(Dispatchers.IO) {
        try {
            val response = api.getDevFundStatus()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(IOException("Failed to get dev fund status: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Propose a development fund expenditure
     */
    suspend fun proposeDevFund(
        description: String,
        amount: Double,
        recipient: String,
        proposer: String
    ): Result<DevFundProposal> = withContext(Dispatchers.IO) {
        try {
            val params = DevFundProposalParams(description, amount, recipient, proposer)
            val response = api.proposeDevFund(params)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(IOException("Proposal failed: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Sign a development fund proposal
     */
    suspend fun signDevFundProposal(
        proposalId: String,
        signer: String,
        signature: String
    ): Result<DevFundProposal> = withContext(Dispatchers.IO) {
        try {
            val params = SignProposalParams(signer, signature)
            val response = api.signDevFundProposal(proposalId, params)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(IOException("Signing failed: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // ==================== Checkpoint Operations ====================

    /**
     * Get all finality checkpoints
     */
    suspend fun getCheckpoints(): Result<List<Checkpoint>> = withContext(Dispatchers.IO) {
        try {
            val response = api.getCheckpoints()
            if (response.isSuccessful) {
                Result.success(response.body() ?: emptyList())
            } else {
                Result.failure(IOException("Failed to get checkpoints: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Get latest checkpoint
     */
    suspend fun getLatestCheckpoint(): Result<Checkpoint> = withContext(Dispatchers.IO) {
        try {
            val response = api.getLatestCheckpoint()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(IOException("Failed to get latest checkpoint: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // ==================== Utility Methods ====================

    /**
     * Clear all cached data
     */
    fun clearCache() {
        cachedBlockchainInfo = null
        cacheTimestamp = 0
    }

    /**
     * Check if we have a saved wallet
     */
    fun hasSavedWallet(): Boolean {
        return getSavedWalletAddress() != null
    }
}
