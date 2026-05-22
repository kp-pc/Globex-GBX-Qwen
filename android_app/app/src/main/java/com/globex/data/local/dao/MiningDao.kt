package com.globex.wallet.data.local.dao

import androidx.room.*
import com.globex.wallet.domain.model.MiningStats
import kotlinx.coroutines.flow.Flow

@Dao
interface MiningDao {
    
    @Query("SELECT * FROM mining_stats WHERE wallet_id = :walletId")
    fun getMiningStatsByWallet(walletId: String): Flow<MiningStats?>
    
    @Query("SELECT * FROM mining_stats ORDER BY last_updated DESC LIMIT 1")
    suspend fun getLatestMiningStats(): MiningStats?
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertMiningStats(stats: MiningStats)
    
    @Update
    suspend fun updateMiningStats(stats: MiningStats)
    
    @Delete
    suspend fun deleteMiningStats(stats: MiningStats)
    
    @Query("UPDATE mining_stats SET is_mining = :isMining WHERE wallet_id = :walletId")
    suspend fun updateMiningStatus(walletId: String, isMining: Boolean)
}
