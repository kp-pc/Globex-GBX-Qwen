package com.globex.core.data.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/**
 * DTOs for GET /chain endpoint
 */
@Serializable
data class ChainResponse(
    @SerialName("chain") val chain: List<BlockDto>,
    @SerialName("length") val length: Int
)

@Serializable
data class BlockDto(
    @SerialName("height") val height: Long,
    @SerialName("hash") val hash: String,
    @SerialName("previousHash") val previousHash: String,
    @SerialName("timestamp") val timestamp: Long,
    @SerialName("nonce") val nonce: Long,
    @SerialName("difficulty") val difficulty: Long,
    @SerialName("merkleRoot") val merkleRoot: String,
    @SerialName("transactions") val transactions: List<TransactionDto> = emptyList(),
    @SerialName("miner") val miner: String? = null
)

/**
 * DTOs for POST /mine endpoint
 */
@Serializable
data class MineRequest(
    @SerialName("minerAddress") val minerAddress: String
)

@Serializable
data class MineResponse(
    @SerialName("success") val success: Boolean,
    @SerialName("block") val block: BlockDto?,
    @SerialName("reward") val reward: Long,
    @SerialName("message") val message: String? = null
)

/**
 * DTOs for POST /transactions/new endpoint
 */
@Serializable
data class TransactionRequest(
    @SerialName("fromAddress") val fromAddress: String,
    @SerialName("toAddress") val toAddress: String,
    @SerialName("amount") val amount: Long,
    @SerialName("fee") val fee: Long = 0,
    @SerialName("signature") val signature: String,
    @SerialName("publicKey") val publicKey: String,
    @SerialName("memo") val memo: String? = null
)

@Serializable
data class TransactionResponse(
    @SerialName("success") val success: Boolean,
    @SerialName("transactionId") val transactionId: String?,
    @SerialName("transaction") val transaction: TransactionDto?,
    @SerialName("message") val message: String? = null
)

@Serializable
data class TransactionDto(
    @SerialName("id") val id: String,
    @SerialName("fromAddress") val fromAddress: String,
    @SerialName("toAddress") val toAddress: String,
    @SerialName("amount") val amount: Long,
    @SerialName("fee") val fee: Long = 0,
    @SerialName("timestamp") val timestamp: Long,
    @SerialName("signature") val signature: String,
    @SerialName("memo") val memo: String? = null
)

/**
 * DTOs for POST /nodes/register endpoint
 */
@Serializable
data class NodeRegisterRequest(
    @SerialName("url") val url: String,
    @SerialName("nodeId") val nodeId: String? = null
)

@Serializable
data class NodeRegisterResponse(
    @SerialName("success") val success: Boolean,
    @SerialName("node") val node: NodeDto?,
    @SerialName("message") val message: String? = null
)

@Serializable
data class NodeDto(
    @SerialName("id") val id: String,
    @SerialName("url") val url: String,
    @SerialName("height") val height: Long = 0,
    @SerialName("status") val status: String = "unknown"
)

/**
 * DTOs for GET /nodes/resolve endpoint
 */
@Serializable
data class NodesResolveResponse(
    @SerialName("success") val success: Boolean,
    @SerialName("chain") val chain: List<BlockDto>?,
    @SerialName("replaced") val replaced: Boolean,
    @SerialName("message") val message: String? = null
)

/**
 * Generic API response wrapper
 */
@Serializable
data class ApiResponse<T>(
    @SerialName("success") val success: Boolean,
    @SerialName("data") val data: T?,
    @SerialName("error") val error: String? = null,
    @SerialName("code") val code: Int? = null
)

/**
 * Error response DTO
 */
@Serializable
data class ErrorResponse(
    @SerialName("error") val error: String,
    @SerialName("message") val message: String,
    @SerialName("code") val code: Int? = null
)
