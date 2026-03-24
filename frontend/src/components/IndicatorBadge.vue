<template>
  <div class="badge">
    <span class="label">{{ label }}</span>
    <span class="val">{{ value.toFixed(2) }}</span>
  </div>
</template>

<script setup lang="ts">
defineProps<{ label: string; value: number }>()
</script>

<style scoped>
.badge {
  background: #12121a; border-radius: 8px; padding: 12px 16px;
  display: flex; flex-direction: column; gap: 4px;
  border: 1px solid #2a2a38; min-width: 100px;
}
.label { font-size: 11px; color: #888; text-transform: uppercase; }
.val { font-size: 20px; font-weight: 700; color: #fff; }
</style>
