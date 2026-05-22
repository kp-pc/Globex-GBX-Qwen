package com.globex.feature_wallet.util

import java.security.MessageDigest
import kotlin.experimental.and

/**
 * SHA256 hashing utility
 */
object Sha256Hash {
    
    fun hash(data: ByteArray): ByteArray {
        val digest = MessageDigest.getInstance("SHA-256")
        return digest.digest(data)
    }
    
    fun hash(data: String): ByteArray {
        return hash(data.toByteArray(Charsets.UTF_8))
    }
    
    fun hashTwice(data: ByteArray): ByteArray {
        return hash(hash(data))
    }
    
    fun hashTwice(data: String): ByteArray {
        return hashTwice(data.toByteArray(Charsets.UTF_8))
    }
    
    fun toHexString(bytes: ByteArray): String {
        return bytes.joinToString("") { "%02x".format(it) }
    }
}

/**
 * RIPEMD160 hashing utility
 */
object Ripemd160Hash {
    
    fun hash(data: ByteArray): ByteArray {
        val digest = org.bouncycastle.jcajce.provider.digest.RIPEMD160.Digest()
        return digest.digest(data)
    }
    
    fun hash(data: String): ByteArray {
        return hash(data.toByteArray(Charsets.UTF_8))
    }
}

/**
 * Base58 encoding/decoding utility
 */
object Base58 {
    
    private const val ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    private val ENCODED = ALPHABET.toCharArray()
    
    fun encode(input: ByteArray): String {
        if (input.isEmpty()) return ""
        
        // Count leading zeros
        var zeros = 0
        while (zeros < input.size && input[zeros] == 0.toByte()) {
            zeros++
        }
        
        // Convert base-256 to base-58
        val size = ((input.size - zeros) * 1.38).toInt() + 1
        val encoded = ByteArray(size)
        var start = encoded.size - 1
        
        for (byte in input) {
            if (byte == 0.toByte() && start < encoded.size - 1) continue
            
            var carry = (byte and 0xFF).toInt()
            var i = encoded.size - 1
            
            while (carry != 0 || i > start) {
                carry += 256 * encoded[i].toInt()
                encoded[i] = (carry % 58).toByte()
                carry /= 58
                i--
            }
            start = i
        }
        
        // Build result string
        val result = StringBuilder()
        
        // Add leading '1's for each leading zero byte
        for (i in 0 until zeros) {
            result.append('1')
        }
        
        // Add encoded characters
        for (i in start until encoded.size) {
            result.append(ENCODED[encoded[i].toInt()])
        }
        
        return result.toString()
    }
    
    fun decode(input: String): ByteArray {
        if (input.isEmpty()) return byteArrayOf()
        
        // Count leading '1's
        var zeros = 0
        while (zeros < input.length && input[zeros] == '1') {
            zeros++
        }
        
        // Convert base-58 to base-256
        val size = ((input.length - zeros) * 0.733).toInt() + zeros + 1
        val decoded = ByteArray(size)
        var start = decoded.size - 1
        
        for (char in input) {
            if (char == '1' && start < decoded.size - 1) continue
            
            val charIndex = ALPHABET.indexOf(char)
            if (charIndex < 0) throw IllegalArgumentException("Invalid Base58 character: $char")
            
            var carry = charIndex
            var i = decoded.size - 1
            
            while (carry != 0 || i > start) {
                carry += 58 * decoded[i].toInt()
                decoded[i] = (carry % 256).toByte()
                carry /= 256
                i--
            }
            start = i
        }
        
        // Return result without leading zeros (except those from leading '1's)
        val result = ByteArray(zeros + (decoded.size - start))
        System.arraycopy(decoded, start, result, zeros, decoded.size - start)
        
        return result
    }
}
