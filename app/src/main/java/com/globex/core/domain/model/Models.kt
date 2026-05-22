package com.globex.core.domain.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/**
 * Wallet data model representing a user's wallet
 */
@Serializable
data class Wallet(
    @SerialName("address") val address: String,
    @SerialName("publicKey") val publicKey: String,
    @SerialName("balance") val balance: Long,
    @SerialName("pendingBalance") val pendingBalance: Long = 0,
    @SerialName("nonce") val nonce: Int = 0,
    @SerialName("createdAt") val createdAt: Long = System.currentTimeMillis(),
    @SerialName("lastSyncedAt") val lastSyncedAt: Long? = null,
    @SerialName("isBackedUp") val isBackedUp: Boolean = false
) {
    val totalBalance: Long
        get() = balance + pendingBalance

    val formattedBalance: String
        get() = String.format("%.8f", balance / 1e8)
}

/**
 * Transaction data model
 */
@Serializable
data class Transaction(
    @SerialName("id") val id: String,
    @SerialName("fromAddress") val fromAddress: String,
    @SerialName("toAddress") val toAddress: String,
    @SerialName("amount") val amount: Long,
    @SerialName("fee") val fee: Long = 0,
    @SerialName("timestamp") val timestamp: Long = System.currentTimeMillis(),
    @SerialName("signature") val signature: String? = null,
    @SerialName("blockHash") val blockHash: String? = null,
    @SerialName("blockHeight") val blockHeight: Long? = null,
    @SerialName("confirmations") val confirmations: Int = 0,
    @SerialName("memo") val memo: String? = null,
    @SerialName("status") val status: TransactionStatus = TransactionStatus.PENDING
) {
    enum class TransactionStatus {
        PENDING,
        CONFIRMED,
        FAILED,
        REJECTED
    }

    val totalAmount: Long
        get() = amount + fee

    val formattedAmount: String
        get() = String.format("%.8f", amount / 1e8)
}

/**
 * Block data model
 */
@Serializable
data class Block(
    @SerialName("height") val height: Long,
    @SerialName("hash") val hash: String,
    @SerialName("previousHash") val previousHash: String,
    @SerialName("timestamp") val timestamp: Long,
    @SerialName("nonce") val nonce: Long,
    @SerialName("difficulty") val difficulty: Long,
    @SerialName("merkleRoot") val merkleRoot: String,
    @SerialName("transactions") val transactions: List<Transaction> = emptyList(),
    @SerialName("miner") val miner: String? = null,
    @SerialName("size") val size: Int = 0,
    @SerialName("confirmations") val confirmations: Int = 0,
    @SerialName("validator") val validator: String? = null,
    @SerialName("stakeAmount") val stakeAmount: Long? = null
) {
    val transactionCount: Int
        get() = transactions.size

    val formattedDifficulty: String
        get() = String.format("%.4f", difficulty / 1e6)
}

/**
 * Node data model
 */
@Serializable
data class Node(
    @SerialName("id") val id: String,
    @SerialName("url") val url: String,
    @SerialName("height") val height: Long = 0,
    @SerialName("latency") val latency: Long = 0,
    @SerialName("status") val status: NodeStatus = NodeStatus.UNKNOWN,
    @SerialName("lastSeen") val lastSeen: Long? = null,
    @SerialName("version") val version: String? = null,
    @SerialName("isTrusted") val isTrusted: Boolean = false,
    @SerialName("peerCount") val peerCount: Int = 0
) {
    enum class NodeStatus {
        ONLINE,
        OFFLINE,
        SYNCING,
        UNKNOWN
    }

    val isActive: Boolean
        get() = status == NodeStatus.ONLINE || status == NodeStatus.SYNCING
}

/**
 * Mining session data model
 */
@Serializable
data class MiningSession(
    @SerialName("id") val id: String,
    @SerialName("startTime") val startTime: Long = System.currentTimeMillis(),
    @SerialName("endTime") val endTime: Long? = null,
    @SerialName("hashRate") val hashRate: Double = 0.0,
    @SerialName("blocksFound") val blocksFound: Int = 0,
    @SerialName("totalRewards") val totalRewards: Long = 0,
    @SerialName("threadCount") val threadCount: Int = 1,
    @SerialName("isActive") val isActive: Boolean = false,
    @SerialName("difficulty") val difficulty: Long = 0,
    @SerialName("estimatedEarnings") val estimatedEarnings: Long = 0
) {
    val duration: Long
        get() = (endTime ?: System.currentTimeMillis()) - startTime

    val formattedHashRate: String
        get() = "${String.format("%.2f", hashRate)} H/s"

    val formattedRewards: String
        get() = String.format("%.8f", totalRewards / 1e8)
}

/**
 * Validator data model
 */
