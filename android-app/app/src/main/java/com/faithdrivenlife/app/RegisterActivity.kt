package com.faithdrivenlife.app

import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import androidx.core.content.ContextCompat
import androidx.core.app.ActivityCompat
import android.Manifest
import android.view.View
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.textfield.TextInputEditText
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.auth.UserProfileChangeRequest
import com.google.firebase.messaging.FirebaseMessaging

class RegisterActivity : AppCompatActivity() {

    private lateinit var auth: FirebaseAuth
    private lateinit var nameInput: TextInputEditText
    private lateinit var emailInput: TextInputEditText
    private lateinit var passwordInput: TextInputEditText
    private lateinit var registerButton: Button
    private lateinit var statusText: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_register)

        auth = FirebaseAuth.getInstance()
        nameInput = findViewById(R.id.registerName)
        emailInput = findViewById(R.id.registerEmail)
        passwordInput = findViewById(R.id.registerPassword)
        registerButton = findViewById(R.id.registerButton)
        statusText = findViewById(R.id.registerStatus)

        registerButton.setOnClickListener { doRegister() }

        if (auth.currentUser != null) {
            requestNotificationPermissionIfNeeded()
            subscribeToBlogNotifications()
            statusText.visibility = View.VISIBLE
            statusText.text = "You're signed in. You'll get notifications for new blog posts."
        }
    }

    private fun requestNotificationPermissionIfNeeded() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
            ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.POST_NOTIFICATIONS), 1)
        }
    }

    private fun doRegister() {
        val name = nameInput.text?.toString()?.trim().orEmpty()
        val email = emailInput.text?.toString()?.trim().orEmpty()
        val password = passwordInput.text?.toString().orEmpty()

        when {
            name.isEmpty() -> { nameInput.error = "Enter your name"; return }
            email.isEmpty() -> { emailInput.error = "Enter your email"; return }
            password.length < 6 -> { passwordInput.error = "Password must be at least 6 characters"; return }
        }

        registerButton.isEnabled = false
        statusText.visibility = View.VISIBLE
        statusText.text = "Creating account…"

        auth.createUserWithEmailAndPassword(email, password)
            .addOnCompleteListener(this) { task ->
                if (task.isSuccessful) {
                    requestNotificationPermissionIfNeeded()
                    auth.currentUser?.updateProfile(
                        UserProfileChangeRequest.Builder().setDisplayName(name).build()
                    )?.addOnCompleteListener {
                        subscribeToBlogNotifications()
                        statusText.text = "Account created. You'll get notifications for new posts."
                        Toast.makeText(this, "Welcome! Notifications enabled.", Toast.LENGTH_SHORT).show()
                        startActivity(Intent(this, MainActivity::class.java).apply { flags = Intent.FLAG_ACTIVITY_CLEAR_TOP })
                        finish()
                    } ?: run {
                        subscribeToBlogNotifications()
                        startActivity(Intent(this, MainActivity::class.java).apply { flags = Intent.FLAG_ACTIVITY_CLEAR_TOP })
                        finish()
                    }
                } else {
                    statusText.text = task.exception?.message ?: "Registration failed"
                    registerButton.isEnabled = true
                }
            }
    }

    private fun subscribeToBlogNotifications() {
        FirebaseMessaging.getInstance().subscribeToTopic("new_blog").addOnCompleteListener { }
    }
}
