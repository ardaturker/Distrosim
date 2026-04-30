<template>
  <div class="min-h-screen flex flex-col">
    <!-- Header -->
    <header class="border-b border-surface-800 bg-surface-900/80 backdrop-blur-sm sticky top-0 z-10">
      <div class="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-4">
          <NuxtLink to="/" class="flex items-center gap-3 hover:opacity-80 transition-opacity" title="Back to home">
            <div class="w-8 h-8 bg-brand-400 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-surface-950" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10" />
              </svg>
            </div>
            <span class="text-white font-semibold text-lg tracking-tight">DistroSim</span>
          </NuxtLink>
          <span class="text-surface-600">/</span>
          <span class="text-surface-400 text-sm">{{ t('nav_news') }}</span>
        </div>
        <nav class="flex items-center gap-3">
          <NuxtLink to="/simulator" class="text-sm text-surface-400 hover:text-white transition-colors hidden sm:inline">{{ t('nav_simulator') }}</NuxtLink>
          <NuxtLink v-if="hasResults" to="/results" class="text-sm text-surface-400 hover:text-white transition-colors hidden sm:inline">{{ t('nav_results') }}</NuxtLink>
          <button @click="refresh" :disabled="loading"
            class="text-sm border border-surface-700 hover:border-surface-500 text-surface-300 hover:text-white px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50">
            {{ loading ? t('news_loading') : t('news_refresh') }}
          </button>
          <LangToggle />
        </nav>
      </div>
    </header>

    <!-- Hero -->
    <section class="bg-surface-900 border-b border-surface-800">
      <div class="max-w-6xl mx-auto px-6 py-10">
        <div class="flex items-start justify-between gap-6">
          <div>
            <div class="inline-flex items-center gap-2 bg-sky-500/10 border border-sky-500/20 rounded-full px-3 py-1 text-sky-400 text-xs font-medium mb-4">
              <span class="w-1.5 h-1.5 bg-sky-400 rounded-full animate-pulse-slow"></span>
              {{ t('news_live_badge') }}
            </div>
            <h1 class="text-3xl font-bold text-white mb-2">{{ t('news_title') }}</h1>
            <p class="text-surface-400 max-w-xl">{{ t('news_subtitle') }}</p>
          </div>
          <!-- Port stats strip -->
          <div class="hidden md:flex gap-6 shrink-0 text-right">
            <div>
              <div class="text-xs text-surface-500 uppercase tracking-wide mb-0.5">World Rank</div>
              <div class="text-white font-semibold">#11</div>
              <div class="text-surface-500 text-xs">busiest port</div>
            </div>
            <div>
              <div class="text-xs text-surface-500 uppercase tracking-wide mb-0.5">Annual TEU</div>
              <div class="text-white font-semibold">14.6M</div>
              <div class="text-surface-500 text-xs">2023 throughput</div>
            </div>
            <div>
              <div class="text-xs text-surface-500 uppercase tracking-wide mb-0.5">Connection</div>
              <div class="text-white font-semibold">~3 days</div>
              <div class="text-surface-500 text-xs">Rotterdam → Aarhus</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Main -->
    <main class="flex-1 max-w-6xl mx-auto w-full px-6 py-8">

      <!-- Loading state -->
      <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="i in 9" :key="i" class="bg-surface-900 border border-surface-800 rounded-xl p-5 animate-pulse">
          <div class="h-3 bg-surface-700 rounded mb-3 w-1/3"></div>
          <div class="h-4 bg-surface-700 rounded mb-2"></div>
          <div class="h-4 bg-surface-700 rounded mb-2 w-4/5"></div>
          <div class="h-3 bg-surface-700 rounded mt-4 w-1/2"></div>
        </div>
      </div>

      <!-- Error state -->
      <div v-else-if="error" class="bg-red-900/20 border border-red-700/40 rounded-xl p-8 text-center">
        <div class="text-red-400 text-lg mb-2">Could not load news</div>
        <div class="text-surface-500 text-sm mb-4">{{ error }}</div>
        <button @click="refresh" class="text-sm bg-surface-800 hover:bg-surface-700 text-white px-4 py-2 rounded-lg border border-surface-700 transition-colors">
          Try again
        </button>
      </div>

      <!-- News grid -->
      <template v-else-if="data">

        <!-- Region selector -->
        <div class="mb-5">
          <div class="text-xs text-surface-500 uppercase tracking-wide font-medium mb-2">{{ t('news_region_label') }}</div>
          <div class="flex gap-2 flex-wrap">
            <button
              v-for="region in regions"
              :key="region.id"
              @click="switchRegion(region.id)"
              :class="activeRegion === region.id
                ? 'bg-brand-400 text-surface-950 border-brand-400'
                : 'bg-surface-800 text-surface-400 border-surface-700 hover:border-surface-500'"
              class="px-3 py-1.5 rounded-lg border text-sm font-medium transition-colors"
            >
              {{ lang === 'tr' ? region.label_tr : region.label }}
            </button>
          </div>
        </div>

        <!-- Category filter tabs -->
        <div class="flex items-center gap-3 mb-6 flex-wrap">
          <button v-for="cat in categories" :key="cat.value"
            @click="activeCategory = cat.value"
            :class="activeCategory === cat.value
              ? 'bg-brand-400 text-surface-950 border-brand-400'
              : 'bg-surface-800 text-surface-400 border-surface-700 hover:border-surface-500'"
            class="px-3 py-1.5 rounded-lg border text-sm font-medium transition-colors">
            {{ cat.label }}
            <span class="ml-1 opacity-70 text-xs">{{ categoryCounts[cat.value] }}</span>
          </button>
          <span class="ml-auto text-xs text-surface-600">
            {{ t('news_updated') }} {{ timeAgo(data.fetched_at) }}
          </span>
        </div>

        <!-- Live Route Intelligence panel -->
        <RoutePulse v-if="riskSignals.length" :signals="riskSignals" />

        <!-- Port-tagged banner (if any) -->
        <div v-if="rotterdamArticles.length > 0 && activeCategory === 'all'" class="mb-6">
          <div class="flex items-center gap-2 mb-3">
            <div class="w-2 h-2 bg-brand-400 rounded-full"></div>
            <span class="text-brand-400 text-xs font-semibold uppercase tracking-wide">{{ t('news_direct') }}</span>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <NewsCard v-for="a in rotterdamArticles.slice(0, 4)" :key="a.url" :article="a" highlight />
          </div>
        </div>

        <!-- All / filtered articles -->
        <div v-if="filteredArticles.length > 0">
          <div class="flex items-center gap-2 mb-3" v-if="activeCategory === 'all' && rotterdamArticles.length > 0">
            <div class="w-2 h-2 bg-surface-600 rounded-full"></div>
            <span class="text-surface-500 text-xs font-medium uppercase tracking-wide">{{ t('news_other') }}</span>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <NewsCard v-for="a in filteredArticles" :key="a.url" :article="a" />
          </div>
        </div>

        <div v-else class="text-center py-16 text-surface-600">
          {{ t('news_empty') }}
        </div>

        <!-- Sources footer -->
        <div class="mt-8 pt-6 border-t border-surface-800">
          <div class="flex flex-wrap gap-x-6 gap-y-1 text-xs text-surface-600">
            <span class="text-surface-500 font-medium">{{ t('news_sources') }}</span>
            <span v-for="s in data.sources_ok" :key="s" class="text-surface-600">{{ s }}</span>
            <span v-if="data.sources_failed.length" class="text-red-600">{{ t('news_failed') }} {{ data.sources_failed.join(', ') }}</span>
          </div>
          <p class="text-xs text-surface-700 mt-2">{{ data.note }}</p>
        </div>

      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useSimulationStore } from '~/stores/simulation'

