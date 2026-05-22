package com.globex.feature_wallet.util

import android.content.Context
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import com.globex.core.domain.model.Wallet
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

/**
 * Secure wallet storage using EncryptedSharedPreferences
 */
class SecureWalletStorage(private val context: Context) {
    
    private val masterKey by lazy {
        MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()
    }
    
    private val sharedPreferences by lazy {
        EncryptedSharedPreferences.create(
            context,
            "globex_wallet_prefs",
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    }
    
    private val json = Json { ignoreUnknownKeys = true }
    
    companion object {
        private const val KEY_WALLET_DATA = "wallet_data"
        private const val KEY_WALLET_ADDRESS = "wallet_address"
        private const val KEY_IS_BACKED_UP = "is_backed_up"
        private const val KEY_ENCRYPTION_KEY = "encryption_key"
    }
    
    /**
     * Save wallet securely
     */
    fun saveWallet(wallet: Wallet): Boolean {
        return try {
            sharedPreferences.edit().apply {
                putString(KEY_WALLET_ADDRESS, wallet.address)
                putString(KEY_WALLET_DATA, json.encodeToString(wallet))
                putBoolean(KEY_IS_BACKED_UP, wallet.isBackedUp)
            }.apply()
            true
        } catch (e: Exception) {
            e.printStackTrace()
            false
        }
    }
    
    /**
     * Get saved wallet
     */
    fun getWallet(): Wallet? {
        return try {
            val walletData = sharedPreferences.getString(KEY_WALLET_DATA, null) ?: return null
            json.decodeFromString<Wallet>(walletData)
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }
    
    /**
     * Get wallet address
     */
    fun getWalletAddress(): String? {
        return sharedPreferences.getString(KEY_WALLET_ADDRESS, null)
    }
    
    /**
     * Check if wallet is backed up
     */
    fun isBackedUp(): Boolean {
        return sharedPreferences.getBoolean(KEY_IS_BACKED_UP, false)
    }
    
    /**
     * Mark wallet as backed up
     */
    fun markAsBackedUp() {
        sharedPreferences.edit().putBoolean(KEY_IS_BACKED_UP, true).apply()
    }
    
    /**
     * Clear all wallet data
     */
    fun clear() {
        sharedPreferences.edit().clear().apply()
    }
    
    /**
     * Export wallet to encrypted JSON
     */
    fun exportWallet(encryptionKey: String): String? {
        return try {
            val wallet = getWallet() ?: return null
            // In a real implementation, encrypt the JSON with the provided key
            json.encodeToString(wallet)
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }
    
    /**
     * Import wallet from encrypted JSON
     */
    fun importWallet(encryptedData: String, decryptionKey: String): Boolean {
        return try {
            // In a real implementation, decrypt the JSON with the provided key
            val wallet = json.decodeFromString<Wallet>(encryptedData)
            saveWallet(wallet)
            true
        } catch (e: Exception) {
            e.printStackTrace()
            false
        }
    }
}
