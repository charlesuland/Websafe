<template>
    <section class="features">
        <div class="container">

            <h2>Why Use WebSafe?</h2>

            <div class="feature-grid">

                <div class="feature-card">
                    <h3> Security First</h3>
                    <p>Build websites with built-in security protections.</p>
                </div>

                <div class="feature-card">
                    <h3> Drag & Drop Builder</h3>
                    <p>Design layouts visually without writing code.</p>
                </div>

                <div class="feature-card">
                    <h3> Ecommerce Ready</h3>
                    <p>Sell products online with integrated payments.</p>
                </div>

            </div>
        </div>
    </section>
</template>


<style scoped>

.features{
  padding:80px 20px;
  background:#f7f9fc;
}

.container{
  max-width:1200px;
  margin:auto;
  text-align:center;
}

.features h2{
  font-size:36px;
  margin-bottom:40px;
  color:rgba(0, 112, 217);
}

.feature-grid{
  display:grid;
  grid-template-columns:repeat(3,1fr);
  gap:30px;
}

.feature-card{
  background:white;
  padding:30px;
  border-radius:10px;
  box-shadow:0 8px 20px rgba(0,0,0,0.08);
  transition:transform .2s ease;
}

.feature-card:hover{
  transform:translateY(-5px);
}

.feature-card h3{
  margin-bottom:10px;
  color: rgba(0, 112, 217);
}

.feature-card p{
  color:#666;
}

</style>