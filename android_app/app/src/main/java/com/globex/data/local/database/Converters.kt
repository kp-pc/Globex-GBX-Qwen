package com.globex.wallet.data.local.database

import androidx.room.TypeConverter
import java.math.BigDecimal
import java.util.Date

class Converters {
    
    @TypeConverter
    fun fromBigDecimal(value: BigDecimal): String {
        return value.toPlainString()
    }
    
    @TypeConverter
    fun toBigDecimal(value: String): BigDecimal {
        return BigDecimal(value)
    }
    
    @TypeConverter
    fun fromDate(date: Date?): Long? {
        return date?.time
    }
    
    @TypeConverter
    fun toDate(timestamp: Long?): Date? {
        return timestamp?.let { Date(it) }
    }
}
