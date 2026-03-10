<template>
  <Navbar /> 
  <HeroSection /> 
  <FeatureSection />
  <HowItWorksSection />
  <PricingSection />
  <Footer />
</template>
    
<script setup>

import Navbar from "../components/NavBar.vue"
import HeroSection from "../components/HeroSection.vue";
import FeatureSection from "@/components/FeatureSection.vue";
import HowItWorksSection from "@/components/HowItWorksSection.vue";
import PricingSection from "@/components/PricingSection.vue";
import Footer from "../components/Footer.vue"



</script>

<style>

.container{
  max-width:1200px;
  margin:auto;
}

</style>