package com.globex.core.presentation.security

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * PIN protection manager with encrypted storage
 */
class PinProtectionManager(private val context: Context) {
    
    private val masterKey by lazy {
        MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()
    }
    
    private val sharedPreferences: SharedPreferences by lazy {
        EncryptedSharedPreferences.create(
            context,
            "globex_pin_prefs",
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    }
    
    private val _isPinSet = MutableStateFlow(false)
    val isPinSet: Flow<Boolean> = _isPinSet.asStateFlow()
    
    private val _isAppLocked = MutableStateFlow(false)
    val isAppLocked: Flow<Boolean> = _isAppLocked.asStateFlow()
    
    companion object {
        private const val KEY_PIN_HASH = "pin_hash"
        private const val KEY_PIN_SALT = "pin_salt"
        private const val KEY_IS_LOCKED = "is_app_locked"
        private const val KEY_LOCK_TIMEOUT = "lock_timeout"
        private const val DEFAULT_LOCK_TIMEOUT = 30000L // 30 seconds
    }
    
    init {
        _isPinSet.value = hasPin()
        _isAppLocked.value = isAppLockEnabled()
    }
    
    /**
     * Set a new PIN
     */
    fun setPin(pin: String): Result<Unit> {
        return try {
            if (!isValidPin(pin)) {
                return Result.failure(Exception("Invalid PIN format"))
            }
            
            val salt = generateSalt()
            val hashedPin = hashPin(pin, salt)
            
            sharedPreferences.edit().apply {
                putString(KEY_PIN_HASH, hashedPin)
                putString(KEY_PIN_SALT, salt)
            }.apply()
            
            _isPinSet.value = true
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Verify PIN
     */
    fun verifyPin(pin: String): Boolean {
        if (!hasPin()) return false
        
        val storedHash = sharedPreferences.getString(KEY_PIN_HASH, null) ?: return false
        val storedSalt = sharedPreferences.getString(KEY_PIN_SALT, null) ?: return false
        
        val hashedPin = hashPin(pin, storedSalt)
        return hashedPin == storedHash
    }
    
    /**
     * Check if PIN is set
     */
    fun hasPin(): Boolean {
        return sharedPreferences.contains(KEY_PIN_HASH)
    }
    
    /**
     * Remove PIN
     */
    fun removePin(): Boolean {
        return try {
            sharedPreferences.edit().remove(KEY_PIN_HASH).remove(KEY_PIN_SALT).apply()
            _isPinSet.value = false
            true
        } catch (e: Exception) {
            false
        }
    }
    
    /**
     * Enable app lock
     */
    fun enableAppLock(): Boolean {
        return try {
            sharedPreferences.edit().putBoolean(KEY_IS_LOCKED, true).apply()
            _isAppLocked.value = true
            true
        } catch (e: Exception) {
            false
        }
    }
    
    /**
     * Disable app lock
     */
    fun disableAppLock(): Boolean {
        return try {
            sharedPreferences.edit().putBoolean(KEY_IS_LOCKED, false).apply()
            _isAppLocked.value = false
            true
        } catch (e: Exception) {
            false
        }
    }
    
    /**
     * Check if app lock is enabled
     */
    fun isAppLockEnabled(): Boolean {
        return sharedPreferences.getBoolean(KEY_IS_LOCKED, false)
    }
    
    /**
     * Set lock timeout
     */
    fun setLockTimeout(timeoutMs: Long): Boolean {
        return try {
            sharedPreferences.edit().putLong(KEY_LOCK_TIMEOUT, timeoutMs).apply()
            true
        } catch (e: Exception) {
            false
        }
    }
    
    /**
     * Get lock timeout
     */
    fun getLockTimeout(): Long {
        return sharedPreferences.getLong(KEY_LOCK_TIMEOUT, DEFAULT_LOCK_TIMEOUT)
    }
    
    /**
     * Validate PIN format
     */
    private fun isValidPin(pin: String): Boolean {
        // PIN should be 4-8 digits
        return pin.length in 4..8 && pin.all { it.isDigit() }
    }
    
    /**
     * Generate random salt
     */
    private fun generateSalt(): String {
        val bytes = ByteArray(16)
        java.security.SecureRandom().nextBytes(bytes)
        return bytes.joinToString("") { "%02x".format(it) }
    }
    
    /**
     * Hash PIN with salt using SHA-256
     */
    private fun hashPin(pin: String, salt: String): String {
        val digest = java.security.MessageDigest.getInstance("SHA-256")
        val combined = (pin + salt).toByteArray(Charsets.UTF_8)
        val hashed = digest.digest(combined)
        return hashed.joinToString("") { "%02x".format(it) }
    }
    
    /**
     * Change PIN
     */
    fun changePin(oldPin: String, newPin: String): Result<Unit> {
        return if (verifyPin(oldPin)) {
            setPin(newPin)
        } else {
            Result.failure(Exception("Current PIN is incorrect"))
        }
    }
}
