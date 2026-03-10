<template>
    <nav class="navbar">
        <div class="logo">WebSafe</div>

        <div class="search">
            <input type="text" placeholder="Search...">
        </div>

        <div class="links">
            <router-link to="/login">Log In</router-link>
            <a href="#">About Us</a>
            <a href="#">Support</a>
        </div>

    </nav>
</template>

<script setup>
</script>

<style scoped>

.navbar{
    position: sticky;
    top: 0;
    z-index: 1000;
    
    display:flex;
    align-items:center;
    justify-content:space-between;

    padding: 24px 30px;
    background:white;
}

.logo{
    font-size: 20px;
    font-weight: bold;
    color: rgba(0, 112, 217);
}

.search input{
    width: 300px;
    padding: 8px 14px;
    border-radius: 20px;
    border: 1px solid #ccc;
}

.links a{
    text-decoration:none;
    color:black;
    font-weight:500;
    padding: 10px;
}

.login{
    padding: 8px 16px;
    border-radius: 6px;
    border:none;
    background:black;
    color:white;
    cursor:pointer;
}


</style>