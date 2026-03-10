<template>
  <section class="how-it-works">

    <div class="container">

      <h2>How WebSafe Works</h2>

      <div class="steps">

        <div class="step">
          <h3>1. Create an Account</h3>
          <p>Sign up and start building your secure website.</p>
        </div>

        <div class="step">
          <h3>2. Design Your Site</h3>
          <p>Use our drag-and-drop builder to design pages.</p>
        </div>

        <div class="step">
          <h3>3. Launch Securely</h3>
          <p>Your website is automatically protected.</p>
        </div>

      </div>

    </div>

  </section>
</template>

<style scoped>

.how-it-works{
  padding:80px 20px;
}

.container{
  max-width:1200px;
  margin:auto;
  text-align:center;
}

.steps{
  display:grid;
  grid-template-columns:repeat(3,1fr);
  gap:30px;
  margin-top:40px;
}

.step{
  padding:20px;
}

</style>