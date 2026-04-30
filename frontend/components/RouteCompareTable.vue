<template>
  <div class="overflow-x-auto rounded-xl border border-surface-800">
    <table class="w-full text-sm">
      <thead>
        <tr class="border-b border-surface-800 bg-surface-900">
          <th class="text-left px-4 py-3 text-surface-500 font-medium w-40">Metric</th>
          <th
            v-for="route in routes"
            :key="route.route_id"
            class="px-4 py-3 text-center font-medium"
            :class="route.route_id === selectedId ? 'text-brand-400' : 'text-surface-300'"
          >
            <div class="text-xs font-semibold">{{ routeShortName(route) }}</div>
            <div class="text-xs text-surface-600 font-normal">{{ route.last_mile_type === 'b2b' ? 'B2B pallet' : 'B2C parcel' }}</div>
          </th>
        </tr>
      </thead>
      <tbody>
        <!-- Total Cost -->
        <tr class="border-b border-surface-800/60">
          <td class="px-4 py-3 text-surface-500">Total cost</td>
          <td
            v-for="route in routes"
            :key="route.route_id"
            class="px-4 py-3 text-center font-semibold"
            :class="isBest(route, 'cost') ? 'text-green-400' : 'text-white'"
          >
            ${{ route.total_cost_per_unit_usd.toFixed(2) }}
            <span v-if="isBest(route, 'cost')" class="ml-1 text-xs text-green-500">best</span>
          </td>
        </tr>
        <!-- Lead Time -->
        <tr class="border-b border-surface-800/60">
          <td class="px-4 py-3 text-surface-500">Lead time</td>
          <td
            v-for="route in routes"
            :key="route.route_id"
            class="px-4 py-3 text-center"
            :class="isBest(route, 'time') ? 'text-green-400 font-semibold' : 'text-surface-300'"
          >
            {{ Math.round(route.total_lead_time_days) }}d
            <span v-if="isBest(route, 'time')" class="ml-1 text-xs text-green-500">fastest</span>
          </td>
        </tr>
        <!-- CO2 -->
        <tr class="border-b border-surface-800/60">
          <td class="px-4 py-3 text-surface-500">CO₂/unit</td>
          <td
            v-for="route in routes"
            :key="route.route_id"
            class="px-4 py-3 text-center"
            :class="isBest(route, 'co2') ? 'text-green-400 font-semibold' : 'text-surface-300'"
          >
            {{ route.co2_kg_per_unit?.toFixed(3) ?? '—' }} kg
            <span v-if="isBest(route, 'co2')" class="ml-1 text-xs text-green-500">greenest</span>
          </td>
        </tr>
        <!-- Confidence -->
        <tr class="border-b border-surface-800/60">
          <td class="px-4 py-3 text-surface-500">Confidence</td>
          <td v-for="route in routes" :key="route.route_id" class="px-4 py-3 text-center">
            <span
              class="px-2 py-0.5 rounded-full text-xs font-medium"
              :class="confidenceClass(route.confidence_score)"
            >{{ Math.round(route.confidence_score * 100) }}%</span>
          </td>
        </tr>
        <!-- Risk Signals -->
        <tr>
          <td class="px-4 py-3 text-surface-500">Live risks</td>
          <td v-for="route in routes" :key="route.route_id" class="px-4 py-3 text-center">
            <span v-if="!route.risk_signal_count" class="text-surface-600 text-xs">none</span>
            <span
              v-else
              class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold"
              :class="riskClass(route.risk_level)"
            >
              <span class="w-1.5 h-1.5 rounded-full animate-pulse" :class="riskDotClass(route.risk_level)"></span>
              {{ route.risk_signal_count }}
            </span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
interface Route {
  route_id: string
  route_name: string
  freight_mode: string
  last_mile_type: string
  total_cost_per_unit_usd: number
  total_lead_time_days: number
  co2_kg_per_unit?: number
  confidence_score: number
  risk_signal_count: number
  risk_level: string
}

const props = defineProps<{
  routes: Route[]
  selectedId?: string
}>()

function routeShortName(route: Route) {
  const m = route.freight_mode === 'ocean_fcl' ? 'FCL'
    : route.freight_mode === 'ocean_lcl' ? 'LCL'
    : 'Air'
  return m
}

function isBest(route: Route, metric: 'cost' | 'time' | 'co2') {
  if (!props.routes.length) return false
  if (metric === 'cost') return route.total_cost_per_unit_usd === Math.min(...props.routes.map(r => r.total_cost_per_unit_usd))
  if (metric === 'time') return route.total_lead_time_days === Math.min(...props.routes.map(r => r.total_lead_time_days))
  if (metric === 'co2') {
    const vals = props.routes.map(r => r.co2_kg_per_unit ?? Infinity)
    return (route.co2_kg_per_unit ?? Infinity) === Math.min(...vals)
  }
  return false
}

function confidenceClass(score: number) {
  if (score >= 0.7) return 'bg-green-900/40 text-green-400 border border-green-800/40'
  if (score >= 0.4) return 'bg-amber-900/40 text-amber-400 border border-amber-800/40'
  return 'bg-red-900/40 text-red-400 border border-red-800/40'
}

function riskClass(level: string) {
  if (level === 'high')   return 'bg-red-900/40 text-red-400 border border-red-800/40'
  if (level === 'medium') return 'bg-amber-900/40 text-amber-400 border border-amber-800/40'
  return 'bg-sky-900/40 text-sky-400 border border-sky-800/40'
}

function riskDotClass(level: string) {
  if (level === 'high')   return 'bg-red-400'
  if (level === 'medium') return 'bg-amber-400'
  return 'bg-sky-400'
}
</script>
