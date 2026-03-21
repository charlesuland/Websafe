<template>
  <div class="login-container">

    <div class="login-card">

      <h1>{{ title }}</h1>
      <p>{{ subtitle }}</p>

      <form @submit.prevent="login">

        <div class="input-group">
          <label>Email</label>
          <input v-model="email" type="text" placeholder="Enter your email" />
        </div>

        <div class="input-group">
          <label>Password</label>
          <input v-model="password" type="password" placeholder="Enter your password" />
        </div>

        <!-- Only show for register -->
        <div v-if="isRegister" class="input-group">
          <label>Confirm Password</label>
          <input type="password" placeholder="Confirm password" />
        </div>

        <button class="login-btn">
          {{ buttonText }}
        </button>

        <div class="register-group">
          <router-link :to="linkRoute">{{ linkText }}</router-link>
        </div>

      </form>

    </div>

  </div>
</template>

<script setup>

defineProps({
  title: String,
  subtitle: String,
  buttonText: String,
  linkText: String,
  linkRoute: String,
  isRegister: Boolean
})

import { ref } from 'vue'

const email = ref('')
const password = ref('')

async function login() {
  console.log("Trying to login with: " + email.value + " " + password.value)
  const body = new URLSearchParams()

  body.append('username', email.value)
  body.append('password', password.value)

  const res = await fetch(`/api/token`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body
  })

  if (!res.ok) {
    alert("Login failed!")
    return
  }

  const data = await res.json()

  localStorage.setItem('token', data.access_token)

  window.location.href = '/dashboard'
}

</script>

<style scoped>

.login-container{
  height:100vh;
  display:flex;
  justify-content:center;
  align-items:center;
  background:#03152e;
}

.login-card{
  background:white;
  padding:40px;
  border-radius:12px;
  width:380px;
  box-shadow:0 10px 25px rgba(0,0,0,.2);
  text-align:center;
}

.login-card h1{
  margin-bottom:5px;
  color: rgba(0,112,217);
}

.login-card p{
  color:#666;
  margin-bottom:25px;
}

.input-group{
  display:flex;
  flex-direction:column;
  text-align:left;
  margin-bottom:20px;
}

.input-group label{
  font-size:14px;
  margin-bottom:5px;
}

.input-group input{
  padding:10px;
  border-radius:6px;
  border:1px solid #ccc;
}

.login-btn{
  width:100%;
  padding:12px;
  border:none;
  border-radius:8px;
  background:#2f7df6;
  color:white;
  font-size:16px;
  cursor:pointer;
}

.login-btn:hover{
  background:#1f6ae0;
}

.register-group{
  text-align:center;
  padding-top:20px;
}

</style>