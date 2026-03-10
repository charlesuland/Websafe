<template>
  <footer class="footer">

    <div class="footer-container">

      <div class="footer-grid">

        <div class="footer-brand">
          <h2>WebSafe</h2>
          <p>Secure website building made simple.</p>
        </div>

        <div class="footer-column">
          <h3>Product</h3>
          <ul>
            <li><a href="#">Features</a></li>
            <li><a href="#">Pricing</a></li>
            <li><router-link to="/login">Login</router-link></li>
          </ul>
        </div>

      </div>

      <div class="footer-bottom">
        <p>© 2026 WebSafe. All rights reserved.</p>
      </div>

    </div>

  </footer>
</template>

<style scoped>

.footer{
  background:#03152e;
  color:white;
  padding:60px 20px 30px;
}

.footer-container{
  max-width:1200px;
  margin:auto;
}

.footer-grid{
  display:grid;
  grid-template-columns:2fr 1fr;
  gap:40px;
  margin-bottom:40px;
}

.footer-brand h2{
  margin-bottom:10px;
}

.footer-brand p{
  color:#b8c3d1;
}

.footer-column h3{
  margin-bottom:15px;
}

.footer-column ul{
  list-style:none;
  padding:0;
}

.footer-column li{
  margin-bottom:10px;
}

.footer-column a{
  color:#b8c3d1;
  text-decoration:none;
}

.footer-column a:hover{
  color:white;
}

.footer-bottom{
  border-top:1px solid rgba(255,255,255,0.1);
  padding-top:20px;
  text-align:center;
  color:#b8c3d1;
}

</style>