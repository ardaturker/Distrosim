<template>
  <div class="relative h-72">
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup lang="ts">
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import type { RouteResult } from '~/stores/simulation'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const props = defineProps<{ routes: RouteResult[] }>()

const chartData = computed(() => ({
  labels: props.routes.map(r => r.route_name.replace(' + ', '\n+')),
  datasets: [
    {
      label: 'Landed Cost (USD/unit)',
      data: props.routes.map(r => r.total_cost_per_unit_usd),
      backgroundColor: props.routes.map(r =>
        r.badge === 'cheapest' ? 'rgba(52, 211, 153, 0.6)' :
        r.badge === 'fastest'  ? 'rgba(56, 189, 248, 0.6)' :
        r.badge === 'most_reliable' ? 'rgba(251, 191, 36, 0.6)' :
        'rgba(148, 163, 184, 0.35)'
      ),
      borderColor: props.routes.map(r =>
        r.badge === 'cheapest' ? 'rgba(52, 211, 153, 0.9)' :
        r.badge === 'fastest'  ? 'rgba(56, 189, 248, 0.9)' :
        r.badge === 'most_reliable' ? 'rgba(251, 191, 36, 0.9)' :
        'rgba(148, 163, 184, 0.6)'
      ),
      borderWidth: 1.5,
      borderRadius: 4,
    },
    {
      label: 'Error Low',
      data: props.routes.map(r => r.error_low_usd),
      backgroundColor: 'transparent',
      borderColor: 'transparent',
      borderWidth: 0,
    },
    {
      label: 'Error High',
      data: props.routes.map(r => r.error_high_usd),
      backgroundColor: 'transparent',
      borderColor: 'transparent',
      borderWidth: 0,
    },
  ],
}))

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#1e293b',
      borderColor: '#334155',
      borderWidth: 1,
      titleColor: '#f8fafc',
      bodyColor: '#94a3b8',
      padding: 10,
      callbacks: {
        label: (ctx: any) => {
          if (ctx.datasetIndex !== 0) return undefined
          const r = props.routes[ctx.dataIndex]
          return [
            `Landed: $${r.total_cost_per_unit_usd.toFixed(2)}/unit`,
            `Range: $${r.error_low_usd.toFixed(2)} – $${r.error_high_usd.toFixed(2)}`,
            `Lead time: ${r.total_lead_time_days.toFixed(0)} days`,
          ]
        },
      },
    },
  },
  scales: {
    x: {
      grid: { color: 'rgba(51,65,85,0.5)' },
      ticks: { color: '#64748b', font: { size: 11 } },
    },
    y: {
      grid: { color: 'rgba(51,65,85,0.5)' },
      ticks: {
        color: '#64748b',
        callback: (v: number) => `$${v.toFixed(0)}`,
      },
    },
  },
}))
</script>
