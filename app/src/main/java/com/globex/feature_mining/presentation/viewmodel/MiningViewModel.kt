package com.globex.feature_mining.presentation.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.globex.core.data.api.GlobexApi
import com.globex.core.data.local.dao.MiningDao
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class MiningViewModel @Inject constructor(
    private val api: GlobexApi,
    private val miningDao: MiningDao
) : ViewModel() {

    data class MiningUiState(
        val isMining: Boolean = false,
        val hashRate: Double = 0.0,
        val totalRewards: Long = 0L,
        val estimatedEarnings: Double = 0.0,
        val difficulty: Double = 0.0,
        val threadCount: Int = 4,
        val blocksMined: Int = 0,
        val isLoading: Boolean = false,
        val error: String? = null
    )

    private val _uiState = MutableStateFlow(MiningUiState())
    val uiState: StateFlow<MiningUiState> = _uiState.asStateFlow()

    fun startMining(minerAddress: String) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            try {
                // Call mining API
                val response = api.mineBlock(com.globex.core.data.dto.MineRequest(minerAddress))
                if (response.isSuccessful && response.body()?.success == true) {
                    _uiState.value = _uiState.value.copy(
                        isMining = true,
                        isLoading = false
                    )
                } else {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        error = response.message()
                    )
                }
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = e.message
                )
            }
        }
    }

    fun stopMining() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isMining = false)
        }
    }

    fun updateThreadCount(count: Int) {
        _uiState.value = _uiState.value.copy(threadCount = count)
    }

    fun loadMiningStats() {
        viewModelScope.launch {
            miningDao.getTotalRewards()
                .catch { e -> _uiState.value = _uiState.value.copy(error = e.message) }
                .collect { rewards ->
                    _uiState.value = _uiState.value.copy(totalRewards = rewards ?: 0L)
                }
        }
    }
}
