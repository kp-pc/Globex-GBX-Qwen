package com.globex.feature_dashboard.presentation.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.globex.feature_dashboard.domain.model.DashboardState
import com.globex.feature_dashboard.domain.model.SyncStatus
import com.globex.feature_dashboard.domain.model.ValidatorStatus
import com.globex.feature_dashboard.domain.repository.DashboardRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class DashboardViewModel @Inject constructor(
    private val repository: DashboardRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(DashboardState())
    val uiState: StateFlow<DashboardState> = _uiState.asStateFlow()

    init {
        loadDashboardData()
    }

    fun loadDashboardData() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            
            launch {
                repository.getBalance()
                    .catch { e -> _uiState.value = _uiState.value.copy(error = e.message) }
                    .collect { balance ->
                        _uiState.value = _uiState.value.copy(balance = balance)
                    }
            }
            
            launch {
                repository.getBlockHeight()
                    .catch { e -> _uiState.value = _uiState.value.copy(error = e.message) }
                    .collect { height ->
                        _uiState.value = _uiState.value.copy(blockHeight = height)
                    }
            }
            
            launch {
                repository.getDifficulty()
                    .catch { e -> _uiState.value = _uiState.value.copy(error = e.message) }
                    .collect { difficulty ->
                        _uiState.value = _uiState.value.copy(difficulty = difficulty)
                    }
            }
            
            launch {
                repository.getPeerCount()
                    .catch { e -> _uiState.value = _uiState.value.copy(error = e.message) }
                    .collect { count ->
                        _uiState.value = _uiState.value.copy(peerCount = count)
                    }
            }
            
            launch {
                repository.getHashRate()
                    .catch { e -> _uiState.value = _uiState.value.copy(error = e.message) }
                    .collect { rate ->
                        _uiState.value = _uiState.value.copy(hashRate = rate)
                    }
            }
            
            launch {
                repository.getLatestBlocks(10)
                    .catch { e -> _uiState.value = _uiState.value.copy(error = e.message) }
                    .collect { blocks ->
                        _uiState.value = _uiState.value.copy(latestBlocks = blocks)
                    }
            }
            
            launch {
                repository.getSyncStatus()
                    .catch { e -> _uiState.value = _uiState.value.copy(error = e.message) }
                    .collect { status ->
                        _uiState.value = _uiState.value.copy(syncStatus = status)
                    }
            }
            
            launch {
                repository.getStakingAmount()
                    .catch { e -> _uiState.value = _uiState.value.copy(error = e.message) }
                    .collect { amount ->
                        _uiState.value = _uiState.value.copy(stakingAmount = amount)
                    }
            }
            
            launch {
                repository.getValidatorStatus()
                    .catch { e -> _uiState.value = _uiState.value.copy(error = e.message) }
                    .collect { status ->
                        val validatorStatus = when (status) {
                            "ACTIVE" -> ValidatorStatus.ACTIVE
                            "SLASHED" -> ValidatorStatus.SLASHED
                            "PENDING" -> ValidatorStatus.PENDING
                            else -> ValidatorStatus.INACTIVE
                        }
                        _uiState.value = _uiState.value.copy(validatorStatus = validatorStatus)
                    }
            }
            
            _uiState.value = _uiState.value.copy(isLoading = false)
        }
    }

    fun refresh() {
        viewModelScope.launch {
            repository.refreshDashboard()
            loadDashboardData()
        }
    }
}
