package com.globex.core.data.local

import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * Room Entity for Wallet
 */
@Entity(tableName = "wallets")
data class WalletEntity(
    @PrimaryKey val address: String,
    val publicKey: String,
    val balance: Long,
    val pendingBalance: Long = 0,
    val nonce: Int = 0,
    val createdAt: Long = System.currentTimeMillis(),
    val lastSyncedAt: Long? = null,
    val isBackedUp: Boolean = false
)

/**
 * Room Entity for Transaction
 */
@Entity(tableName = "transactions")
data class TransactionEntity(
    @PrimaryKey val id: String,
    val fromAddress: String,
    val toAddress: String,
    val amount: Long,
    val fee: Long = 0,
    val timestamp: Long = System.currentTimeMillis(),
    val signature: String? = null,
    val blockHash: String? = null,
    val blockHeight: Long? = null,
    val confirmations: Int = 0,
    val memo: String? = null,
    val status: String = "PENDING"
)

/**
 * Room Entity for Block
 */
@Entity(tableName = "blocks")
data class BlockEntity(
    @PrimaryKey val hash: String,
    val height: Long,
    val previousHash: String,
    val timestamp: Long,
    val nonce: Long,
    val difficulty: Long,
    val merkleRoot: String,
    val miner: String? = null,
    val size: Int = 0,
    val confirmations: Int = 0,
    val validator: String? = null,
    val stakeAmount: Long? = null,
    val transactionCount: Int = 0
)

/**
 * Room Entity for Node
 */
@Entity(tableName = "nodes")
data class NodeEntity(
    @PrimaryKey val id: String,
    val url: String,
    val height: Long = 0,
    val latency: Long = 0,
    val status: String = "UNKNOWN",
    val lastSeen: Long? = null,
    val version: String? = null,
    val isTrusted: Boolean = false,
    val peerCount: Int = 0
)

/**
 * Room Entity for Mining Session
 */
@Entity(tableName = "mining_sessions")
data class MiningEntity(
    @PrimaryKey val id: String,
    val startTime: Long = System.currentTimeMillis(),
    val endTime: Long? = null,
    val hashRate: Double = 0.0,
    val blocksFound: Int = 0,
    val totalRewards: Long = 0,
    val threadCount: Int = 1,
    val isActive: Boolean = false,
    val difficulty: Long = 0,
    val estimatedEarnings: Long = 0
)

/**
 * Room Entity for Validator
 */
@Entity(tableName = "validators")
data class ValidatorEntity(
    @PrimaryKey val address: String,
    val stakeAmount: Long,
    val uptime: Double = 100.0,
    val blocksValidated: Int = 0,
    val penalties: Int = 0,
    val rewards: Long = 0,
    val isActive: Boolean = false,
    val joinedAt: Long = System.currentTimeMillis(),
    val lastValidatedBlock: Long? = null
)

/**
 * Room Entity for Fund
 */
@Entity(tableName = "funds")
data class FundEntity(
    @PrimaryKey val address: String,
    val balance: Long,
    val vestingTotal: Long,
    val vestingReleased: Long = 0,
    val vestingCliff: Long,
    val vestingDuration: Long,
    val treasuryBalance: Long = 0,
    val multisigThreshold: Int = 3,
    val lastReportId: String? = null
)