@Serializable
data class Validator(
    @SerialName("address") val address: String,
    @SerialName("stakeAmount") val stakeAmount: Long,
    @SerialName("uptime") val uptime: Double = 100.0,
    @SerialName("blocksValidated") val blocksValidated: Int = 0,
    @SerialName("penalties") val penalties: Int = 0,
    @SerialName("rewards") val rewards: Long = 0,
    @SerialName("isActive") val isActive: Boolean = false,
    @SerialName("joinedAt") val joinedAt: Long = System.currentTimeMillis(),
    @SerialName("lastValidatedBlock") val lastValidatedBlock: Long? = null,
    @SerialName("slashingEvents") val slashingEvents: List<SlashingEvent> = emptyList()
) {
    val formattedStake: String
        get() = String.format("%.8f", stakeAmount / 1e8)

    val formattedUptime: String
        get() = String.format("%.2f%%", uptime)

    val formattedRewards: String
        get() = String.format("%.8f", rewards / 1e8)
}

/**
 * Stake data model
 */
@Serializable
data class Stake(
    @SerialName("id") val id: String,
    @SerialName("address") val address: String,
    @SerialName("amount") val amount: Long,
    @SerialName("lockPeriod") val lockPeriod: Long,
    @SerialName("startTime") val startTime: Long = System.currentTimeMillis(),
    @SerialName("endTime") val endTime: Long,
    @SerialName("estimatedRewards") val estimatedRewards: Long = 0,
    @SerialName("actualRewards") val actualRewards: Long = 0,
    @SerialName("status") val status: StakeStatus = StakeStatus.ACTIVE,
    @SerialName("validatorAddress") val validatorAddress: String? = null
) {
    enum class StakeStatus {
        ACTIVE,
        LOCKED,
        UNLOCKING,
        COMPLETED,
        SLASHED
    }

    val remainingTime: Long
        get() = maxOf(0, endTime - System.currentTimeMillis())

    val formattedAmount: String
        get() = String.format("%.8f", amount / 1e8)

    val isUnlocked: Boolean
        get() = System.currentTimeMillis() >= endTime
}

/**
 * Fund data model for development fund
 */
@Serializable
data class Fund(
    @SerialName("address") val address: String,
    @SerialName("balance") val balance: Long,
    @SerialName("vestingTotal") val vestingTotal: Long,
    @SerialName("vestingReleased") val vestingReleased: Long = 0,
    @SerialName("vestingCliff") val vestingCliff: Long,
    @SerialName("vestingDuration") val vestingDuration: Long,
    @SerialName("treasuryBalance") val treasuryBalance: Long = 0,
    @SerialName("lastReport") val lastReport: FundReport? = null,
    @SerialName("multisigThreshold") val multisigThreshold: Int = 3,
    @SerialName("multisigSigners") val multisigSigners: List<String> = emptyList()
) {
    val formattedBalance: String
        get() = String.format("%.8f", balance / 1e8)

    val formattedTreasury: String
        get() = String.format("%.8f", treasuryBalance / 1e8)

    val releasePercentage: Double
        get() = if (vestingTotal > 0) (vestingReleased.toDouble() / vestingTotal) * 100 else 0.0
}

/**
 * Fund report data model
 */
@Serializable
data class FundReport(
    @SerialName("id") val id: String,
    @SerialName("title") val title: String,
    @SerialName("description") val description: String,
    @SerialName("amount") val amount: Long,
    @SerialName("recipient") val recipient: String,
    @SerialName("timestamp") val timestamp: Long = System.currentTimeMillis(),
    @SerialName("status") val status: ReportStatus = ReportStatus.PENDING,
    @SerialName("approvals") val approvals: List<String> = emptyList()
) {
    enum class ReportStatus {
        PENDING,
        APPROVED,
        REJECTED,
        EXECUTED
    }

    val formattedAmount: String
        get() = String.format("%.8f", amount / 1e8)
}

/**
 * Slashing event data model
 */
@Serializable
data class SlashingEvent(
    @SerialName("id") val id: String,
    @SerialName("validatorAddress") val validatorAddress: String,
    @SerialName("amount") val amount: Long,
    @SerialName("reason") val reason: String,
    @SerialName("timestamp") val timestamp: Long = System.currentTimeMillis(),
    @SerialName("blockHeight") val blockHeight: Long
) {
    val formattedAmount: String
        get() = String.format("%.8f", amount / 1e8)
}

/**
 * Checkpoint data model for finality
 */
@Serializable
data class Checkpoint(
    @SerialName("height") val height: Long,
    @SerialName("hash") val hash: String,
    @SerialName("timestamp") val timestamp: Long,
    @SerialName("validatorCount") val validatorCount: Int,
    @SerialName("votes") val votes: Int,
    @SerialName("isFinalized") val isFinalized: Boolean = false,
    @SerialName("epoch") val epoch: Long
) {
    val votePercentage: Double
        get() = if (validatorCount > 0) (votes.toDouble() / validatorCount) * 100 else 0.0
}
