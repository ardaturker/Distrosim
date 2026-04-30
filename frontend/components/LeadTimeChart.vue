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
  Tooltip,
} from 'chart.js'
import type { RouteResult } from '~/stores/simulation'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip)

const props = defineProps<{ routes: RouteResult[] }>()

const chartData = computed(() => ({
  labels: props.routes.map(r => r.route_name),
  datasets: [{
    label: 'Lead Time (days)',
    data: props.routes.map(r => r.total_lead_time_days),
    backgroundColor: props.routes.map(r =>
      r.badge === 'fastest' ? 'rgba(56, 189, 248, 0.7)' : 'rgba(100, 116, 139, 0.4)'
    ),
    borderColor: props.routes.map(r =>
      r.badge === 'fastest' ? 'rgba(56, 189, 248, 1)' : 'rgba(100, 116, 139, 0.7)'
    ),
    borderWidth: 1.5,
    borderRadius: 4,
  }],
}))

const chartOptions = computed(() => ({
  indexAxis: 'y' as const,
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
          const r = props.routes[ctx.dataIndex]
          return [`${r.total_lead_time_days.toFixed(1)} days`, `$${r.total_cost_per_unit_usd.toFixed(2)}/unit`]
        },
      },
    },
  },
  scales: {
    x: {
      grid: { color: 'rgba(51,65,85,0.5)' },
      ticks: {
        color: '#64748b',
        callback: (v: number) => `${v}d`,
      },
    },
    y: {
      grid: { display: false },
      ticks: { color: '#64748b', font: { size: 11 } },
    },
  },
}))
</script>
