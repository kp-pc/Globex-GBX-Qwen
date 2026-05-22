package com.globex.core.presentation.security

import android.app.Activity
import android.view.WindowManager
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.ui.platform.LocalView

/**
 * Helper to disable screenshots on sensitive screens
 */
class ScreenshotProtection {
    
    /**
     * Enable screenshot protection for an Activity
     * This disables screenshots and screen recording for the given activity
     */
    fun enable(activity: Activity) {
        activity.window.setFlags(
            WindowManager.LayoutParams.FLAG_SECURE,
            WindowManager.LayoutParams.FLAG_SECURE
        )
    }
    
    /**
     * Disable screenshot protection for an Activity
     */
    fun disable(activity: Activity) {
        activity.window.clearFlags(WindowManager.LayoutParams.FLAG_SECURE)
    }
}

/**
 * Composable function to enable screenshot protection in Jetpack Compose
 * Use this on sensitive screens like wallet, keys, PIN entry, etc.
 */
@Composable
fun DisableScreenshots() {
    val view = LocalView.current
    
    DisposableEffect(Unit) {
        val window = (view.context as? Activity)?.window
        
        // Enable FLAG_SECURE to prevent screenshots
        window?.addFlags(WindowManager.LayoutParams.FLAG_SECURE)
        
        onDispose {
            window?.clearFlags(WindowManager.LayoutParams.FLAG_SECURE)
        }
    }
}

/**
 * Extension function for Activity to enable screenshot protection
 */
fun Activity.disableScreenshots() {
    window.setFlags(
        WindowManager.LayoutParams.FLAG_SECURE,
        WindowManager.LayoutParams.FLAG_SECURE
    )
}

/**
 * Extension function for Activity to enable screenshots
 */
fun Activity.enableScreenshots() {
    window.clearFlags(WindowManager.LayoutParams.FLAG_SECURE)
}
