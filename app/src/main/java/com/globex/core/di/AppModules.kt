package com.globex.core.di

import android.content.Context
import androidx.room.Room
import com.globex.core.data.api.GlobexApi
import com.globex.core.data.local.AppDatabase
import com.globex.core.data.local.dao.*
import com.globex.core.data.network.NetworkModule
import com.globex.core.data.repository.*
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

/**
 * Hilt module for database dependencies
 */
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideAppDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            AppDatabase.DATABASE_NAME
        )
            .fallbackToDestructiveMigration()
            .build()
    }

    @Provides
    @Singleton
    fun provideWalletDao(database: AppDatabase): WalletDao {
        return database.walletDao()
    }

    @Provides
    @Singleton
    fun provideTransactionDao(database: AppDatabase): TransactionDao {
        return database.transactionDao()
    }

    @Provides
    @Singleton
    fun provideBlockDao(database: AppDatabase): BlockDao {
        return database.blockDao()
    }

    @Provides
    @Singleton
    fun provideNodeDao(database: AppDatabase): NodeDao {
        return database.nodeDao()
    }

    @Provides
    @Singleton
    fun provideMiningDao(database: AppDatabase): MiningDao {
        return database.miningDao()
    }

    @Provides
    @Singleton
    fun provideValidatorDao(database: AppDatabase): ValidatorDao {
        return database.validatorDao()
    }

    @Provides
    @Singleton
    fun provideFundDao(database: AppDatabase): FundDao {
        return database.fundDao()
    }
}

/**
 * Hilt module for network dependencies
 */
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideGlobexApi(): GlobexApi {
        return com.globex.core.data.network.NetworkModule.apiService
    }
}

/**
 * Hilt module for repository dependencies
 */
@Module
@InstallIn(SingletonComponent::class)
object RepositoryModule {

    @Provides
    @Singleton
    fun provideWalletRepository(api: GlobexApi): WalletRepository {
        return WalletRepository(api)
    }

    @Provides
    @Singleton
    fun provideMiningRepository(api: GlobexApi): MiningRepository {
        return MiningRepository(api)
    }

    @Provides
    @Singleton
    fun provideNodeRepository(api: GlobexApi): NodeRepository {
        return NodeRepository(api)
    }

    @Provides
    @Singleton
    fun provideExplorerRepository(api: GlobexApi): ExplorerRepository {
        return ExplorerRepository(api)
    }

    @Provides
    @Singleton
    fun provideStakeRepository(api: GlobexApi): StakeRepository {
        return StakeRepository(api)
    }

    @Provides
    @Singleton
    fun provideFundRepository(api: GlobexApi): FundRepository {
        return FundRepository(api)
    }
}

/**
 * Hilt module for security dependencies
 */
@Module
@InstallIn(SingletonComponent::class)
object SecurityModule {

    @Provides
    @Singleton
    fun provideEncryptedSharedPreferences(@ApplicationContext context: Context): android.content.SharedPreferences {
        val masterKey = androidx.security.crypto.MasterKey.Builder(context)
            .setKeyScheme(androidx.security.crypto.MasterKey.KeyScheme.AES256_GCM)
            .build()

        return androidx.security.crypto.EncryptedSharedPreferences.create(
            context,
            "globex_secure_prefs",
            masterKey,
            androidx.security.crypto.EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            androidx.security.crypto.EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    }
}

/**
 * Hilt module for ViewModel dependencies (for assisted injection if needed)
 */
@Module
@InstallIn(SingletonComponent::class)
object ViewModelModule {

    // Add any ViewModel-specific dependencies here if needed
    // Most ViewModels will be injected automatically via @HiltViewModel
}
