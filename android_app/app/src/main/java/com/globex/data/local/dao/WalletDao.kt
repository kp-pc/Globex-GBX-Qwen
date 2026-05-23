package com.globex.wallet.data.local.dao

import androidx.room.*
import com.globex.wallet.domain.model.Wallet
import kotlinx.coroutines.flow.Flow

@Dao
interface WalletDao {
    
    @Query("SELECT * FROM wallets")
    fun getAllWallets(): Flow<List<Wallet>>
    
    @Query("SELECT * FROM wallets WHERE id = :walletId")
    suspend fun getWalletById(walletId: String): Wallet?
    
    @Query("SELECT * FROM wallets WHERE is_active = 1 LIMIT 1")
    fun getActiveWallet(): Flow<Wallet?>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertWallet(wallet: Wallet)
    
    @Update
    suspend fun updateWallet(wallet: Wallet)
    
    @Delete
    suspend fun deleteWallet(wallet: Wallet)
    
    @Query("UPDATE wallets SET is_active = 0")
    suspend fun deactivateAllWallets()
}
