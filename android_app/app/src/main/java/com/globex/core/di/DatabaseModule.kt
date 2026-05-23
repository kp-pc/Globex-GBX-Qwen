package com.globex.wallet.core.di

import android.content.Context
import androidx.room.Room
import com.globex.wallet.data.local.database.GlobexDatabase
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideGlobexDatabase(
        @ApplicationContext context: Context
    ): GlobexDatabase {
        return Room.databaseBuilder(
            context,
            GlobexDatabase::class.java,
            "globex_database"
        )
            .fallbackToDestructiveMigration()
            .build()
    }

    @Provides
    @Singleton
    fun provideWalletDao(database: GlobexDatabase) = database.walletDao()

    @Provides
    @Singleton
    fun provideTransactionDao(database: GlobexDatabase) = database.transactionDao()

    @Provides
    @Singleton
    fun provideMiningDao(database: GlobexDatabase) = database.miningDao()
}
