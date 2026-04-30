<template>
  <div class="overflow-x-auto pb-2">
    <div class="flex items-center gap-0 min-w-max">
      <template v-for="(step, i) in steps" :key="step.step_id">
        <!-- Step node -->
        <div class="flex flex-col items-center">
          <div class="w-28 text-center">
            <!-- Icon circle -->
            <div class="mx-auto mb-1.5 w-10 h-10 rounded-full flex items-center justify-center border-2"
              :class="confidenceClass(step.confidence)">
              <component :is="stepIcon(step.step_id)" class="w-5 h-5" />
            </div>
            <!-- Name -->
            <div class="text-xs text-surface-300 font-medium leading-tight px-1">{{ shortName(step.step_name) }}</div>
            <!-- Cost -->
            <div class="font-mono text-brand-400 text-xs mt-0.5">${{ step.cost_per_unit_usd.toFixed(2) }}</div>
            <!-- Time (skip if 0) -->
            <div v-if="step.lead_time_days > 0" class="text-surface-600 text-xs">{{ step.lead_time_days.toFixed(0) }}d</div>
          </div>
        </div>

        <!-- Connector arrow (not after last step) -->
        <div v-if="i < steps.length - 1" class="flex items-center mx-1">
          <div class="h-px w-6 bg-surface-700"></div>
          <svg class="w-3 h-3 text-surface-600 -ml-1" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { StepResult } from '~/stores/simulation'
import { defineComponent, h } from 'vue'

defineProps<{ steps: StepResult[] }>()

function confidenceClass(confidence: string) {
  if (confidence === 'live') return 'border-emerald-500/60 bg-emerald-500/10 text-emerald-400'
  if (confidence === 'cached') return 'border-sky-500/60 bg-sky-500/10 text-sky-400'
  return 'border-surface-600 bg-surface-800 text-surface-400'
}

function shortName(name: string): string {
  const map: Record<string, string> = {
    'Ex-Works (Factory)': 'Ex-Works',
    'Origin Inland Transport': 'Inland (CN)',
    'Export Customs & Docs': 'Export Customs',
    'Origin Port Handling (THC)': 'THC Origin',
    'Ocean Freight — FCL 40ft': 'Ocean FCL',
    'Ocean Freight — LCL': 'Ocean LCL',
    'Air Freight — PVG → CPH': 'Air Freight',
    'Freight Insurance': 'Insurance',
    'Destination Port Handling': 'THC Dest',
    'Import Customs & Duties (EU)': 'Import Duty',
    'Destination Inland Transport': 'Inland (DK)',
    'Warehousing (Denmark)': 'Warehouse',
  }
  for (const [key, val] of Object.entries(map)) {
    if (name.includes(key.split(' ')[0])) return val
  }
  return name.split(' ').slice(0, 2).join(' ')
}

// Simple inline SVG icon components per step type
function stepIcon(stepId: string) {
  const icons: Record<string, string> = {
    ex_works: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4',
    origin_inland: 'M5 17H3a2 2 0 01-2-2V5a2 2 0 012-2h11a2 2 0 012 2v3m-7 9h7a2 2 0 002-2v-4a2 2 0 00-2-2h-7m-3 8l-2-2m0 0l2-2m-2 2h8',
    export_customs: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    thc_origin: 'M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4',
    intl_freight: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10',
    insurance: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z',
    thc_dest: 'M3 7h18M3 7l4-4m-4 4l4 4M21 17H3m18 0l-4 4m4-4l-4-4',
    import_customs: 'M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3',
    dest_inland: 'M9 17a2 2 0 11-4 0 2 2 0 014 0zM19 17a2 2 0 11-4 0 2 2 0 014 0z M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1V8a1 1 0 011-1h2.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a1 1 0 01-1 1h-1',
    warehousing: 'M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4',
    last_mile: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
  }
  const d = icons[stepId] || icons['ex_works']
  return defineComponent({
    render() {
      return h('svg', { fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor', 'stroke-width': '1.5' },
        [h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d })]
      )
    }
  })
}
</script>
