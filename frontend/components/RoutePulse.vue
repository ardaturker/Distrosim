<template>
  <div v-if="signals.length > 0" class="bg-surface-900 border border-amber-700/30 rounded-xl p-4 mb-6">
    <div class="flex items-center gap-2 mb-3">
      <span class="w-2 h-2 bg-amber-400 rounded-full animate-pulse"></span>
      <span class="text-amber-400 text-xs font-semibold uppercase tracking-wide">Live Route Intelligence</span>
      <span class="ml-auto text-xs text-surface-600">{{ signals.length }} active signal{{ signals.length !== 1 ? 's' : '' }}</span>
    </div>
    <div class="space-y-2">
      <div
        v-for="(signal, i) in signals.slice(0, maxVisible)"
        :key="i"
        class="flex items-start gap-3 text-sm"
      >
        <span
          class="mt-0.5 shrink-0 px-1.5 py-0.5 rounded text-xs font-semibold uppercase"
          :class="levelClass(signal.level)"
        >{{ signal.level }}</span>
        <div class="min-w-0">
          <span class="text-white font-medium">{{ signal.label }}</span>
          <span class="text-surface-500 ml-2 text-xs">{{ signal.detail }}</span>
          <div class="flex items-center gap-2 mt-0.5">
            <span class="text-surface-600 text-xs">{{ signal.article_source }}</span>
            <span class="text-surface-700">·</span>
            <span class="text-xs text-surface-600">Affects:</span>
            <span v-for="rt in signal.route_types" :key="rt" class="text-xs text-surface-500 bg-surface-800 px-1.5 py-0.5 rounded">{{ rt }}</span>
          </div>
        </div>
        <a
          v-if="signal.article_url"
          :href="signal.article_url"
          target="_blank"
          rel="noopener"
          class="shrink-0 text-xs text-surface-600 hover:text-brand-400 transition-colors mt-0.5"
        >↗</a>
      </div>
      <button
        v-if="signals.length > maxVisible"
        @click="maxVisible += 5"
        class="text-xs text-surface-600 hover:text-surface-400 transition-colors mt-1"
      >Show {{ signals.length - maxVisible }} more…</button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Signal {
  level: string
  label: string
  detail: string
  route_types: string[]
  article_source: string
  article_url: string
}

defineProps<{ signals: Signal[] }>()

const maxVisible = ref(5)

function levelClass(level: string) {
  if (level === 'high')   return 'bg-red-900/60 text-red-400 border border-red-800/40'
  if (level === 'medium') return 'bg-amber-900/60 text-amber-400 border border-amber-800/40'
  return 'bg-sky-900/60 text-sky-400 border border-sky-800/40'
}
</script>
