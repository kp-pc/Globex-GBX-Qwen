package com.globex.feature_dashboard.domain.repository

import com.globex.core.domain.model.Block
import com.globex.feature_dashboard.domain.model.BlockSummary
import com.globex.feature_dashboard.domain.model.SyncStatus
import kotlinx.coroutines.flow.Flow

interface DashboardRepository {
    fun getBalance(): Flow<Double>
    fun getBlockHeight(): Flow<Long>
    fun getDifficulty(): Flow<Double>
    fun getPeerCount(): Flow<Int>
    fun getHashRate(): Flow<Double>
    fun getLatestBlocks(limit: Int = 10): Flow<List<BlockSummary>>
    fun getSyncStatus(): Flow<SyncStatus>
    fun getStakingAmount(): Flow<Double>
    fun getValidatorStatus(): Flow<String>
    suspend fun refreshDashboard()
}
