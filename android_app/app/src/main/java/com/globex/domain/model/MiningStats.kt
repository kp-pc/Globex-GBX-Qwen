package com.globex.wallet.domain.model

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.Date

@Entity(tableName = "mining_stats")
data class MiningStats(
    @PrimaryKey
    val id: String,
    val walletId: String,
    val isMining: Boolean = false,
    val totalHashes: Long = 0L,
    val hashesPerSecond: Double = 0.0,
    val blocksFound: Int = 0,
    val totalRewards: Double = 0.0,
    val startTime: Date? = null,
    val lastUpdated: Date = Date()
)
