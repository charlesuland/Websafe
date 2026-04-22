<template>
  <main id="main-content">
    <AuthForm
      title="Create an Account"
      subtitle="Join WebSafe and start building"
      buttonText="Sign Up"
      linkText="Already have an account? Log In"
      linkRoute="/login"
      :isRegister="true"
    />
  </main>
</template>

<script setup>
import AuthForm from "../components/AuthForm.vue"
</script>
