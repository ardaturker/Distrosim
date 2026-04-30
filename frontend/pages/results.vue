<template>
  <div class="min-h-screen flex flex-col">
    <!-- Header -->
    <header class="border-b border-surface-800 bg-surface-900/80 backdrop-blur-sm sticky top-0 z-10">
      <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-4">
          <NuxtLink to="/simulator" class="flex items-center gap-3 hover:opacity-80 transition-opacity">
            <div class="w-8 h-8 bg-brand-400 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-surface-950" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10" />
              </svg>
            </div>
            <span class="text-white font-semibold text-lg tracking-tight">DistroSim</span>
          </NuxtLink>
          <span class="text-surface-600">/</span>
          <span class="text-surface-400 text-sm">Results</span>
        </div>
        <div class="flex items-center gap-3 flex-wrap">
          <span v-if="result" class="text-surface-500 text-xs font-mono hidden sm:inline">{{ result.num_routes }} routes · {{ result.elapsed_s }}s</span>
          <!-- Risk indicator in header -->
          <span
            v-if="result?.route_risk_summary?.total"
            class="inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border"
            :class="result.route_risk_summary.high > 0
              ? 'bg-red-900/30 text-red-400 border-red-800/40'
              : 'bg-amber-900/30 text-amber-400 border-amber-800/40'"
          >
            <span class="w-1.5 h-1.5 rounded-full animate-pulse"
              :class="result.route_risk_summary.high > 0 ? 'bg-red-400' : 'bg-amber-400'"></span>
            {{ result.route_risk_summary.total }} live risk{{ result.route_risk_summary.total !== 1 ? 's' : '' }}
          </span>
          <button @click="exportCSV" class="text-sm text-surface-400 hover:text-white border border-surface-700 hover:border-surface-500 rounded-lg px-3 py-1.5 transition-colors hidden sm:inline">
            Export CSV
          </button>
          <NuxtLink to="/news" class="text-sm text-surface-400 hover:text-white transition-colors flex items-center gap-1.5">
            <span class="w-1.5 h-1.5 bg-sky-400 rounded-full animate-pulse-slow"></span>
            <span class="hidden sm:inline">Rotterdam News</span>
          </NuxtLink>
          <LangToggle />
          <NuxtLink to="/simulator" class="text-sm bg-surface-800 hover:bg-surface-700 text-white rounded-lg px-4 py-1.5 transition-colors border border-surface-700">
            {{ t('nav_new_sim') }}
          </NuxtLink>
        </div>
      </div>
    </header>

    <!-- No result guard -->
    <div v-if="!result" class="flex-1 flex flex-col items-center justify-center gap-4 text-surface-500">
      <svg class="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <p>No simulation results yet.</p>
      <NuxtLink to="/simulator" class="text-brand-400 hover:underline text-sm">Run a simulation →</NuxtLink>
    </div>

    <template v-else>
      <main class="flex-1 max-w-7xl mx-auto w-full px-4 md:px-6 py-8 space-y-6 animate-fade-in">

        <!-- Live Intelligence Panel (News × Route Intelligence) -->
        <RoutePulse v-if="allRiskSignals.length" :signals="allRiskSignals" />

        <!-- Summary bar -->
        <div class="bg-surface-900 border border-surface-800 rounded-xl p-5 flex flex-col md:flex-row md:items-center gap-4 md:gap-8 flex-wrap">
          <div>
            <div class="text-xs text-surface-500 uppercase tracking-wide mb-0.5">Product</div>
            <div class="text-white font-semibold">{{ result.product.name }}</div>
            <div class="font-mono text-brand-400 text-sm">HS {{ result.product.hs_code }}</div>
          </div>
          <div class="h-px md:h-10 md:w-px bg-surface-700"></div>
          <div>
            <div class="text-xs text-surface-500 uppercase tracking-wide mb-0.5">Lane</div>
            <div class="text-white text-sm">{{ result.lane.origin }}</div>
            <div class="text-surface-400 text-sm">→ {{ result.lane.destination }}</div>
          </div>
          <div class="h-px md:h-10 md:w-px bg-surface-700"></div>
          <div>
            <div class="text-xs text-surface-500 uppercase tracking-wide mb-0.5">Volume</div>
            <div class="text-white font-semibold">{{ result.product.annual_volume.toLocaleString() }} units/year</div>
            <div class="text-surface-400 text-sm">{{ result.product.weight_kg }}kg · ${{ result.product.value_usd }}/unit value</div>
          </div>
          <!-- Tariff scenario badge -->
          <div v-if="result.tariff_scenario?.surcharge_pct" class="h-px md:h-10 md:w-px bg-surface-700"></div>
          <div v-if="result.tariff_scenario?.surcharge_pct">
            <div class="text-xs text-surface-500 uppercase tracking-wide mb-0.5">Tariff Scenario</div>
            <div class="inline-flex items-center gap-1.5 px-2 py-1 bg-amber-900/30 border border-amber-800/40 rounded-lg text-amber-400 text-sm font-medium">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              {{ result.tariff_scenario.label }}
            </div>
          </div>
          <div class="h-px md:h-10 md:w-px bg-surface-700"></div>
          <div class="flex gap-6">
            <div>
              <div class="text-xs text-surface-500 mb-0.5">Origin LPI</div>
              <div class="text-white font-mono">{{ result.lane.origin_lpi.value }}</div>
            </div>
            <div>
              <div class="text-xs text-surface-500 mb-0.5">Dest LPI</div>
              <div class="text-white font-mono">{{ result.lane.dest_lpi.value }}</div>
            </div>
          </div>
        </div>

        <!-- Top route cards -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div v-if="store.cheapestRoute" class="bg-surface-900 border border-emerald-700/40 rounded-xl p-5 relative overflow-hidden">
            <div class="absolute top-0 right-0 bg-emerald-500/10 text-emerald-400 text-xs font-bold px-3 py-1 rounded-bl-lg">CHEAPEST</div>
            <div class="text-surface-400 text-xs uppercase tracking-wide mb-1">Lowest landed cost</div>
            <div class="text-2xl font-bold text-white">${{ store.cheapestRoute.total_cost_per_unit_usd.toFixed(2) }}<span class="text-sm text-surface-500 font-normal">/unit</span></div>
            <div class="text-surface-400 text-sm mt-1">{{ store.cheapestRoute.route_name }}</div>
            <div class="text-surface-500 text-xs mt-1">Range: ${{ store.cheapestRoute.error_low_usd.toFixed(2) }} – ${{ store.cheapestRoute.error_high_usd.toFixed(2) }}</div>
            <div v-if="store.cheapestRoute.co2_kg_per_unit" class="text-surface-600 text-xs mt-1">
              🌿 {{ store.cheapestRoute.co2_kg_per_unit.toFixed(3) }} kg CO₂e/unit
            </div>
          </div>
          <div v-if="store.fastestRoute" class="bg-surface-900 border border-sky-700/40 rounded-xl p-5 relative overflow-hidden">
            <div class="absolute top-0 right-0 bg-sky-500/10 text-sky-400 text-xs font-bold px-3 py-1 rounded-bl-lg">FASTEST</div>
            <div class="text-surface-400 text-xs uppercase tracking-wide mb-1">Shortest lead time</div>
            <div class="text-2xl font-bold text-white">{{ store.fastestRoute.total_lead_time_days.toFixed(0) }}<span class="text-sm text-surface-500 font-normal"> days</span></div>
            <div class="text-surface-400 text-sm mt-1">{{ store.fastestRoute.route_name }}</div>
            <div class="text-surface-500 text-xs mt-1">${{ store.fastestRoute.total_cost_per_unit_usd.toFixed(2) }}/unit landed cost</div>
            <div v-if="store.fastestRoute.co2_kg_per_unit" class="text-surface-600 text-xs mt-1">
              🌿 {{ store.fastestRoute.co2_kg_per_unit.toFixed(3) }} kg CO₂e/unit
            </div>
          </div>
          <div v-if="store.mostReliableRoute" class="bg-surface-900 border border-brand-400/30 rounded-xl p-5 relative overflow-hidden">
            <div class="absolute top-0 right-0 bg-brand-400/10 text-brand-400 text-xs font-bold px-3 py-1 rounded-bl-lg">MOST RELIABLE</div>
            <div class="text-surface-400 text-xs uppercase tracking-wide mb-1">Highest ML confidence</div>
            <div class="text-2xl font-bold text-white">{{ (store.mostReliableRoute.confidence_score * 100).toFixed(0) }}<span class="text-sm text-surface-500 font-normal">% conf.</span></div>
            <div class="text-surface-400 text-sm mt-1">{{ store.mostReliableRoute.route_name }}</div>
            <div class="text-surface-500 text-xs mt-1">${{ store.mostReliableRoute.total_cost_per_unit_usd.toFixed(2) }}/unit · {{ store.mostReliableRoute.total_lead_time_days.toFixed(0) }} days</div>
          </div>
        </div>

        <!-- Charts + Map tabs -->
        <div class="bg-surface-900 border border-surface-800 rounded-xl overflow-hidden">
          <div class="flex border-b border-surface-800">
            <button v-for="tab in chartTabs" :key="tab.id"
              @click="activeChartTab = tab.id"
              :class="activeChartTab === tab.id ? 'text-white border-b-2 border-brand-400' : 'text-surface-500 hover:text-surface-300'"
              class="px-5 py-3 text-sm font-medium transition-colors">
              {{ tab.label }}
            </button>
          </div>
          <div class="p-6">
            <div v-show="activeChartTab === 'cost'" style="height: 260px;">
              <CostChart :routes="result.routes" />
            </div>
            <div v-show="activeChartTab === 'time'" style="height: 260px;">
              <LeadTimeChart :routes="result.routes" />
            </div>
            <div v-show="activeChartTab === 'waterfall'" style="height: 260px;">
              <WaterfallChart v-if="store.selectedRoute" :steps="store.selectedRoute.steps" />
            </div>
            <div v-show="activeChartTab === 'map'">
              <ClientOnly>
                <RouteMap :active-mode="store.selectedRoute?.freight_mode" :destination-id="result?.lane?.destination_id" />
                <template #fallback>
                  <div class="h-80 bg-surface-800 rounded-xl flex items-center justify-center text-surface-600 text-sm">Loading map…</div>
                </template>
              </ClientOnly>
            </div>
            <p v-if="activeChartTab === 'waterfall'" class="text-xs text-surface-600 mt-3">
              Waterfall for: {{ store.selectedRoute?.route_name }} — select a route tab below to update.
            </p>
          </div>
        </div>

        <!-- Side-by-Side Route Comparison -->
        <div class="bg-surface-900 border border-surface-800 rounded-xl overflow-hidden">
          <div class="px-6 py-4 border-b border-surface-800">
            <h3 class="text-white font-semibold text-sm">Route Comparison</h3>
            <p class="text-surface-500 text-xs mt-0.5">All routes side-by-side. Green = best in category.</p>
          </div>
          <div class="p-4">
            <RouteCompareTable :routes="result.routes" :selected-id="store.selectedRoute?.route_id" />
          </div>
        </div>

        <!-- Route selector + detail -->
        <div class="bg-surface-900 border border-surface-800 rounded-xl overflow-hidden">
          <!-- Route tabs with risk badges -->
          <div class="flex overflow-x-auto border-b border-surface-800">
            <button
              v-for="(r, i) in result.routes"
              :key="r.route_id"
              @click="store.selectRoute(i)"
              :class="store.selectedRouteIndex === i
                ? 'text-white border-b-2 border-brand-400 bg-surface-800'
                : 'text-surface-500 hover:text-surface-300 hover:bg-surface-800/50'"
              class="px-4 py-3 text-sm font-medium whitespace-nowrap transition-colors flex items-center gap-2"
            >
              <span class="w-5 h-5 rounded-full text-xs flex items-center justify-center font-bold"
                :class="store.selectedRouteIndex === i ? 'bg-brand-400 text-surface-950' : 'bg-surface-700 text-surface-400'">
                {{ r.rank }}
              </span>
              <span class="hidden sm:inline">{{ r.route_name }}</span>
              <span class="sm:hidden">{{ routeShortLabel(r) }}</span>
              <span v-if="r.badge" class="text-xs px-1.5 py-0.5 rounded font-normal hidden md:inline"
                :class="{
                  'bg-emerald-500/15 text-emerald-400': r.badge === 'cheapest',
                  'bg-sky-500/15 text-sky-400': r.badge === 'fastest',
                  'bg-brand-400/15 text-brand-400': r.badge === 'most_reliable'
                }">
                {{ r.badge.replace('_', ' ') }}
              </span>
              <!-- Risk badge on tab -->
              <RiskBadge
                v-if="r.risk_signal_count"
                :count="r.risk_signal_count"
                :level="r.risk_level || 'low'"
                :title="`${r.risk_signal_count} live risk signal(s) on this route`"
              />
            </button>
          </div>

          <div v-if="store.selectedRoute" class="p-6 space-y-6">
            <!-- Route header -->
            <div class="flex flex-col md:flex-row md:items-start gap-4 justify-between">
              <div>
                <h3 class="text-white text-lg font-semibold">{{ store.selectedRoute.route_name }}</h3>
                <p class="text-surface-400 text-sm mt-1">{{ store.selectedRoute.description }}</p>
              </div>
              <div class="flex gap-4 sm:gap-6 shrink-0 flex-wrap">
                <div class="text-right">
                  <div class="text-xs text-surface-500 uppercase tracking-wide">Landed Cost</div>
                  <div class="text-xl font-bold text-white">${{ store.selectedRoute.total_cost_per_unit_usd.toFixed(2) }}/unit</div>
                  <div class="text-xs text-surface-500">range ${{ store.selectedRoute.error_low_usd.toFixed(2) }}–${{ store.selectedRoute.error_high_usd.toFixed(2) }}</div>
                </div>
                <div class="text-right">
                  <div class="text-xs text-surface-500 uppercase tracking-wide">Lead Time</div>
                  <div class="text-xl font-bold text-white">{{ store.selectedRoute.total_lead_time_days.toFixed(0) }} days</div>
                </div>
                <!-- CO2 KPI -->
                <div v-if="store.selectedRoute.co2_kg_per_unit" class="text-right">
                  <div class="text-xs text-surface-500 uppercase tracking-wide">CO₂/unit</div>
                  <div class="text-xl font-bold text-emerald-400">{{ store.selectedRoute.co2_kg_per_unit.toFixed(3) }} kg</div>
                  <div class="text-xs text-surface-500">CO₂e · GLEC v3</div>
                </div>
                <div class="text-right">
                  <div class="text-xs text-surface-500 uppercase tracking-wide">ML Confidence</div>
                  <ConfidenceBar :score="store.selectedRoute.confidence_score" />
                </div>
              </div>
            </div>

            <!-- Route-level risk signals (if any) -->
            <div
              v-if="store.selectedRoute.risk_signals?.length"
              class="bg-amber-900/10 border border-amber-800/30 rounded-lg px-4 py-3"
            >
              <div class="flex items-center gap-2 mb-2">
                <span class="w-1.5 h-1.5 bg-amber-400 rounded-full animate-pulse"></span>
                <span class="text-amber-400 text-xs font-semibold uppercase tracking-wide">Route Risk Signals</span>
                <span class="ml-auto text-xs text-surface-600">from live news</span>
              </div>
              <div class="space-y-1.5">
                <div v-for="sig in store.selectedRoute.risk_signals?.slice(0, 3)" :key="sig.label" class="flex items-start gap-2 text-xs">
                  <span class="mt-0.5 shrink-0 px-1.5 py-0.5 rounded text-xs font-semibold uppercase"
                    :class="sig.level === 'high' ? 'bg-red-900/60 text-red-400' : sig.level === 'medium' ? 'bg-amber-900/60 text-amber-400' : 'bg-sky-900/60 text-sky-400'">
                    {{ sig.level }}
                  </span>
                  <span class="text-white font-medium">{{ sig.label }}</span>
                  <span class="text-surface-500">{{ sig.detail }}</span>
                  <a v-if="sig.article_url" :href="sig.article_url" target="_blank" class="ml-auto shrink-0 text-surface-600 hover:text-brand-400">↗</a>
                </div>
              </div>
            </div>

            <!-- Route tree -->
            <RouteTree :steps="store.selectedRoute.steps" />

            <!-- Step cards -->
            <div class="space-y-3">
              <h4 class="text-surface-400 text-xs uppercase tracking-wide font-medium">Step-by-Step Breakdown</h4>
              <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
                <StepCard
                  v-for="step in store.selectedRoute.steps"
                  :key="step.step_id"
                  :step="step"
                />
              </div>
            </div>

            <!-- CO2 breakdown -->
            <div v-if="store.selectedRoute.co2_breakdown" class="bg-surface-800 rounded-lg px-4 py-3 text-xs text-surface-500">
              <span class="text-emerald-400 font-medium">CO₂ breakdown</span>
              ({{ store.selectedRoute.co2_methodology }}):
              <span class="ml-2">Origin road: {{ store.selectedRoute.co2_breakdown.origin_inland?.toFixed(4) }} kg</span>
              <span class="ml-2">Intl freight: {{ store.selectedRoute.co2_breakdown.intl_freight?.toFixed(4) }} kg</span>
              <span class="ml-2">Dest road: {{ store.selectedRoute.co2_breakdown.dest_inland?.toFixed(4) }} kg</span>
            </div>

            <!-- ML adjustments note -->
            <div class="bg-surface-800 rounded-lg px-4 py-3 text-xs text-surface-500 flex gap-2">
              <svg class="w-4 h-4 text-brand-400 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.347.347a3.003 3.003 0 01-4.95 0l-.347-.347z" />
              </svg>
              ML adjusted cost: ×{{ store.selectedRoute.ml_cost_multiplier.toFixed(3) }} &nbsp;|&nbsp;
              ML adjusted lead time: ×{{ store.selectedRoute.ml_lead_multiplier.toFixed(3) }} &nbsp;|&nbsp;
              Based on World Bank LPI (origin: {{ result.lane.origin_lpi.value }}, dest: {{ result.lane.dest_lpi.value }})
            </div>
          </div>
        </div>

        <!-- Data transparency panel -->
        <details class="bg-surface-900 border border-surface-800 rounded-xl overflow-hidden">
          <summary class="px-6 py-4 cursor-pointer text-surface-400 text-sm font-medium hover:text-white transition-colors flex items-center gap-2">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Data Transparency — Sources &amp; Freshness
          </summary>
          <div class="px-6 pb-5 pt-2 border-t border-surface-800 space-y-3">
            <div class="text-xs text-surface-500">{{ result.data_freshness }}</div>
            <div>
              <div class="text-xs text-surface-500 uppercase tracking-wide mb-2">API Sources Used</div>
              <div class="flex flex-wrap gap-2">
                <span v-for="s in result.api_sources_used" :key="s"
                  class="bg-surface-800 text-surface-300 text-xs px-2.5 py-1 rounded-md font-mono">{{ s }}</span>
              </div>
            </div>
            <div class="text-xs text-surface-600">
              {{ result.fallback_step_count }} step(s) used benchmark fallback data.
              Simulation ID: {{ result.simulation_id }} · {{ new Date(result.timestamp).toLocaleString() }}
            </div>
          </div>
        </details>

      </main>
    </template>
  </div>
