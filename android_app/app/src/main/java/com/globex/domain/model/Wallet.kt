package com.globex.wallet.domain.model

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.math.BigDecimal
import java.util.Date

@Entity(tableName = "wallets")
data class Wallet(
    @PrimaryKey
    val id: String,
    val name: String,
    val address: String,
    val balance: BigDecimal,
    val stakedBalance: BigDecimal = BigDecimal.ZERO,
    val isMining: Boolean = false,
    val isActive: Boolean = true,
    val createdAt: Date = Date(),
    val lastSyncedAt: Date? = null
)
