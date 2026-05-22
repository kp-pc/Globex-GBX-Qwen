package com.globex.feature_wallet.domain.usecase

import com.globex.core.data.dto.TransactionRequest
import com.globex.core.data.repository.WalletRepository
import com.globex.core.domain.model.Transaction
import com.globex.feature_wallet.util.Sha256Hash
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

/**
 * Use case for creating a new transaction
 */
class CreateTransactionUseCase(
    private val walletRepository: WalletRepository
) {
    
    operator fun invoke(
        fromAddress: String,
        toAddress: String,
        amount: Long,
        fee: Long,
        signature: String,
        publicKey: String,
        memo: String? = null
    ): Flow<Result<Transaction>> = flow {
        // Validate inputs
        val validationError = validateTransaction(fromAddress, toAddress, amount, fee)
        if (validationError != null) {
            emit(Result.failure(Exception(validationError)))
            return@flow
        }
        
        val request = TransactionRequest(
            fromAddress = fromAddress,
            toAddress = toAddress,
            amount = amount,
            fee = fee,
            signature = signature,
            publicKey = publicKey,
            memo = memo
        )
        
        val result = walletRepository.createTransaction(request)
        emit(result)
    }
    
    /**
     * Validate transaction inputs
     */
    private fun validateTransaction(
        fromAddress: String,
        toAddress: String,
        amount: Long,
        fee: Long
    ): String? {
        if (fromAddress.isBlank()) {
            return "Sender address is required"
        }
        
        if (toAddress.isBlank()) {
            return "Recipient address is required"
        }
        
        if (fromAddress == toAddress) {
            return "Cannot send to same address"
        }
        
        if (amount <= 0) {
            return "Amount must be greater than 0"
        }
        
        if (fee < 0) {
            return "Fee cannot be negative"
        }
        
        // Validate address format (basic check)
        if (!isValidAddress(fromAddress)) {
            return "Invalid sender address format"
        }
        
        if (!isValidAddress(toAddress)) {
            return "Invalid recipient address format"
        }
        
        return null
    }
    
    /**
     * Basic address validation
     */
    private fun isValidAddress(address: String): Boolean {
        // Basic validation - should be enhanced based on actual address format
        return address.length in 26..35 && address.all { 
            it.isLetterOrDigit() || it in listOf('1', '2', '3', '4', '5', '6', '7', '8', '9') 
        }
    }
}

/**
 * Use case for generating transaction signature
 */
class SignTransactionUseCase {
    
    operator fun invoke(
        transactionData: String,
        privateKey: java.security.PrivateKey
    ): Result<String> {
        return try {
            val signature = java.security.Signature.getInstance("SHA256withECDSA")
            signature.initSign(privateKey)
            signature.update(transactionData.toByteArray(Charsets.UTF_8))
            val signatureBytes = signature.sign()
            Result.success(Sha256Hash.toHexString(signatureBytes))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

/**
 * Use case for validating transaction inputs
 */
class ValidateTransactionUseCase {
    
    operator fun invoke(
        recipientAddress: String,
        amount: Long,
        fee: Long,
        balance: Long
    ): Result<Unit> {
        val errors = mutableListOf<String>()
        
        if (recipientAddress.isBlank()) {
            errors.add("Recipient address is required")
        }
        
        if (!isValidAddress(recipientAddress)) {
            errors.add("Invalid recipient address format")
        }
        
        if (amount <= 0) {
            errors.add("Amount must be greater than 0")
        }
        
        if (fee < 0) {
            errors.add("Fee cannot be negative")
        }
        
        if (amount + fee > balance) {
            errors.add("Insufficient balance")
        }
        
        return if (errors.isEmpty()) {
            Result.success(Unit)
        } else {
            Result.failure(Exception(errors.joinToString("; ")))
        }
    }
    
    private fun isValidAddress(address: String): Boolean {
        return address.length in 26..35 && address.all { 
            it.isLetterOrDigit() || it in listOf('1', '2', '3', '4', '5', '6', '7', '8', '9') 
        }
    }
}
