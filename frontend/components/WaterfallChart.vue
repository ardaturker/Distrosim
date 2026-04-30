<template>
  <div class="relative">
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup lang="ts">
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend)

interface Step {
  step_id: string
  step_name: string
  cost_per_unit_usd: number
}

const props = defineProps<{ steps: Step[] }>()

// Group steps into 5 cost buckets
const BUCKETS: Record<string, { label: string; color: string; ids: string[] }> = {
  production: {
    label: 'Production',
    color: 'rgba(99,102,241,0.85)',
    ids: ['ex_works'],
  },
  freight: {
    label: 'Freight',
    color: 'rgba(251,191,36,0.85)',
    ids: ['origin_inland', 'export_customs', 'thc_origin', 'intl_freight', 'insurance', 'thc_dest', 'dest_inland'],
  },
  duties: {
    label: 'Duties & Tax',
    color: 'rgba(239,68,68,0.85)',
    ids: ['import_customs'],
  },
  warehousing: {
    label: 'Warehousing',
    color: 'rgba(34,197,94,0.85)',
    ids: ['warehousing'],
  },
  last_mile: {
    label: 'Last-Mile',
    color: 'rgba(14,165,233,0.85)',
    ids: ['last_mile'],
  },
}

const bucketTotals = computed(() => {
  const totals: Record<string, number> = {}
  for (const [key, bucket] of Object.entries(BUCKETS)) {
    totals[key] = props.steps
      .filter(s => bucket.ids.includes(s.step_id))
      .reduce((sum, s) => sum + s.cost_per_unit_usd, 0)
  }
  return totals
})

const chartData = computed(() => ({
  labels: Object.values(BUCKETS).map(b => b.label),
  datasets: [
    {
      label: 'Cost per unit (USD)',
      data: Object.keys(BUCKETS).map(k => Math.round(bucketTotals.value[k] * 100) / 100),
      backgroundColor: Object.values(BUCKETS).map(b => b.color),
      borderRadius: 6,
      borderSkipped: false,
    },
  ],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: (ctx: any) => ` $${ctx.raw.toFixed(2)} / unit`,
      },
    },
  },
  scales: {
    x: {
      grid: { color: 'rgba(255,255,255,0.05)' },
      ticks: { color: '#94a3b8' },
    },
    y: {
      grid: { color: 'rgba(255,255,255,0.05)' },
      ticks: { color: '#94a3b8', callback: (v: any) => `$${v}` },
      beginAtZero: true,
    },
  },
}
</script>
