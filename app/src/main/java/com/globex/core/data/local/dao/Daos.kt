package com.globex.core.data.local.dao

import androidx.room.*
import kotlinx.coroutines.flow.Flow
import com.globex.core.data.local.*

/**
 * DAO for Wallet operations
 */
@Dao
interface WalletDao {
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(wallet: WalletEntity)
    
    @Update
    suspend fun update(wallet: WalletEntity)
    
    @Delete
    suspend fun delete(wallet: WalletEntity)
    
    @Query("SELECT * FROM wallets WHERE address = :address")
    suspend fun getByAddress(address: String): WalletEntity?
    
    @Query("SELECT * FROM wallets WHERE address LIKE '%' || :query || '%'")
    fun search(query: String): Flow<List<WalletEntity>>
    
    @Query("SELECT * FROM wallets ORDER BY createdAt DESC LIMIT :limit OFFSET :offset")
    fun getAll(limit: Int = 20, offset: Int = 0): Flow<List<WalletEntity>>
    
    @Query("SELECT COUNT(*) FROM wallets")
    fun getCount(): Flow<Int>

    @Query("SELECT * FROM wallets WHERE isActive = 1 LIMIT 1")
    suspend fun getActiveWallet(): WalletEntity?
}

/**
 * DAO for Transaction operations
 */
@Dao
interface TransactionDao {
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(transaction: TransactionEntity)
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(transactions: List<TransactionEntity>)
    
    @Update
    suspend fun update(transaction: TransactionEntity)
    
    @Delete
    suspend fun delete(transaction: TransactionEntity)
    
    @Query("SELECT * FROM transactions WHERE id = :id")
    suspend fun getById(id: String): TransactionEntity?
    
    @Query("SELECT * FROM transactions WHERE fromAddress = :address OR toAddress = :address ORDER BY timestamp DESC")
    fun getByAddress(address: String): Flow<List<TransactionEntity>>
    
    @Query("SELECT * FROM transactions WHERE blockHash = :blockHash")
    fun getByBlockHash(blockHash: String): Flow<List<TransactionEntity>>
    
    @Query("SELECT * FROM transactions WHERE status = :status ORDER BY timestamp DESC")
    fun getByStatus(status: String): Flow<List<TransactionEntity>>
    
    @Query("SELECT * FROM transactions WHERE (fromAddress LIKE '%' || :query || '%' OR toAddress LIKE '%' || :query || '%') ORDER BY timestamp DESC")
    fun search(query: String): Flow<List<TransactionEntity>>
    
    @Query("SELECT * FROM transactions ORDER BY timestamp DESC LIMIT :limit OFFSET :offset")
    fun getAll(limit: Int = 20, offset: Int = 0): Flow<List<TransactionEntity>>
    
    @Query("SELECT COUNT(*) FROM transactions")
    fun getCount(): Flow<Int>
}

/**
 * DAO for Block operations
 */
@Dao
interface BlockDao {
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(block: BlockEntity)
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(blocks: List<BlockEntity>)
    
    @Update
    suspend fun update(block: BlockEntity)
    
    @Delete
    suspend fun delete(block: BlockEntity)
    
    @Query("SELECT * FROM blocks WHERE hash = :hash")
    suspend fun getByHash(hash: String): BlockEntity?
    
    @Query("SELECT * FROM blocks WHERE height = :height")
    suspend fun getByHeight(height: Long): BlockEntity?
    
    @Query("SELECT * FROM blocks ORDER BY height DESC LIMIT :limit OFFSET :offset")
    fun getLatest(limit: Int = 20, offset: Int = 0): Flow<List<BlockEntity>>
    
    @Query("SELECT * FROM blocks WHERE miner LIKE '%' || :query || '%' ORDER BY height DESC")
    fun searchByMiner(query: String): Flow<List<BlockEntity>>
    
    @Query("SELECT * FROM blocks ORDER BY height DESC LIMIT :limit OFFSET :offset")
    fun getAll(limit: Int = 20, offset: Int = 0): Flow<List<BlockEntity>>
    
    @Query("SELECT COUNT(*) FROM blocks")
    fun getCount(): Flow<Int>
    
    @Query("SELECT MAX(height) FROM blocks")
    fun getMaxHeight(): Flow<Long?>

