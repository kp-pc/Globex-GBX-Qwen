package com.globex.feature_dashboard.data.repository

import com.globex.core.data.api.GlobexApi
import com.globex.core.data.local.dao.BlockDao
import com.globex.core.data.local.dao.WalletDao
import com.globex.feature_dashboard.domain.model.BlockSummary
import com.globex.feature_dashboard.domain.model.SyncStatus
import com.globex.feature_dashboard.domain.repository.DashboardRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class DashboardRepositoryImpl @Inject constructor(
    private val api: GlobexApi,
    private val walletDao: WalletDao,
    private val blockDao: BlockDao
) : DashboardRepository {

    override fun getBalance(): Flow<Double> = flow {
        val wallet = walletDao.getActiveWallet()
        emit(wallet?.balance ?: 0.0)
    }

    override fun getBlockHeight(): Flow<Long> = flow {
        val chain = api.getChain()
        emit(chain.body?.blocks?.size?.toLong() ?: 0L)
    }

    override fun getDifficulty(): Flow<Double> = flow {
        val chain = api.getChain()
        val latestBlock = chain.body?.blocks?.lastOrNull()
        emit(latestBlock?.difficulty ?: 0.0)
    }

    override fun getPeerCount(): Flow<Int> = flow {
        // TODO: Implement peer count from node service
        emit(0)
    }

    override fun getHashRate(): Flow<Double> = flow {
        // TODO: Implement hash rate from mining service
        emit(0.0)
    }

    override fun getLatestBlocks(limit: Int): Flow<List<BlockSummary>> = flow {
        val blocks = blockDao.getLatestBlocks(limit)
            .map { block ->
                BlockSummary(
                    height = block.height,
                    hash = block.hash,
                    timestamp = block.timestamp,
                    transactions = block.transactionCount
                )
            }
        emit(blocks)
    }

    override fun getSyncStatus(): Flow<SyncStatus> = flow {
        // TODO: Implement sync status check
        emit(SyncStatus.SYNCED)
    }

    override fun getStakingAmount(): Flow<Double> = flow {
        // TODO: Implement staking amount from stake repository
        emit(0.0)
    }

    override fun getValidatorStatus(): Flow<String> = flow {
        // TODO: Implement validator status
        emit("INACTIVE")
    }

    override suspend fun refreshDashboard() {
        // Trigger data refresh
        blockDao.getAllBlocks() // Force DB refresh
    }
}
