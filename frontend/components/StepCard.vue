<template>
  <div class="bg-surface-800 rounded-lg p-4 border border-surface-700 hover:border-surface-600 transition-colors">
    <!-- Step name + confidence badge -->
    <div class="flex items-start justify-between gap-2 mb-3">
      <div class="text-white text-sm font-medium leading-snug">{{ step.step_name }}</div>
      <span class="shrink-0 text-xs px-2 py-0.5 rounded font-medium"
        :class="{
          'bg-emerald-500/15 text-emerald-400': step.confidence === 'live',
          'bg-sky-500/15 text-sky-400': step.confidence === 'cached',
          'bg-surface-700 text-surface-400': step.confidence === 'benchmark',
        }">
        {{ step.confidence }}
      </span>
    </div>

    <!-- Cost + time row -->
    <div class="flex gap-4 mb-3">
      <div>
        <div class="text-xs text-surface-500 mb-0.5">Cost/unit</div>
        <div class="text-white font-mono font-semibold">${{ step.cost_per_unit_usd.toFixed(3) }}</div>
      </div>
      <div v-if="step.lead_time_days > 0">
        <div class="text-xs text-surface-500 mb-0.5">Lead time</div>
        <div class="text-white font-mono">{{ step.lead_time_days.toFixed(1) }}d</div>
      </div>
    </div>

    <!-- Error bar -->
    <div class="mb-3">
      <div class="text-xs text-surface-500 mb-1.5">90% CI range / unit</div>
      <div class="relative h-2 bg-surface-700 rounded-full overflow-hidden">
        <div class="absolute inset-y-0 rounded-full bg-brand-400/50"
          :style="{ left: errorBarLeft + '%', width: errorBarWidth + '%' }"></div>
        <!-- Current value marker -->
        <div class="absolute top-0 bottom-0 w-0.5 bg-brand-400 rounded-full"
          :style="{ left: valueMarker + '%' }"></div>
      </div>
      <div class="flex justify-between text-xs text-surface-600 mt-1 font-mono">
        <span>${{ step.error_low_usd.toFixed(3) }}</span>
        <span>${{ step.error_high_usd.toFixed(3) }}</span>
      </div>
    </div>

    <!-- Error % -->
    <div class="text-xs text-surface-500 mb-2 font-mono">
      ±{{ errorPct }}% uncertainty
    </div>

    <!-- Source -->
    <div class="text-xs text-surface-600 truncate" :title="step.source">
      <svg class="w-3 h-3 inline mr-1 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
      </svg>
      {{ step.source.split('—')[0].trim().slice(0, 50) }}
    </div>

    <!-- Notes (collapsible) -->
    <div v-if="step.notes" class="mt-2 text-xs text-surface-600 leading-relaxed line-clamp-2" :title="step.notes">
      {{ step.notes }}
    </div>
  </div>
</template>

<script setup lang="ts">
import type { StepResult } from '~/stores/simulation'

const props = defineProps<{ step: StepResult }>()

const errorPct = computed(() => {
  const cost = props.step.cost_per_unit_usd
  if (!cost) return '0.0'
  const spread = props.step.error_high_usd - props.step.error_low_usd
  return ((spread / 2 / cost) * 100).toFixed(1)
})

// Position error bar within the visual range
const errorBarLeft = computed(() => {
  const low = props.step.error_low_usd
  const high = props.step.error_high_usd
  if (high === low) return 0
  return 0  // bar always starts at left of range display
})

const errorBarWidth = computed(() => {
  // Width as % of range: (high - low) / max(high, 1) * 100
  const low = props.step.error_low_usd
  const high = props.step.error_high_usd
  if (!high) return 0
  return Math.min(100, ((high - low) / high) * 100)
})

const valueMarker = computed(() => {
  const low = props.step.error_low_usd
  const high = props.step.error_high_usd
  const val = props.step.cost_per_unit_usd
  if (high === low) return 50
  return Math.max(0, Math.min(100, ((val - low) / (high - low)) * 100))
})
</script>
