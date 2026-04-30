<template>
  <span
    v-if="count > 0"
    class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border"
    :class="badgeClass"
    :title="title"
  >
    <span class="w-1.5 h-1.5 rounded-full animate-pulse" :class="dotClass"></span>
    {{ count }}
  </span>
</template>

<script setup lang="ts">
const props = defineProps<{
  count: number
  level: string   // "high" | "medium" | "low" | "none"
  title?: string
}>()

const badgeClass = computed(() => {
  if (props.level === 'high')   return 'bg-red-900/50 text-red-400 border-red-800/50'
  if (props.level === 'medium') return 'bg-amber-900/50 text-amber-400 border-amber-800/50'
  return 'bg-sky-900/50 text-sky-400 border-sky-800/50'
})

const dotClass = computed(() => {
  if (props.level === 'high')   return 'bg-red-400'
  if (props.level === 'medium') return 'bg-amber-400'
  return 'bg-sky-400'
})
</script>
