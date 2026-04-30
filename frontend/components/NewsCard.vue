<template>
  <a :href="article.url" target="_blank" rel="noopener noreferrer"
    class="group flex flex-col bg-surface-900 border rounded-xl p-5 hover:border-surface-600 transition-all duration-200 hover:-translate-y-0.5"
    :class="highlight ? 'border-brand-400/30 hover:border-brand-400/60' : 'border-surface-800'">

    <!-- Top row: source + date -->
    <div class="flex items-center justify-between gap-2 mb-3">
      <div class="flex items-center gap-2">
        <!-- Rotterdam badge -->
        <span v-if="article.rotterdam_tagged"
          class="text-xs bg-brand-400/15 text-brand-400 border border-brand-400/20 px-2 py-0.5 rounded font-medium">
          Rotterdam
        </span>
        <span class="text-xs text-surface-500 font-medium truncate max-w-[140px]">{{ article.source }}</span>
      </div>
      <span class="text-xs text-surface-600 shrink-0 font-mono">{{ formatDate(article.published_at) }}</span>
    </div>

    <!-- Title -->
    <h3 class="text-white text-sm font-semibold leading-snug mb-2 group-hover:text-brand-400 transition-colors line-clamp-3">
      {{ article.title }}
    </h3>

    <!-- Summary -->
    <p v-if="article.summary" class="text-surface-500 text-xs leading-relaxed line-clamp-3 mb-4 flex-1">
      {{ article.summary }}
    </p>

    <!-- Bottom: category + relevance -->
    <div class="flex items-center justify-between mt-auto pt-3 border-t border-surface-800">
      <span class="text-xs px-2 py-0.5 rounded-full border"
        :class="categoryStyle(article.category)">
        {{ categoryLabel(article.category) }}
      </span>
      <div class="flex items-center gap-1.5">
        <div class="w-16 h-1 bg-surface-800 rounded-full overflow-hidden">
          <div class="h-full rounded-full bg-brand-400/60" :style="{ width: article.relevance_score + '%' }"></div>
        </div>
        <span class="text-xs text-surface-600 font-mono">{{ article.relevance_score }}</span>
      </div>
    </div>
  </a>
</template>

<script setup lang="ts">
defineProps<{
  article: {
    title: string
    summary: string
    url: string
    source: string
    category: string
    published_at: string
    relevance_score: number
    rotterdam_tagged: boolean
  }
  highlight?: boolean
}>()

function formatDate(iso: string): string {
  try {
    const d = new Date(iso)
    return d.toLocaleDateString('en-DK', { day: 'numeric', month: 'short' })
  } catch {
    return ''
  }
}

function categoryLabel(cat: string): string {
  const map: Record<string, string> = {
    port_official: 'Port Official',
    shipping:      'Shipping',
    container:     'Container',
    supply_chain:  'Supply Chain',
    freight:       'Freight',
  }
  return map[cat] ?? cat
}

function categoryStyle(cat: string): string {
  const map: Record<string, string> = {
    port_official: 'bg-brand-400/10 text-brand-400 border-brand-400/20',
    shipping:      'bg-sky-500/10 text-sky-400 border-sky-500/20',
    container:     'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    supply_chain:  'bg-purple-500/10 text-purple-400 border-purple-500/20',
    freight:       'bg-orange-500/10 text-orange-400 border-orange-500/20',
  }
  return map[cat] ?? 'bg-surface-800 text-surface-400 border-surface-700'
}
</script>
