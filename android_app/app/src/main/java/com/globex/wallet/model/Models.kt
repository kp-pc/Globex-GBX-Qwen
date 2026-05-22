package com.globex.wallet.model

import com.google.gson.annotations.SerializedName

/**
 * Data class representing a Wallet response from the API
 */
data class WalletResponse(
    @SerializedName("address")
    val address: String,
    @SerializedName("public_key")
    val publicKey: String,
    @SerializedName("message")
    val message: String
)

/**
 * Data class representing blockchain info
 */
data class BlockchainInfo(
    @SerializedName("height")
    val height: Int,
    @SerializedName("blocks")
    val blocks: Int,
    @SerializedName("pending_transactions")
    val pendingTransactions: Int,
    @SerializedName("difficulty")
    val difficulty: Int = 0,
    @SerializedName("hash_rate")
    val hashRate: String = "0 H/s",
    @SerializedName("total_supply")
    val totalSupply: Double = 0.0
)

/**
 * Data class representing a mining response
 */
data class MineResponse(
    @SerializedName("success")
    val success: Boolean,
    @SerializedName("block_index")
    val blockIndex: Int,
    @SerializedName("reward")
    val reward: Int,
    @SerializedName("hash")
    val hash: String,
    @SerializedName("message")
    val message: String
)

/**
 * Data class representing a transaction response
 */
data class TransactionResponse(
    @SerializedName("success")
    val success: Boolean,
    @SerializedName("tx_id")
    val txId: String,
    @SerializedName("message")
    val message: String
)

/**
 * Data class representing validation response
 */
data class ValidateResponse(
    @SerializedName("valid")
    val valid: Boolean,
    @SerializedName("message")
    val message: String
)

/**
 * Data class representing a transaction input
 */
data class TransactionInput(
    @SerializedName("txid")
    val txid: String,
    @SerializedName("vout")
    val vout: Int,
    @SerializedName("script_sig")
    val scriptSig: String,
    @SerializedName("sequence")
    val sequence: Long = 4294967295
)

/**
 * Data class representing a transaction output
 */
data class TransactionOutput(
    @SerializedName("value")
    val value: Double,
    @SerializedName("script_pub_key")
    val scriptPubKey: String,
    @SerializedName("address")
    val address: String
)

/**
 * Data class representing a full transaction
 */
data class Transaction(
    @SerializedName("txid")
    val txid: String,
    @SerializedName("version")
    val version: Int = 1,
    @SerializedName("locktime")
    val locktime: Long = 0,
    @SerializedName("inputs")
    val inputs: List<TransactionInput>,
    @SerializedName("outputs")
    val outputs: List<TransactionOutput>,
    @SerializedName("timestamp")
    val timestamp: Long,
    @SerializedName("fee")
    val fee: Double = 0.0
)

/**
 * Data class representing a block
 */
data class Block(
    @SerializedName("index")
    val index: Int,
    @SerializedName("timestamp")
    val timestamp: Long,
    @SerializedName("transactions")
    val transactions: List<Transaction>,
    @SerializedName("prev_hash")
    val prevHash: String,
    @SerializedName("nonce")
    val nonce: Long,
    @SerializedName("difficulty")
    val difficulty: Int,
    @SerializedName("merkle_root")
    val merkleRoot: String,
    @SerializedName("hash")
    val hash: String,
    @SerializedName("validator")
    val validator: String? = null,
    @SerializedName("block_reward")
    val blockReward: Double = 50.0
)

/**
 * Data class representing chain response
 */
data class ChainResponse(
    @SerializedName("chain")
    val chain: List<Block>,
    @SerializedName("length")
    val length: Int
)

/**
 * Data class representing a peer node
 */
data class PeerNode(
    @SerializedName("node_id")
    val nodeId: String,
    @SerializedName("address")
    val address: String,
    @SerializedName("port")
    val port: Int,
    @SerializedName("last_seen")
    val lastSeen: Long,
    @SerializedName("height")
    val height: Int
)

/**
 * Data class representing nodes response
 */
data class NodesResponse(
    @SerializedName("nodes")
    val nodes: List<PeerNode>,
    @SerializedName("count")
    val count: Int
)

/**
 * Data class representing development fund status
 */
data class DevFundStatus(
    @SerializedName("fund_address")
    val fundAddress: String,
    @SerializedName("total_allocated")
    val totalAllocated: Double,
    @SerializedName("total_released")
    val totalReleased: Double,
    @SerializedName("available_balance")
    val availableBalance: Double,
    @SerializedName("vesting_progress")
    val vestingProgress: Double,
    @SerializedName("proposals")
    val proposals: List<DevFundProposal>,
    @SerializedName("multisig_config")
    val multisigConfig: MultiSigConfig
)

/**
 * Data class representing a development fund proposal
 */
data class DevFundProposal(
    @SerializedName("proposal_id")
    val proposalId: String,
    @SerializedName("description")
    val description: String,
    @SerializedName("amount")
    val amount: Double,
    @SerializedName("recipient")
    val recipient: String,
    @SerializedName("status")
    val status: String,
    @SerializedName("signatures")
    val signatures: Int,
    @SerializedName("required_signatures")
    val requiredSignatures: Int,
    @SerializedName("created_at")
    val createdAt: Long
)

/**
 * Data class representing multi-sig configuration
 */
data class MultiSigConfig(
    @SerializedName("required_signatures")
    val requiredSignatures: Int,
    @SerializedName("total_signers")
    val totalSigners: Int,
    @SerializedName("signers")
    val signers: List<String>
)

/**
 * Data class representing UTXO
 */
data class UTXO(
    @SerializedName("txid")
    val txid: String,
    @SerializedName("vout")
    val vout: Int,
    @SerializedName("value")
    val value: Double,
    @SerializedName("address")
    val address: String,
    @SerializedName("confirmations")
    val confirmations: Int
)

/**
 * Data class representing balance response
 */
data class BalanceResponse(
    @SerializedName("address")
    val address: String,
    @SerializedName("confirmed_balance")
    val confirmedBalance: Double,
    @SerializedName("unconfirmed_balance")
    val unconfirmedBalance: Double,
    @SerializedName("total_balance")
    val totalBalance: Double,
    @SerializedName("utxo_count")
    val utxoCount: Int
)

/**
 * Data class representing staking response
 */
data class StakeResponse(
    @SerializedName("success")
    val success: Boolean,
    @SerializedName("validator_address")
    val validatorAddress: String,
    @SerializedName("staked_amount")
    val stakedAmount: Double,
    @SerializedName("message")
    val message: String
)
