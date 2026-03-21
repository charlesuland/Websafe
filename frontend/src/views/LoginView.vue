<template>
  <AuthForm
    title="Welcome Back"
    subtitle="Log in to your WebSafe account"
    buttonText="Log In"
    linkText="Don't have an account? Sign Up"
    linkRoute="/register"
    :isRegister="false"
  />
</template>

<script setup>
import AuthForm from "@/components/AuthForm.vue"
</script>