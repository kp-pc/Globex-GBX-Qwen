package com.globex.core.data.repository

import com.globex.core.data.api.GlobexApi
import com.globex.core.data.dto.*
import com.globex.core.domain.model.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import retrofit2.HttpException
import java.io.IOException

/**
 * Repository for wallet operations using Coroutines and Flow
 */
class WalletRepository(
    private val api: GlobexApi
) {
    
    fun getBalance(address: String): Flow<Result<Wallet>> = flow {
        try {
            val response = api.getBalance(address)
            if (response.isSuccessful && response.body() != null) {
                val dto = response.body()!!.data
                if (dto != null) {
                    emit(Result.success(
                        Wallet(
                            address = dto.address,
                            publicKey = "",
                            balance = dto.balance,
                            pendingBalance = dto.pendingBalance,
                            nonce = dto.nonce
                        )
                    ))
                } else {
                    emit(Result.failure(Exception("Balance data not found")))
                }
            } else {
                emit(Result.failure(HttpException(response)))
            }
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }

    fun getTransactions(address: String, page: Int = 0, limit: Int = 20): Flow<Result<List<Transaction>>> = flow {
        try {
            val response = api.getTransactions(address, page, limit)
            if (response.isSuccessful && response.body() != null) {
                val dtos = response.body()!!.data ?: emptyList()
                val transactions = dtos.map { dto ->
                    Transaction(
                        id = dto.id,
                        fromAddress = dto.fromAddress,
                        toAddress = dto.toAddress,
                        amount = dto.amount,
                        fee = dto.fee,
                        timestamp = dto.timestamp,
                        signature = dto.signature,
                        memo = dto.memo
                    )
                }
                emit(Result.success(transactions))
            } else {
                emit(Result.failure(HttpException(response)))
            }
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }

    suspend fun createTransaction(request: TransactionRequest): Result<Transaction> {
        return try {
            val response = api.createTransaction(request)
            if (response.isSuccessful && response.body() != null) {
                val body = response.body()!!
                if (body.success && body.transaction != null) {
                    val dto = body.transaction
                    Result.success(
                        Transaction(
                            id = dto.id,
                            fromAddress = dto.fromAddress,
                            toAddress = dto.toAddress,
                            amount = dto.amount,
                            fee = dto.fee,
                            timestamp = dto.timestamp,
                            signature = dto.signature,
                            memo = dto.memo,
                            status = Transaction.TransactionStatus.PENDING
                        )
                    )
                } else {
                    Result.failure(Exception(body.message ?: "Transaction failed"))
                }
            } else {
                Result.failure(HttpException(response))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

/**
 * Repository for mining operations using Coroutines and Flow
 */
class MiningRepository(
    private val api: GlobexApi
) {
    
    fun mineBlock(minerAddress: String): Flow<Result<MiningSession>> = flow {
        try {
            val request = MineRequest(minerAddress)
            val response = api.mineBlock(request)
            if (response.isSuccessful && response.body() != null) {
                val body = response.body()!!
                if (body.success) {
                    val session = MiningSession(
                        id = System.currentTimeMillis().toString(),
                        hashRate = 0.0,
                        blocksFound = if (body.block != null) 1 else 0,
                        totalRewards = body.reward,
                        isActive = false,
                        estimatedEarnings = body.reward
                    )
                    emit(Result.success(session))
                } else {
                    emit(Result.failure(Exception(body.message ?: "Mining failed")))
                }
            } else {
                emit(Result.failure(HttpException(response)))
            }
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }

    fun getNetworkStats(): Flow<Result<NetworkStats>> = flow {
        try {
            val response = api.getNetworkStats()
            if (response.isSuccessful && response.body() != null) {
                val dto = response.body()!!.data
                if (dto != null) {
                    emit(Result.success(
                        NetworkStats(
                            blockHeight = dto.blockHeight,
                            difficulty = dto.difficulty,
                            peerCount = dto.peerCount,
                            hashRate = dto.hashRate,
                            totalSupply = dto.totalSupply,
                            circulatingSupply = dto.circulatingSupply
                        )
                    ))
                } else {
                    emit(Result.failure(Exception("Network stats not found")))
                }
            } else {
                emit(Result.failure(HttpException(response)))
            }
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }
}

/**
 * Repository for node operations using Coroutines and Flow
 */
class NodeRepository(
    private val api: GlobexApi
) {
    
    fun registerNode(url: String): Flow<Result<Node>> = flow {
        try {
            val request = NodeRegisterRequest(url)
            val response = api.registerNode(request)
            if (response.isSuccessful && response.body() != null) {
                val body = response.body()!!
                if (body.success && body.node != null) {
                    val dto = body.node
                    emit(Result.success(
                        Node(
                            id = dto.id,
                            url = dto.url,
                            height = dto.height,
                            status = when (dto.status.lowercase()) {
                                "online" -> Node.NodeStatus.ONLINE
                                "offline" -> Node.NodeStatus.OFFLINE
                                "syncing" -> Node.NodeStatus.SYNCING
                                else -> Node.NodeStatus.UNKNOWN
                            }
                        )
                    ))
                } else {
                    emit(Result.failure(Exception(body.message ?: "Node registration failed")))
                }
            } else {
                emit(Result.failure(HttpException(response)))
            }
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }

    fun resolveChain(): Flow<Result<List<Block>>> = flow {
        try {
            val response = api.resolveChain()
            if (response.isSuccessful && response.body() != null) {
                val body = response.body()!!
                if (body.success && body.chain != null) {
                    val blocks = body.chain.map { dto ->
                        Block(
                            height = dto.height,
                            hash = dto.hash,
                            previousHash = dto.previousHash,
                            timestamp = dto.timestamp,
                            nonce = dto.nonce,
                            difficulty = dto.difficulty,
                            merkleRoot = dto.merkleRoot,
                            miner = dto.miner
                        )
                    }
                    emit(Result.success(blocks))
                } else {
                    emit(Result.failure(Exception(body.message ?: "Chain resolution failed")))
                }
            } else {
                emit(Result.failure(HttpException(response)))
            }
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }

    fun getNodes(): Flow<Result<List<Node>>> = flow {
        try {
            val response = api.getNodes()
            if (response.isSuccessful && response.body() != null) {
                val dtos = response.body()!!.data ?: emptyList()
                val nodes = dtos.map { dto ->
                    Node(
                        id = dto.id,
                        url = dto.url,
                        height = dto.height
                    )
                }
                emit(Result.success(nodes))
            } else {
                emit(Result.failure(HttpException(response)))
            }
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }
}

/**
 * Repository for explorer operations using Coroutines and Flow
 */
class ExplorerRepository(
    private val api: GlobexApi
) {
    
    fun getBlockByHeight(height: Long): Flow<Result<Block>> = flow {
        try {
            val response = api.getBlockByHeight(height)
            if (response.isSuccessful && response.body() != null) {
                val dto = response.body()!!.data
                if (dto != null) {
                    emit(Result.success(
                        Block(
                            height = dto.height,
                            hash = dto.hash,
                            previousHash = dto.previousHash,
                            timestamp = dto.timestamp,
                            nonce = dto.nonce,
                            difficulty = dto.difficulty,
                            merkleRoot = dto.merkleRoot,
                            miner = dto.miner
                        )
                    ))
                } else {
                    emit(Result.failure(Exception("Block not found")))
                }
            } else {
                emit(Result.failure(HttpException(response)))
            }
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }

    fun getBlockByHash(hash: String): Flow<Result<Block>> = flow {
        try {
            val response = api.getBlockByHash(hash)
            if (response.isSuccessful && response.body() != null) {
                val dto = response.body()!!.data
                if (dto != null) {
                    emit(Result.success(
                        Block(
                            height = dto.height,
                            hash = dto.hash,
                            previousHash = dto.previousHash,
                            timestamp = dto.timestamp,
                            nonce = dto.nonce,
                            difficulty = dto.difficulty,
                            merkleRoot = dto.merkleRoot,
                            miner = dto.miner
                        )
                    ))
                } else {
                    emit(Result.failure(Exception("Block not found")))
                }
            } else {
                emit(Result.failure(HttpException(response)))
            }
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }

    fun getTransaction(id: String): Flow<Result<Transaction>> = flow {
        try {
            val response = api.getTransaction(id)
            if (response.isSuccessful && response.body() != null) {
                val dto = response.body()!!.data
                if (dto != null) {
                    emit(Result.success(
                        Transaction(
                            id = dto.id,
                            fromAddress = dto.fromAddress,
                            toAddress = dto.toAddress,
                            amount = dto.amount,
                            fee = dto.fee,
                            timestamp = dto.timestamp,
                            signature = dto.signature,
                            memo = dto.memo
                        )
                    ))
                } else {
                    emit(Result.failure(Exception("Transaction not found")))
                }
            } else {
                emit(Result.failure(HttpException(response)))
            }
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }

    fun getChain(): Flow<Result<List<Block>>> = flow {
        try {
            val response = api.getChain()
            if (response.isSuccessful && response.body() != null) {
                val dtos = response.body()!!.chain
                val blocks = dtos.map { dto ->
                    Block(
                        height = dto.height,
                        hash = dto.hash,
                        previousHash = dto.previousHash,
                        timestamp = dto.timestamp,
                        nonce = dto.nonce,
                        difficulty = dto.difficulty,
                        merkleRoot = dto.merkleRoot,
                        miner = dto.miner
                    )
                }
                emit(Result.success(blocks))
            } else {
                emit(Result.failure(HttpException(response)))
            }
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }
}

/**
 * Repository for staking operations using Coroutines and Flow
 */
class StakeRepository(
    private val api: GlobexApi
) {
    
    fun getStakingInfo(address: String): Flow<Result<Stake>> = flow {
        try {
            val response = api.getStakingInfo(address)
            if (response.isSuccessful && response.body() != null) {
                val dto = response.body()!!.data
                if (dto != null) {
                    emit(Result.success(
                        Stake(
                            id = System.currentTimeMillis().toString(),
                            address = dto.address,
                            amount = dto.stakedAmount,
                            lockPeriod = dto.lockPeriod,
                            endTime = dto.endTime,
                            actualRewards = dto.rewards
                        )
                    ))
                } else {
                    emit(Result.failure(Exception("Staking info not found")))
                }
            } else {
                emit(Result.failure(HttpException(response)))
            }
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }
}

/**
 * Repository for fund operations using Coroutines and Flow
 */
class FundRepository(
    private val api: GlobexApi
) {
    
    fun getFundInfo(): Flow<Result<Fund>> = flow {
        try {
            val response = api.getFundInfo()
            if (response.isSuccessful && response.body() != null) {
                val dto = response.body()!!.data
                if (dto != null) {
                    emit(Result.success(
                        Fund(
                            address = dto.address,
                            balance = dto.balance,
                            vestingTotal = dto.vestingTotal,
                            vestingReleased = dto.vestingReleased,
                            treasuryBalance = dto.treasuryBalance,
                            vestingCliff = 0,
                            vestingDuration = 0
                        )
                    ))
                } else {
                    emit(Result.failure(Exception("Fund info not found")))
                }
            } else {
                emit(Result.failure(HttpException(response)))
            }
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }
}

/**
 * Network stats model
 */
data class NetworkStats(
    val blockHeight: Long,
    val difficulty: Long,
    val peerCount: Int,
    val hashRate: Double,
    val totalSupply: Long,
    val circulatingSupply: Long
)
