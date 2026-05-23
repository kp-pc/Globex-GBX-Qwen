package com.globex.wallet.data.local.database

import androidx.room.*
import com.globex.wallet.domain.model.Wallet
import com.globex.wallet.domain.model.Transaction
import com.globex.wallet.domain.model.MiningStats

@Database(
    entities = [
        Wallet::class,
        Transaction::class,
        MiningStats::class
    ],
    version = 1,
    exportSchema = false
)
@TypeConverters(Converters::class)
abstract class GlobexDatabase : RoomDatabase() {
    
    abstract fun walletDao(): WalletDao
    abstract fun transactionDao(): TransactionDao
    abstract fun miningDao(): MiningDao
    
    companion object {
        const val DATABASE_NAME = "globex_db"
    }
}
