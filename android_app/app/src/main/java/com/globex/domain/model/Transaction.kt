package com.globex.wallet.domain.model

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.math.BigDecimal
import java.util.Date

@Entity(tableName = "transactions")
data class Transaction(
    @PrimaryKey
    val id: String,
    val walletId: String,
    val type: String, // SEND, RECEIVE, STAKE, UNSTAKE, MINING_REWARD
    val amount: BigDecimal,
    val fee: BigDecimal = BigDecimal.ZERO,
    val fromAddress: String?,
    val toAddress: String?,
    val txHash: String?,
    val status: String = "PENDING", // PENDING, CONFIRMED, FAILED
    val timestamp: Date = Date(),
    val blockHeight: Long? = null,
    val confirmations: Int = 0,
    val memo: String? = null
)
