<template>
  <div class="sensor-card">
    <h3 class="title">{{ title }}</h3>
    <div class="value">{{ value }}{{ unit }}</div>
    <div class="bar-bg">
      <div class="bar-fill" :class="color" :style="{ width: value + '%' }"></div>
    </div>
  </div>
</template>

<script setup>
defineProps(['title', 'value', 'unit', 'color']);
</script>