<template>
  <div class="login-container">
    <div class="login-card">
      <h1>{{ title }}</h1>
      <p>{{ subtitle }}</p>

      <!-- Show error messages to the user instead of a bare alert() -->
      <div v-if="errorMessage" class="error-banner">{{ errorMessage }}</div>

      <form @submit.prevent="handleSubmit">

        <!-- Registration-only fields -->
        <template v-if="isRegister">
          <div class="input-row">
            <div class="input-group">
              <label>First Name</label>
              <input v-model="firstName" type="text" placeholder="First name" required />
            </div>
            <div class="input-group">
              <label>Last Name</label>
              <input v-model="lastName" type="text" placeholder="Last name" required />
            </div>
          </div>

          <div class="input-group">
            <label>Username</label>
            <input v-model="username" type="text" placeholder="Choose a username" required />
          </div>

          <div class="input-group">
            <label>Phone</label>
            <input v-model="phone" type="tel" placeholder="Phone number" required />
          </div>
        </template>

        <div class="input-group">
          <label>Email</label>
          <input v-model="email" type="email" placeholder="Enter your email" required />
        </div>

        <div class="input-group">
          <label>Password</label>
          <input v-model="password" type="password" placeholder="Enter your password" required />
        </div>

        <!-- Confirm password only shown on register -->
        <div v-if="isRegister" class="input-group">
          <label>Confirm Password</label>
          <input v-model="confirmPassword" type="password" placeholder="Confirm password" required />
        </div>

        <button class="login-btn" :disabled="loading">
          {{ loading ? 'Please wait...' : buttonText }}
        </button>

        <div class="register-group">
          <router-link :to="linkRoute">{{ linkText }}</router-link>
        </div>

      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

// defineProps return value is captured as `props` so we can reference
// props.isRegister inside the script functions below.
const props = defineProps({
  title: String,
  subtitle: String,
  buttonText: String,
  linkText: String,
  linkRoute: String,
  isRegister: Boolean
})

const router = useRouter()

// Shared fields
const email = ref('')
const password = ref('')
const errorMessage = ref('')
const loading = ref(false)

// Registration-only fields
const username = ref('')
const firstName = ref('')
const lastName = ref('')
const phone = ref('')
const confirmPassword = ref('')

async function handleSubmit() {
  if (props.isRegister) {
    await register()
  } else {
    await login()
  }
}

async function login() {
  errorMessage.value = ''
  loading.value = true

  try {
    // OAuth2 password flow requires form-encoded body, not JSON
    const body = new URLSearchParams()
    body.append('username', email.value)
    body.append('password', password.value)

    const res = await fetch('/api/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body
    })

    if (!res.ok) {
      errorMessage.value = res.status === 401
        ? 'Incorrect email or password.'
        : 'Something went wrong. Please try again.'
      return
    }

    const data = await res.json()
    localStorage.setItem('token', data.access_token)
    router.push('/dashboard')
  } catch (err) {
    errorMessage.value = 'Could not reach the server. Check your connection.'
  } finally {
    loading.value = false
  }
}

async function register() {
  errorMessage.value = ''

  // Client-side password match check before hitting the server
  if (password.value !== confirmPassword.value) {
    errorMessage.value = 'Passwords do not match.'
    return
  }

  loading.value = true

  try {
    const res = await fetch('/api/users/add-user', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: username.value,
        email: email.value,
        plain_password: password.value,
        first_name: firstName.value,
        last_name: lastName.value,
        phone: phone.value
      })
    })

    if (!res.ok) {
      const data = await res.json()
      errorMessage.value = data.detail || 'Registration failed. Please try again.'
      loading.value = false
      return
    }

    // On success, auto-login. We intentionally do NOT reset loading here —
    // login() keeps the button disabled the whole way through and resets it
    // in its own finally block, preventing a flicker mid-flow.
    await login()
  } catch (err) {
    errorMessage.value = 'Could not reach the server. Check your connection.'
    loading.value = false
  }
}
</script>

<style scoped>

.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #03152e;
}

.login-card {
  background: white;
  padding: 40px;
  border-radius: 12px;
  width: 420px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, .2);
  text-align: center;
}

.login-card h1 {
  margin-bottom: 5px;
  color: rgba(0, 112, 217);
}

.login-card p {
  color: #666;
  margin-bottom: 25px;
}

.error-banner {
  background: #fff0f0;
  color: #c0392b;
  border: 1px solid #f5c6cb;
  border-radius: 6px;
  padding: 10px 14px;
  margin-bottom: 16px;
  font-size: 14px;
  text-align: left;
}

.input-row {
  display: flex;
  gap: 12px;
}

.input-row .input-group {
  flex: 1;
}

.input-group {
  display: flex;
  flex-direction: column;
  text-align: left;
  margin-bottom: 16px;
}

.input-group label {
  font-size: 14px;
  margin-bottom: 5px;
  font-weight: 500;
}

.input-group input {
  padding: 10px;
  border-radius: 6px;
  border: 1px solid #ccc;
  font-size: 14px;
}

.input-group input:focus {
  outline: none;
  border-color: #2f7df6;
  box-shadow: 0 0 0 2px rgba(47, 125, 246, 0.15);
}

.login-btn {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 8px;
  background: #2f7df6;
  color: white;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.2s;
}

.login-btn:hover:not(:disabled) {
  background: #1f6ae0;
}

.login-btn:disabled {
  background: #93b8f9;
  cursor: not-allowed;
}

.register-group {
  text-align: center;
  padding-top: 20px;
}

</style>