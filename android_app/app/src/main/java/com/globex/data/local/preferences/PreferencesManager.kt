package com.globex.wallet.data.local.preferences

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.*
import androidx.datastore.preferences.preferencesDataStore
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.map
import java.io.IOException
import javax.inject.Inject
import javax.inject.Singleton

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "globex_prefs")

@Singleton
class PreferencesManager @Inject constructor(
    @ApplicationContext private val context: Context
) {
    
    companion object {
        val WALLET_ADDRESS = stringPreferencesKey("wallet_address")
        val IS_LOGGED_IN = booleanPreferencesKey("is_logged_in")
        val BIOMETRIC_ENABLED = booleanPreferencesKey("biometric_enabled")
        val NOTIFICATIONS_ENABLED = booleanPreferencesKey("notifications_enabled")
        val THEME_MODE = stringPreferencesKey("theme_mode") // LIGHT, DARK, SYSTEM
        val CURRENCY = stringPreferencesKey("currency")
        val LANGUAGE = stringPreferencesKey("language")
        val MINING_ENABLED = booleanPreferencesKey("mining_enabled")
        val AUTO_SYNC_ENABLED = booleanPreferencesKey("auto_sync_enabled")
    }
    
    private val dataStore = context.dataStore
    
    val walletAddressFlow: Flow<String?> = dataStore.data
        .catch { exception ->
            if (exception is IOException) {
                emit(emptyPreferences())
            } else {
                throw exception
            }
        }
        .map { preferences ->
            preferences[WALLET_ADDRESS]
        }
    
    val isLoggedInFlow: Flow<Boolean> = dataStore.data
        .catch { exception ->
            if (exception is IOException) {
                emit(emptyPreferences())
            } else {
                throw exception
            }
        }
        .map { preferences ->
            preferences[IS_LOGGED_IN] ?: false
        }
    
    val biometricEnabledFlow: Flow<Boolean> = dataStore.data
        .map { preferences ->
            preferences[BIOMETRIC_ENABLED] ?: false
        }
    
    suspend fun saveWalletAddress(address: String) {
        dataStore.edit { preferences ->
            preferences[WALLET_ADDRESS] = address
        }
    }
    
    suspend fun setLoggedIn(isLoggedIn: Boolean) {
        dataStore.edit { preferences ->
            preferences[IS_LOGGED_IN] = isLoggedIn
        }
    }
    
    suspend fun setBiometricEnabled(enabled: Boolean) {
        dataStore.edit { preferences ->
            preferences[BIOMETRIC_ENABLED] = enabled
        }
    }
    
    suspend fun setThemeMode(mode: String) {
        dataStore.edit { preferences ->
            preferences[THEME_MODE] = mode
        }
    }
    
    suspend fun clearAllPreferences() {
        dataStore.edit { preferences ->
            preferences.clear()
        }
    }
}
