import { defineStore } from 'pinia'

export interface SimulationForm {
  product_name: string
  hs_code: string
  production_cost_usd: number
  product_value_usd: number
  weight_kg: number
  length_cm: number
  width_cm: number
  height_cm: number
  annual_volume: number
  freight_mode_preference: 'all' | 'ocean' | 'air'
  last_mile_preference: 'both' | 'b2b' | 'b2c'
  weight_cost: number
  weight_time: number
  weight_reliability: number
  tariff_surcharge_pct: number
  destination_id: string
}

export interface StepResult {
  step_id: string
  step_name: string
  mode: string
  cost_per_unit_usd: number
  cost_total_usd: number
  lead_time_days: number
  source: string
  confidence: 'live' | 'cached' | 'benchmark'
  error_low_usd: number
  error_high_usd: number
  notes: string
}

export interface RiskSignal {
  route_types: string[]
  level: 'high' | 'medium' | 'low'
  label: string
  detail: string
  article_title: string
  article_url: string
  article_source: string
}

export interface RouteResult {
  route_id: string
  route_name: string
  freight_mode: string
  last_mile_type: string
  description: string
  steps: StepResult[]
  total_cost_per_unit_usd: number
  total_cost_benchmark_usd: number
  total_lead_time_days: number
  total_lead_time_benchmark_days: number
  ml_cost_multiplier: number
  ml_lead_multiplier: number
  error_low_usd: number
  error_high_usd: number
  confidence_score: number
  rank: number
  rank_score: number
  cost_score: number
  time_score: number
  reliability_score: number
  badge: string
  trade_off: string
  // CO2 (GLEC v3)
  co2_kg_per_unit?: number
  co2_breakdown?: Record<string, number>
  co2_methodology?: string
  // News × Route Intelligence
  risk_signals?: RiskSignal[]
  risk_signal_count?: number
  risk_level?: string
}

export interface RouteRiskSummary {
  total: number
  high: number
  medium: number
  low: number
  top_label: string | null
}

export interface SimulationResult {
  simulation_id: string
  timestamp: string
  elapsed_s: number
  product: { name: string; hs_code: string; annual_volume: number; weight_kg: number; value_usd: number }
  lane: { origin: string; destination: string; origin_lpi: { value: number; source: string }; dest_lpi: { value: number; source: string } }
  tariff_scenario?: { surcharge_pct: number; label: string }
  route_risk_summary?: RouteRiskSummary
  routes: RouteResult[]
  num_routes: number
  api_sources_used: string[]
  fallback_step_count: number
  data_freshness: string
}

const DEFAULT_FORM: SimulationForm = {
  product_name: 'Electronic Thermostat',
  hs_code: '9032.10',
  production_cost_usd: 8,
  product_value_usd: 35,
  weight_kg: 0.5,
  length_cm: 15,
  width_cm: 10,
  height_cm: 3,
  annual_volume: 5000,
  freight_mode_preference: 'all',
  last_mile_preference: 'both',
  weight_cost: 0.40,
  weight_time: 0.30,
  weight_reliability: 0.30,
  tariff_surcharge_pct: 0,
  destination_id: 'dk_aarhus',
}

export const useSimulationStore = defineStore('simulation', {
  state: () => ({
    form: { ...DEFAULT_FORM } as SimulationForm,
    result: null as SimulationResult | null,
    loading: false,
    error: null as string | null,
    selectedRouteIndex: 0,
    hsSuggestions: [] as { code: string; description: string; weight_kg?: number }[],
  }),

  getters: {
    selectedRoute: (state): RouteResult | null =>
      state.result?.routes?.[state.selectedRouteIndex] ?? null,

    cheapestRoute: (state): RouteResult | null =>
      state.result?.routes?.find(r => r.badge === 'cheapest') ?? state.result?.routes?.[0] ?? null,

    fastestRoute: (state): RouteResult | null =>
      state.result?.routes?.find(r => r.badge === 'fastest') ?? null,

    mostReliableRoute: (state): RouteResult | null =>
      state.result?.routes?.find(r => r.badge === 'most_reliable') ?? null,
  },

  actions: {
    async runSimulation() {
      this.loading = true
      this.error = null
      const config = useRuntimeConfig()
      const apiBase = config.public.apiBase

      try {
        const data = await $fetch<SimulationResult>(`${apiBase}/simulate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: this.form,
        })
        this.result = data
        this.selectedRouteIndex = 0
        return true
      } catch (e: any) {
        this.error = e?.data?.detail || e?.message || 'Simulation failed. Is the backend running?'
        return false
      } finally {
        this.loading = false
      }
    },

    async searchHsCodes(q: string) {
      if (q.length < 2) { this.hsSuggestions = []; return }
      const config = useRuntimeConfig()
      try {
        const data = await $fetch<{ code: string; description: string; weight_kg?: number }[]>(
          `${config.public.apiBase}/hs-codes/search`,
          { params: { q } }
        )
        this.hsSuggestions = data
      } catch {
        this.hsSuggestions = []
      }
    },

    resetForm() {
      this.form = { ...DEFAULT_FORM }
    },

    selectRoute(index: number) {
      this.selectedRouteIndex = index
    },

    encodeFormToUrl(): string {
      const encoded = btoa(JSON.stringify(this.form))
      return `?s=${encoded}`
    },

    loadFormFromUrl() {
      if (typeof window === 'undefined') return
      const params = new URLSearchParams(window.location.search)
      const s = params.get('s')
      if (!s) return
      try {
        const decoded = JSON.parse(atob(s))
        this.form = { ...DEFAULT_FORM, ...decoded }
      } catch {
        // ignore malformed URL state
      }
    },

    copyShareUrl() {
      if (typeof window === 'undefined') return
      const url = window.location.origin + '/simulator' + this.encodeFormToUrl()
      navigator.clipboard.writeText(url).catch(() => {})
      return url
    },
  },
})
