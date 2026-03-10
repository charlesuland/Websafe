<template>
  <section class="hero">

    <div class="hero-container">

      <div class="hero-text">

        <h1>Your Website,<br> Secured by Design</h1>

        <p>
          Build modern websites with security-first infrastructure,
          powerful customization, and built-in ecommerce.
        </p>

        
        
        <div class="cta">
          <router-link class="cta-button" to="/register">Start Free Today</router-link>
        </div>


      </div>

      <div class="hero-image">
        <img src="../assets/websafe-logo.png" alt="WebSafe Logo">
      </div>

    </div>

  </section>
</template>

<script setup>
</script>

<style scoped>

.hero{
  padding:120px 0;
  background-color: rgb(2, 12, 26);
}

.hero-container{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:80px;
}

.hero-text{
  max-width:550px;
  padding: 40px;
}

.hero-text h1{
  font-size:56px;
  font-weight:700;
  line-height:1.1;
  margin-bottom:20px;
}

.hero-text p{
  font-size:18px;
  color:#555;
  margin-bottom:30px;
}

.cta{
  display:inline-block;
}

.cta-button{
  display:inline-block;
  padding:14px 28px;
  font-size:16px;
  font-weight:600;
  border-radius:8px;
  background:#2563eb;
  color:white;
  text-decoration:none;
  transition:all .2s ease;
  box-shadow:0 8px 20px rgba(0,0,0,0.15);
}



.cta-button:hover{
  background:#1d4ed8;
  transform:translateY(-2px);
  box-shadow:0 12px 24px rgba(0,0,0,0.2);
}



.hero-image img{
  width:520px;
  filter: drop-shadow(0px 20px 40px rgba(0,0,0,0.2));
}

</style>