const store = useSimulationStore()
const hasResults = computed(() => !!store.result)
const { t, lang } = useI18n()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase

interface Article {
  title: string
  summary: string
  url: string
  source: string
  category: string
  published_at: string
  relevance_score: number
  rotterdam_tagged: boolean
}

interface NewsData {
  articles: Article[]
  total: number
  sources_ok: string[]
  sources_failed: string[]
  fetched_at: string
  note: string
}

const data = ref<NewsData | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const activeCategory = ref('all')
const riskSignals = ref<any[]>([])
const activeRegion = ref('rotterdam')

interface Region { id: string; label: string; label_tr: string }
const regions = ref<Region[]>([])


const categories = computed(() => [
  { value: 'all',           label: t('news_cat_all') },
  { value: 'port_official', label: t('news_cat_port') },
  { value: 'shipping',      label: t('news_cat_shipping') },
  { value: 'container',     label: t('news_cat_container') },
  { value: 'supply_chain',  label: t('news_cat_sc') },
  { value: 'freight',       label: t('news_cat_freight') },
])

const rotterdamArticles = computed(() =>
  data.value?.articles.filter(a => a.rotterdam_tagged) ?? []
)

const filteredArticles = computed(() => {
  if (!data.value) return []
  const arts = data.value.articles.filter(a => !a.rotterdam_tagged || activeCategory.value !== 'all')
  if (activeCategory.value === 'all') return arts
  return data.value.articles.filter(a => a.category === activeCategory.value)
})

const categoryCounts = computed(() => {
  const counts: Record<string, number> = { all: data.value?.total ?? 0 }
  for (const cat of categories.value) {
    if (cat.value !== 'all') {
      counts[cat.value] = data.value?.articles.filter(a => a.category === cat.value).length ?? 0
    }
  }
  return counts
})

async function fetchNews() {
  loading.value = true
  error.value = null
  try {
    const [newsData, risksData] = await Promise.all([
      $fetch<NewsData>(`${apiBase}/news?limit=30&region=${activeRegion.value}`),
      $fetch<{ signals: any[] }>(`${apiBase}/news/risks?region=${activeRegion.value}`).catch(() => ({ signals: [] })),
    ])
    data.value = newsData
    riskSignals.value = risksData.signals ?? []
  } catch (e: any) {
    error.value = e?.data?.detail || e?.message || 'Backend not reachable'
  } finally {
    loading.value = false
  }
}

function refresh() { fetchNews() }

function switchRegion(id: string) {
  activeRegion.value = id
  activeCategory.value = 'all'
  fetchNews()
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  return `${Math.floor(hrs / 24)}d ago`
}

onMounted(async () => {
  try {
    regions.value = await $fetch<Region[]>(`${apiBase}/news/regions`)
  } catch { /* backend not running */ }
  fetchNews()
})
</script>
