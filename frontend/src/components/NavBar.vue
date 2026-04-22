<template>
    <header class="site-header">
      <nav class="navbar" aria-label="Primary">
        <div>
            <router-link to="/" class="logo">WebSafe</router-link>
        </div>

        <p class="tagline">Secure site building with publishing and ecommerce.</p>

        <div class="links">
            <a href="/#features">Features</a>
            <a href="/#pricing">Pricing</a>
            <router-link to="/login">Log In</router-link>          
            <router-link to="/about">About Us</router-link>
            <a href="/about">Support</a>
        </div>
      </nav>
    </header>
</template>

<script setup>
</script>

<style scoped>

.site-header {
    position: sticky;
    top: 0;
    z-index: 1000;
}

.navbar{
    position: sticky;
    top: 0;
    z-index: 1000;
    
    display:flex;
    align-items:center;
    justify-content:space-between;

    padding: 24px 30px;
    background:white;
    border-bottom: 1px solid #E6F0FA;
}

.logo{
    text-decoration:none;
    font-size: 20px;
    font-weight: bold;
    color: rgba(0, 112, 217);
    
}

.tagline {
    color: #4b5563;
    font-size: 0.95rem;
}

.links {
    display: flex;
    align-items: center;
    gap: 8px;
}

.links a{
    text-decoration:none;
    color:black;
    font-weight:500;
    padding: 10px;
    border-radius: 8px;
}

.links a:hover,
.links a:focus-visible {
    background: #eef4ff;
    color: #0f172a;
}

</style>
