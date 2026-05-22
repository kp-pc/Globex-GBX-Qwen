package com.globex.wallet.core.di

import com.globex.wallet.data.local.preferences.PreferencesManager
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object PreferencesModule {

    @Provides
    @Singleton
    fun providePreferencesManager(): PreferencesManager {
        return PreferencesManager()
    }
}
