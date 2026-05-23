package com.globex.feature_wallet.util

import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import java.security.KeyPairGenerator
import java.security.KeyStore
import java.security.PrivateKey
import java.security.PublicKey
import javax.crypto.Cipher

/**
 * Secure wallet key generator using Android Keystore
 */
class WalletKeyGenerator {
    
    private val keyStore: KeyStore = KeyStore.getInstance("AndroidKeyStore").apply {
        load(null)
    }
    
    companion object {
        private const val KEY_ALIAS = "globex_wallet_key"
        private const val TRANSFORMATION = "EC/ECB/PKCS1Padding"
    }
    
    /**
     * Generate ECDSA SECP256k1 key pair in Android Keystore
     */
    fun generateKeyPair(): Boolean {
        return try {
            if (keyStore.containsAlias(KEY_ALIAS)) {
                deleteKey()
            }
            
            val keyPairGenerator = KeyPairGenerator.getInstance(
                KeyProperties.KEY_ALGORITHM_EC,
                "AndroidKeyStore"
            )
            
            val parameterSpec = KeyGenParameterSpec.Builder(
                KEY_ALIAS,
                KeyProperties.PURPOSE_SIGN or KeyProperties.PURPOSE_VERIFY
            )
                .setAlgorithmParameterSpec(
                    java.security.spec.ECGenParameterSpec("secp256k1")
                )
                .setUserAuthenticationRequired(false)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_PKCS1)
                .build()
            
            keyPairGenerator.initialize(parameterSpec)
            keyPairGenerator.generateKeyPair()
            true
        } catch (e: Exception) {
            e.printStackTrace()
            false
        }
    }
    
    /**
     * Get private key from keystore
     */
    fun getPrivateKey(): PrivateKey? {
        return keyStore.getKey(KEY_ALIAS, null) as? PrivateKey
    }
    
    /**
     * Get public key from keystore
     */
    fun getPublicKey(): PublicKey? {
        val entry = keyStore.getEntry(KEY_ALIAS, null) as? KeyStore.PrivateKeyEntry
        return entry?.certificate?.publicKey
    }
    
    /**
     * Check if key exists
     */
    fun keyExists(): Boolean {
        return keyStore.containsAlias(KEY_ALIAS)
    }
    
    /**
     * Delete key from keystore
     */
    fun deleteKey() {
        keyStore.deleteEntry(KEY_ALIAS)
    }
    
    /**
     * Get cipher for signing
     */
    fun getCipherForSigning(): Cipher? {
        return try {
            Cipher.getInstance(TRANSFORMATION).apply {
                init(Cipher.PRIVATE_KEY, getPrivateKey())
            }
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }
}
