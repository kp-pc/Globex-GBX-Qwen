package com.globex.core.data.local

import androidx.room.*
import com.globex.core.data.local.dao.*

/**
 * Type converters for Room database
 */
class Converters {
    
    @TypeConverter
    fun fromTimestamp(value: Long?): Long? {
        return value
    }
    
    @TypeConverter
    fun toTimestamp(value: Long?): Long? {
        return value
    }
    
    @TypeConverter
    fun fromStringList(value: List<String>): String {
        return value.joinToString(",")
    }
    
    @TypeConverter
    fun toStringList(value: String): List<String> {
        return if (value.isEmpty()) emptyList() else value.split(",").map { it.trim() }
    }
}

/**
 * AppDatabase - Main Room database for Globex
 */
@Database(
    entities = [
        WalletEntity::class,
        TransactionEntity::class,
        BlockEntity::class,
        NodeEntity::class,
        MiningEntity::class,
        ValidatorEntity::class,
        FundEntity::class
    ],
    version = 1,
    exportSchema = true
)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    
    abstract fun walletDao(): WalletDao
    abstract fun transactionDao(): TransactionDao
    abstract fun blockDao(): BlockDao
    abstract fun nodeDao(): NodeDao
    abstract fun miningDao(): MiningDao
    abstract fun validatorDao(): ValidatorDao
    abstract fun fundDao(): FundDao
    
    companion object {
        const val DATABASE_NAME = "globex_database"
    }
}

/**
 * Database migrations
 */
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(database: SupportSQLiteDatabase) {
        // Example migration: Add a new column to wallets table
        // database.execSQL("ALTER TABLE wallets ADD COLUMN isBackedUp INTEGER NOT NULL DEFAULT 0")
    }
}

val MIGRATION_2_3 = object : Migration(2, 3) {
    override fun migrate(database: SupportSQLiteDatabase) {
        // Example migration: Create a new table
        // database.execSQL("CREATE TABLE IF NOT EXISTS stakes (...)")
    }
}

/**
 * Database configuration helper
 */
object DatabaseConfig {
    const val CURRENT_VERSION = 1
    val ALL_MIGRATIONS = arrayOf(
        // Add migrations here as they are created
        // MIGRATION_1_2,
        // MIGRATION_2_3
    )
}
