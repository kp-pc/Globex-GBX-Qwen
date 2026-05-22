package com.globex.feature_dashboard.presentation.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.globex.feature_dashboard.domain.model.SyncStatus
import com.globex.feature_dashboard.domain.model.ValidatorStatus
import com.globex.feature_dashboard.presentation.viewmodel.DashboardViewModel
import java.text.NumberFormat

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(
    viewModel: DashboardViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Globex Dashboard") },
                actions = {
                    IconButton(onClick = { viewModel.refresh() }) {
                        Icon(Icons.Default.Refresh, contentDescription = "Refresh")
                    }
                }
            )
        }
    ) { paddingValues ->
        if (uiState.isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues),
                verticalArrangement = Arrangement.spacedBy(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // Balance Card
                item {
                    BalanceCard(balance = uiState.balance)
                }

                // Stats Grid
                item {
                    StatsGrid(
                        blockHeight = uiState.blockHeight,
                        difficulty = uiState.difficulty,
                        peerCount = uiState.peerCount,
                        hashRate = uiState.hashRate
                    )
                }

                // Sync Status
                item {
                    SyncStatusCard(status = uiState.syncStatus)
                }

                // Staking & Validator
                item {
                    StakingCard(
                        stakingAmount = uiState.stakingAmount,
                        validatorStatus = uiState.validatorStatus
                    )
                }

                // Latest Blocks
                item {
                    Text(
                        text = "Latest Blocks",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold
                    )
                }

                items(uiState.latestBlocks) { block ->
                    BlockItem(block)
                }

                // Error message
                if (uiState.error != null) {
                    item {
                        Card(
                            modifier = Modifier.fillMaxWidth(),
                            colors = CardDefaults.cardColors(containerColor = Color.Red.copy(alpha = 0.1f))
                        ) {
                            Text(
                                text = "Error: ${uiState.error}",
                                modifier = Modifier.padding(16.dp),
                                color = Color.Red
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun BalanceCard(balance: Double) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "Total Balance",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "${NumberFormat.getNumberInstance().format(balance)} GBX",
                style = MaterialTheme.typography.headlineLarge,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary
            )
        }
    }
}

@Composable
fun StatsGrid(
    blockHeight: Long,
    difficulty: Double,
    peerCount: Int,
    hashRate: Double
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        StatCard(
            modifier = Modifier.weight(1f),
            title = "Block Height",
            value = blockHeight.toString()
        )
        StatCard(
            modifier = Modifier.weight(1f),
            title = "Difficulty",
            value = String.format("%.2f", difficulty)
        )
    }
    Spacer(modifier = Modifier.height(8.dp))
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        StatCard(
            modifier = Modifier.weight(1f),
            title = "Peers",
            value = peerCount.toString()
        )
        StatCard(
            modifier = Modifier.weight(1f),
            title = "Hash Rate",
            value = "${String.format("%.2f", hashRate)} H/s"
        )
    }
}

@Composable
fun StatCard(
    modifier: Modifier = Modifier,
    title: String,
    value: String
) {
    Card(
        modifier = modifier,
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = value,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
        }
    }
}

@Composable
fun SyncStatusCard(status: SyncStatus) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp),
        colors = CardDefaults.cardColors(
            containerColor = when (status) {
                SyncStatus.SYNCED -> Color.Green.copy(alpha = 0.1f)
                SyncStatus.SYNCING -> Color.Yellow.copy(alpha = 0.1f)
                SyncStatus.NOT_SYNCED -> Color.Red.copy(alpha = 0.1f)
            }
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "Sync Status",
                style = MaterialTheme.typography.bodyLarge
            )
            Badge(
                colors = BadgeDefaults.badgeColors(
                    containerColor = when (status) {
                        SyncStatus.SYNCED -> Color.Green
                        SyncStatus.SYNCING -> Color.Yellow
                        SyncStatus.NOT_SYNCED -> Color.Red
                    }
                )
            ) {
                Text(
                    text = status.name,
                    color = Color.White
                )
            }
        }
    }
}

@Composable
fun StakingCard(
    stakingAmount: Double,
    validatorStatus: ValidatorStatus
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Text(
                text = "Staking & Validation",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.height(12.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column {
                    Text(
                        text = "Staked Amount",
                        style = MaterialTheme.typography.bodyMedium
                    )
                    Text(
                        text = "${NumberFormat.getNumberInstance().format(stakingAmount)} GBX",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                }
                Column(horizontalAlignment = Alignment.End) {
                    Text(
                        text = "Validator Status",
                        style = MaterialTheme.typography.bodyMedium
                    )
                    Text(
                        text = validatorStatus.name,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = when (validatorStatus) {
                            ValidatorStatus.ACTIVE -> Color.Green
                            ValidatorStatus.SLASHED -> Color.Red
                            ValidatorStatus.PENDING -> Color.Yellow
                            ValidatorStatus.INACTIVE -> Color.Gray
                        }
                    )
                }
            }
        }
    }
}

@Composable
fun BlockItem(block: com.globex.feature_dashboard.domain.model.BlockSummary) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Column {
                Text(
                    text = "Block #${block.height}",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "${block.transactions} transactions",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            Column(horizontalAlignment = Alignment.End) {
                Text(
                    text = block.hash.take(10) + "...",
                    style = MaterialTheme.typography.bodySmall,
                    fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace
                )
                Text(
                    text = formatTimestamp(block.timestamp),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

private fun formatTimestamp(timestamp: Long): String {
    return java.text.SimpleDateFormat("MMM dd, HH:mm", java.util.Locale.getDefault())
        .format(java.util.Date(timestamp))
}