</template>

<script setup lang="ts">
import { useSimulationStore } from '~/stores/simulation'
import type { RiskSignal } from '~/stores/simulation'

const store = useSimulationStore()
const result = computed(() => store.result)
const { t } = useI18n()

// Deduplicate all risk signals across all routes for the RoutePulse panel
const allRiskSignals = computed((): RiskSignal[] => {
  if (!result.value) return []
  const seen = new Set<string>()
  const out: RiskSignal[] = []
  for (const route of result.value.routes) {
    for (const sig of route.risk_signals ?? []) {
      const key = sig.label + '|' + sig.article_url
      if (!seen.has(key)) {
        seen.add(key)
        out.push(sig)
      }
    }
  }
  return out
})

const chartTabs = computed(() => [
  { id: 'cost',      label: t('chart_cost') },
  { id: 'time',      label: t('chart_time') },
  { id: 'waterfall', label: t('chart_waterfall') },
  { id: 'map',       label: t('chart_map') },
])
const activeChartTab = ref('cost')

function routeShortLabel(r: any) {
  const m = r.freight_mode === 'ocean_fcl' ? 'FCL' : r.freight_mode === 'ocean_lcl' ? 'LCL' : 'Air'
  const l = r.last_mile_type === 'b2b' ? 'B2B' : 'B2C'
  return `${m} ${l}`
}

function exportCSV() {
  if (!result.value) return
  const rows: string[] = ['Route,Landed Cost (USD/unit),Lead Time (days),CO2 (kg/unit),Confidence Score,Error Low,Error High,Badge']
  for (const r of result.value.routes) {
    rows.push([
      `"${r.route_name}"`,
      r.total_cost_per_unit_usd.toFixed(2),
      r.total_lead_time_days.toFixed(1),
      r.co2_kg_per_unit?.toFixed(3) ?? '',
      r.confidence_score.toFixed(1),
      r.error_low_usd.toFixed(2),
      r.error_high_usd.toFixed(2),
      r.badge,
    ].join(','))
  }
  const blob = new Blob([rows.join('\n')], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `distrosim-${result.value.simulation_id}.csv`
  a.click()
  URL.revokeObjectURL(url)
}
</script>
