<template>

  <div class="dashboard">

    <h1>Dashboard</h1>
    <p>Welcome to WebSafe.</p>

    <div class="dashboard-header">
      <h2>Your Websites</h2>

      <button class="create-btn">
        + Create Website
      </button>
    </div>

    <div class="site-grid">

      <div class="site-card">
        <h3>My First Website</h3>
        <p>Last edited: Today</p>
        <button>Edit</button>
      </div>

      <div class="site-card">
        <h3>Portfolio Site</h3>
        <p>Last edited: Yesterday</p>
        <button>Edit</button>
      </div>

      <div class="site-card new-site">
        <h3>+ Create New Website</h3>
      </div>

    </div>

  </div>

</template>

<style scoped>

.dashboard{
  padding:80px 20px;
  max-width:1100px;
  margin:auto;
}

.dashboard h1{
  margin-bottom:10px;
}

.dashboard-header{
  margin-top:40px;
  display:flex;
  justify-content:space-between;
  align-items:center;
}

.create-btn{
  background:#2f7df6;
  color:white;
  border:none;
  padding:10px 18px;
  border-radius:8px;
  cursor:pointer;
}

.create-btn:hover{
  background:#1f6ae0;
}

.site-grid{
  margin-top:30px;
  display:grid;
  grid-template-columns:repeat(3,1fr);
  gap:20px;
}

.site-card{
  background:white;
  padding:25px;
  border-radius:12px;
  box-shadow:0 6px 15px rgba(0,0,0,0.1);
}

.site-card h3{
  margin-bottom:10px;
}

.site-card p{
  color:#666;
  font-size:14px;
  margin-bottom:15px;
}

.site-card button{
  background:#2f7df6;
  color:white;
  border:none;
  padding:8px 14px;
  border-radius:6px;
  cursor:pointer;
}

.new-site{
  display:flex;
  align-items:center;
  justify-content:center;
  cursor:pointer;
  font-weight:600;
  background:#f5f7fb;
}

</style>