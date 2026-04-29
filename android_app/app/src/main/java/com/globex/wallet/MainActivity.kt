package com.globex.wallet

import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.globex.wallet.databinding.ActivityMainBinding
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val client = OkHttpClient()
    private val BASE_URL = "http://10.0.2.2:5001" // Android emulator localhost

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupListeners()
        loadBlockchainInfo()
    }

    private fun setupListeners() {
        // Create Wallet Button
        binding.btnCreateWallet.setOnClickListener {
            createWallet()
        }

        // Mine Button
        binding.btnMine.setOnClickListener {
            mineBlock()
        }

        // Send Transaction Button
        binding.btnSend.setOnClickListener {
            sendTransaction()
        }

        // Validate Chain Button
        binding.btnValidate.setOnClickListener {
            validateChain()
        }

        // Refresh Button
        binding.btnRefresh.setOnClickListener {
            loadBlockchainInfo()
        }
    }

    private fun createWallet() {
        lifecycleScope.launch {
            showLoading(true)
            try {
                val response = apiCall("/api/create-wallet")
                withContext(Dispatchers.Main) {
                    val json = JSONObject(response)
                    val address = json.getString("address")
                    binding.tvWalletAddress.text = address
                    binding.tvBalance.text = "0 GBX"
                    Toast.makeText(this@MainActivity, "Wallet created!", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            } finally {
                showLoading(false)
            }
        }
    }

    private fun mineBlock() {
        lifecycleScope.launch {
            showLoading(true)
            try {
                val response = apiCall("/api/mine")
                withContext(Dispatchers.Main) {
                    val json = JSONObject(response)
                    val reward = json.getInt("reward")
                    Toast.makeText(this@MainActivity, "Mined! Reward: $reward GBX", Toast.LENGTH_SHORT).show()
                    loadBlockchainInfo()
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, "Mining error: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            } finally {
                showLoading(false)
            }
        }
    }

    private fun sendTransaction() {
        val recipient = binding.etRecipient.text.toString().trim()
        val amountStr = binding.etAmount.text.toString().trim()

        if (recipient.isEmpty() || amountStr.isEmpty()) {
            Toast.makeText(this, "Please fill all fields", Toast.LENGTH_SHORT).show()
            return
        }

        val amount = amountStr.toIntOrNull()
        if (amount == null || amount <= 0) {
            Toast.makeText(this, "Invalid amount", Toast.LENGTH_SHORT).show()
            return
        }

        lifecycleScope.launch {
            showLoading(true)
            try {
                val jsonBody = JSONObject()
                jsonBody.put("recipient", recipient)
                jsonBody.put("amount", amount)

                val response = apiCall("/api/send", jsonBody.toString())
                withContext(Dispatchers.Main) {
                    val result = JSONObject(response)
                    val success = result.getBoolean("success")
                    if (success) {
                        Toast.makeText(this@MainActivity, "Transaction sent!", Toast.LENGTH_SHORT).show()
                        binding.etRecipient.text.clear()
                        binding.etAmount.text.clear()
                        loadBlockchainInfo()
                    } else {
                        Toast.makeText(this@MainActivity, "Transaction failed", Toast.LENGTH_SHORT).show()
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            } finally {
                showLoading(false)
            }
        }
    }

    private fun validateChain() {
        lifecycleScope.launch {
            showLoading(true)
            try {
                val response = apiCall("/api/validate")
                withContext(Dispatchers.Main) {
                    val json = JSONObject(response)
                    val valid = json.getBoolean("valid")
                    if (valid) {
                        Toast.makeText(this@MainActivity, "✅ Blockchain is valid!", Toast.LENGTH_SHORT).show()
                    } else {
                        Toast.makeText(this@MainActivity, "❌ Blockchain is INVALID!", Toast.LENGTH_LONG).show()
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, "Validation error: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            } finally {
                showLoading(false)
            }
        }
    }

    private fun loadBlockchainInfo() {
        lifecycleScope.launch {
            try {
                val response = apiCall("/api/info")
                withContext(Dispatchers.Main) {
                    val json = JSONObject(response)
                    val height = json.getInt("height")
                    val blocks = json.getInt("blocks")
                    val pending = json.getInt("pending_transactions")

                    binding.tvChainHeight.text = height.toString()
                    binding.tvTotalBlocks.text = blocks.toString()
                    binding.tvPendingTx.text = pending.toString()
                }
            } catch (e: Exception) {
                // Silently fail on initial load
            }
        }
    }

    private suspend fun apiCall(endpoint: String, body: String? = null): String {
        return withContext(Dispatchers.IO) {
            val url = "$BASE_URL$endpoint"
            val request = if (body != null) {
                val mediaType = "application/json; charset=utf-8".toMediaType()
                Request.Builder()
                    .url(url)
                    .post(body.toRequestBody(mediaType))
                    .build()
            } else {
                Request.Builder()
                    .url(url)
                    .get()
                    .build()
            }

            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) {
                    throw Exception("API call failed: ${response.code}")
                }
                response.body?.string() ?: throw Exception("Empty response")
            }
        }
    }

    private fun showLoading(show: Boolean) {
        binding.progressBar.visibility = if (show) View.VISIBLE else View.GONE
        binding.btnCreateWallet.isEnabled = !show
        binding.btnMine.isEnabled = !show
        binding.btnSend.isEnabled = !show
    }
}
