package com.globex.feature_dashboard.domain.model

data class DashboardState(
    val balance: Double = 0.0,
    val blockHeight: Long = 0L,
    val difficulty: Double = 0.0,
    val peerCount: Int = 0,
    val hashRate: Double = 0.0,
    val latestBlocks: List<BlockSummary> = emptyList(),
    val syncStatus: SyncStatus = SyncStatus.NOT_SYNCED,
    val stakingAmount: Double = 0.0,
    val validatorStatus: ValidatorStatus = ValidatorStatus.INACTIVE,
    val isLoading: Boolean = false,
    val error: String? = null
)

data class BlockSummary(
    val height: Long,
    val hash: String,
    val timestamp: Long,
    val transactions: Int
)

enum class SyncStatus {
    NOT_SYNCED,
    SYNCING,
    SYNCED
}

enum class ValidatorStatus {
    INACTIVE,
    ACTIVE,
    SLASHED,
    PENDING
}
