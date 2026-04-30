<template>
  <Navbar />
  <main id="main-content">
    <HeroSection />
    <FeatureSection />
    <HowItWorksSection />
  </main>
  <Footer />
</template>
    
<script setup>

import Navbar from "../components/NavBar.vue"
import HeroSection from "../components/HeroSection.vue";
import FeatureSection from "@/components/FeatureSection.vue";
import HowItWorksSection from "@/components/HowItWorksSection.vue";
import Footer from "../components/Footer.vue"

</script>

<style>

.container{
  max-width:1200px;
  margin:auto;
}

</style>
