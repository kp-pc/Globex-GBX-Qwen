package com.globex.wallet.data.local.dao

import androidx.room.*
import com.globex.wallet.domain.model.Transaction
import kotlinx.coroutines.flow.Flow

@Dao
interface TransactionDao {
    
    @Query("SELECT * FROM transactions WHERE wallet_id = :walletId ORDER BY timestamp DESC")
    fun getTransactionsByWallet(walletId: String): Flow<List<Transaction>>
    
    @Query("SELECT * FROM transactions WHERE id = :transactionId")
    suspend fun getTransactionById(transactionId: String): Transaction?
    
    @Query("SELECT * FROM transactions WHERE wallet_id = :walletId AND type = :type ORDER BY timestamp DESC")
    fun getTransactionsByType(walletId: String, type: String): Flow<List<Transaction>>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertTransaction(transaction: Transaction)
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertTransactions(transactions: List<Transaction>)
    
    @Update
    suspend fun updateTransaction(transaction: Transaction)
    
    @Delete
    suspend fun deleteTransaction(transaction: Transaction)
    
    @Query("DELETE FROM transactions WHERE wallet_id = :walletId")
    suspend fun deleteAllTransactions(walletId: String)
}