    @Query("SELECT * FROM blocks ORDER BY height DESC LIMIT :limit")
    suspend fun getLatestBlocks(limit: Int = 10): List<BlockEntity>

    @Query("SELECT * FROM blocks ORDER BY height DESC")
    suspend fun getAllBlocks(): List<BlockEntity>
}

/**
 * DAO for Node operations
 */
@Dao
interface NodeDao {
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(node: NodeEntity)
    
    @Update
    suspend fun update(node: NodeEntity)
    
    @Delete
    suspend fun delete(node: NodeEntity)
    
    @Query("SELECT * FROM nodes WHERE id = :id")
    suspend fun getById(id: String): NodeEntity?
    
    @Query("SELECT * FROM nodes WHERE url LIKE '%' || :query || '%'")
    fun search(query: String): Flow<List<NodeEntity>>
    
    @Query("SELECT * FROM nodes WHERE status = :status")
    fun getByStatus(status: String): Flow<List<NodeEntity>>
    
    @Query("SELECT * FROM nodes WHERE isTrusted = 1")
    fun getTrustedNodes(): Flow<List<NodeEntity>>
    
    @Query("SELECT * FROM nodes ORDER BY lastSeen DESC LIMIT :limit OFFSET :offset")
    fun getAll(limit: Int = 20, offset: Int = 0): Flow<List<NodeEntity>>
    
    @Query("SELECT COUNT(*) FROM nodes")
    fun getCount(): Flow<Int>
}

/**
 * DAO for Mining Session operations
 */
@Dao
interface MiningDao {
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(session: MiningEntity)
    
    @Update
    suspend fun update(session: MiningEntity)
    
    @Delete
    suspend fun delete(session: MiningEntity)
    
    @Query("SELECT * FROM mining_sessions WHERE id = :id")
    suspend fun getById(id: String): MiningEntity?
    
    @Query("SELECT * FROM mining_sessions WHERE isActive = 1")
    fun getActiveSession(): Flow<MiningEntity?>
    
    @Query("SELECT * FROM mining_sessions ORDER BY startTime DESC LIMIT :limit OFFSET :offset")
    fun getHistory(limit: Int = 20, offset: Int = 0): Flow<List<MiningEntity>>
    
    @Query("SELECT SUM(totalRewards) FROM mining_sessions")
    fun getTotalRewards(): Flow<Long?>
    
    @Query("SELECT AVG(hashRate) FROM mining_sessions WHERE startTime > :startTime")
    fun getAverageHashRate(startTime: Long): Flow<Double?>
}

/**
 * DAO for Validator operations
 */
@Dao
interface ValidatorDao {
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(validator: ValidatorEntity)
    
    @Update
    suspend fun update(validator: ValidatorEntity)
    
    @Delete
    suspend fun delete(validator: ValidatorEntity)
    
    @Query("SELECT * FROM validators WHERE address = :address")
    suspend fun getByAddress(address: String): ValidatorEntity?
    
    @Query("SELECT * FROM validators WHERE isActive = 1")
    fun getActiveValidators(): Flow<List<ValidatorEntity>>
    
    @Query("SELECT * FROM validators ORDER BY stakeAmount DESC LIMIT :limit OFFSET :offset")
    fun getAll(limit: Int = 20, offset: Int = 0): Flow<List<ValidatorEntity>>
    
    @Query("SELECT * FROM validators WHERE address LIKE '%' || :query || '%'")
    fun search(query: String): Flow<List<ValidatorEntity>>
    
    @Query("SELECT COUNT(*) FROM validators")
    fun getCount(): Flow<Int>
}

/**
 * DAO for Fund operations
 */
@Dao
interface FundDao {
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(fund: FundEntity)
    
    @Update
    suspend fun update(fund: FundEntity)
    
    @Delete
    suspend fun delete(fund: FundEntity)
    
    @Query("SELECT * FROM funds WHERE address = :address")
    suspend fun getByAddress(address: String): FundEntity?
    
    @Query("SELECT * FROM funds LIMIT 1")
    fun getCurrentFund(): Flow<FundEntity?>
    
    @Query("SELECT * FROM funds ORDER BY balance DESC LIMIT :limit OFFSET :offset")
    fun getAll(limit: Int = 20, offset: Int = 0): Flow<List<FundEntity>>
}
