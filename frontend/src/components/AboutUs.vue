<template>
  <section class="about">
    <div class="container">
      
      <h1>About <span>WebSafe</span></h1>
      <p class="subtitle">
        Build, customize, and manage your websites securely — all in one place.
      </p>

      <div class="section">
        <h2>Our Mission</h2>
        <p>
          WebSafe is designed to make website creation simple, fast, and secure.
          We empower users to build fully customizable web pages without needing
          complex setup or advanced technical knowledge.
        </p>
      </div>

      <div class="section">
        <h2>What We Offer</h2>
        <ul>
          <li>Drag-and-drop website builder</li>
          <li>Customizable components (text, images, navigation)</li>
          <li>Secure authentication and project management</li>
          <li>Multi-page website support</li>
          <li>Cloud storage integration</li>
        </ul>
      </div>

      <div class="section">
        <h2>Why WebSafe?</h2>
        <p>
          We focus on both usability and security. Whether you're building a personal
          project or a business site, WebSafe ensures your data and content are
          protected while giving you full creative control.
        </p>
      </div>

    </div>
  </section>
</template>

<script setup>
</script>

<style scoped>
.about {
  padding: 60px 20px;
  background: #f5f9ff; /* subtle blue tint */
  min-height: 100vh;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  text-align: center;
}

/* Main Title */
h1 {
  font-size: 38px;
  margin-bottom: 10px;
  color: #0070D9; /* matches logo */
}

/* Subtitle */
.subtitle {
  font-size: 18px;
  color: #555;
  margin-bottom: 40px;
}

/* Sections */
.section {
  margin-bottom: 40px;
  text-align: left;
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

/* Section Titles */
.section h2 {
  font-size: 24px;
  margin-bottom: 10px;
  color: #0070D9; /* blue headers */
}

/* Paragraph text */
.section p {
  color: #333;
  line-height: 1.7;
}

/* List */
ul {
  padding-left: 20px;
}

li {
  margin-bottom: 10px;
  color: #333;
}

/* Optional: hover effect for sections */
.section:hover {
  transform: translateY(-3px);
  transition: 0.2s ease;
}
</style>