<template>
  <div class="text-right">
    <div class="text-xl font-bold" :class="scoreColor">{{ score.toFixed(0) }}<span class="text-sm font-normal text-surface-500">%</span></div>
    <div class="mt-1.5 w-24 ml-auto h-1.5 bg-surface-700 rounded-full overflow-hidden">
      <div class="h-full rounded-full transition-all duration-500" :class="barColor" :style="{ width: score + '%' }"></div>
    </div>
    <div class="text-xs mt-0.5" :class="scoreColor">{{ label }}</div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ score: number }>()

const scoreColor = computed(() => {
  if (props.score >= 70) return 'text-emerald-400'
  if (props.score >= 45) return 'text-brand-400'
  return 'text-red-400'
})

const barColor = computed(() => {
  if (props.score >= 70) return 'bg-emerald-400'
  if (props.score >= 45) return 'bg-brand-400'
  return 'bg-red-400'
})

const label = computed(() => {
  if (props.score >= 70) return 'High'
  if (props.score >= 45) return 'Medium'
  return 'Low'
})
</script>
