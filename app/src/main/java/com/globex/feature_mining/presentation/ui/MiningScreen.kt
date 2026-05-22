package com.globex.feature_mining.presentation.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Stop
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.globex.feature_mining.presentation.viewmodel.MiningViewModel
import java.text.NumberFormat

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MiningScreen(
    viewModel: MiningViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Mining Dashboard") }
            )
        }
    ) { paddingValues ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues),
            verticalArrangement = Arrangement.spacedBy(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // Mining Control Card
            item {
                MiningControlCard(
                    isMining = uiState.isMining,
                    isLoading = uiState.isLoading,
                    onStartClick = { viewModel.startMining("miner_address_here") },
                    onStopClick = { viewModel.stopMining() }
                )
            }

            // Thread Count Slider
            item {
                ThreadCountCard(
                    threadCount = uiState.threadCount,
                    onThreadCountChange = { viewModel.updateThreadCount(it) }
                )
            }

            // Stats Grid
            item {
                MiningStatsGrid(
                    hashRate = uiState.hashRate,
                    totalRewards = uiState.totalRewards,
                    estimatedEarnings = uiState.estimatedEarnings,
                    difficulty = uiState.difficulty,
                    blocksMined = uiState.blocksMined
                )
            }

            // Error message
            if (uiState.error != null) {
                item {
                    Card(
                        modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp),
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

@Composable
fun MiningControlCard(
    isMining: Boolean,
    isLoading: Boolean,
    onStartClick: () -> Unit,
    onStopClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = if (isMining) "Mining Active" else "Mining Stopped",
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
                color = if (isMining) Color.Green else Color.Gray
            )
            Spacer(modifier = Modifier.height(16.dp))
            Row(
                horizontalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                Button(
                    onClick = onStartClick,
                    enabled = !isMining && !isLoading,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color.Green
                    )
                ) {
                    Icon(Icons.Default.PlayArrow, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Start Mining")
                }
                Button(
                    onClick = onStopClick,
                    enabled = isMining,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color.Red
                    )
                ) {
                    Icon(Icons.Default.Stop, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Stop Mining")
                }
            }
            if (isLoading) {
                Spacer(modifier = Modifier.height(16.dp))
                CircularProgressIndicator()
            }
        }
    }
}

@Composable
fun ThreadCountCard(
    threadCount: Int,
    onThreadCountChange: (Int) -> Unit
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
                text = "CPU Threads: $threadCount",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.height(8.dp))
            Slider(
                value = threadCount.toFloat(),
                onValueChange = { onThreadCountChange(it.toInt()) },
                valueRange = 1f..16f,
                steps = 15
            )
        }
    }
}

@Composable
fun MiningStatsGrid(
    hashRate: Double,
    totalRewards: Long,
    estimatedEarnings: Double,
    difficulty: Double,
    blocksMined: Int
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            StatCard(
                modifier = Modifier.weight(1f),
                title = "Hash Rate",
                value = "${String.format("%.2f", hashRate)} H/s"
            )
            StatCard(
                modifier = Modifier.weight(1f),
                title = "Total Rewards",
                value = "${NumberFormat.getNumberInstance().format(totalRewards / 1e8)} GBX"
            )
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            StatCard(
                modifier = Modifier.weight(1f),
                title = "Est. Earnings",
                value = "${String.format("%.4f", estimatedEarnings)} GBX/day"
            )
            StatCard(
                modifier = Modifier.weight(1f),
                title = "Difficulty",
                value = String.format("%.2f", difficulty)
            )
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            StatCard(
                modifier = Modifier.weight(1f),
                title = "Blocks Mined",
                value = blocksMined.toString()
            )
            StatCard(
                modifier = Modifier.weight(1f),
                title = "Threads",
                value = "4"
            )
        }
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
