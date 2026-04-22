<template>
  <a class="skip-link" href="#main-content">Skip to content</a>
  <router-view />
</template>

<style scoped>
.skip-link {
  position: absolute;
  top: -40px;
  left: 16px;
  z-index: 2000;
  padding: 10px 14px;
  border-radius: 10px;
  background: #ffffff;
  color: #0f172a;
  font-weight: 600;
  text-decoration: none;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.18);
}

.skip-link:focus {
  top: 16px;
}
</style>





