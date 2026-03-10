<template>
  <section class="pricing">

    <div class="container">

      <h2>Simple Pricing</h2>
      <p class="subtitle">Choose the plan that fits your needs</p>

      <div class="pricing-grid">

        <div class="pricing-card">
          <h3>Starter</h3>
          <p class="price">$0</p>
          <p class="description">Perfect for learning and small projects.</p>
          <button class="pricing-btn">Get Started</button>
        </div>

        <div class="pricing-card">
          <h3>Pro</h3>
          <p class="price">$12<span>/mo</span></p>
          <p class="description">Best for creators building real websites.</p>
          <button class="pricing-btn">Start Pro</button>
        </div>


      </div>

    </div>

  </section>
</template>

<style scoped>


.container h2{
  color: rgba(0, 112, 217);
}

.pricing{
  padding:100px 20px;
  background:#f7f9fc;
}

.container{
  max-width:1200px;
  margin:auto;
  text-align:center;
}

.subtitle{
  margin-top:10px;
  margin-bottom:50px;
  color: rgba(0, 112, 217);
}

.pricing-grid{
  display:grid;
  grid-template-columns:repeat(2,1fr);
  gap:30px;
}

/* Card */

.pricing-card{
  background:white;
  padding:40px;
  border-radius:12px;
  box-shadow:0 8px 20px rgba(0,0,0,0.08);
  transition:all .2s ease;
  color: rgba(0, 112, 217);
}

.pricing-card:hover{
  transform:translateY(-6px);
}



/* Price */

.price{
  font-size:40px;
  font-weight:700;
  margin:20px 0;
}

.price span{
  font-size:16px;
  color:#777;
}

.description{
  color:#666;
  margin-bottom:25px;
}

/* Button */

.pricing-btn{
  padding:12px 24px;
  border:none;
  border-radius:8px;
  background:#2f7df6;
  color:white;
  cursor:pointer;
  font-size:16px;
}

.pricing-btn:hover{
  background:#1f6ae0;
}

</style>