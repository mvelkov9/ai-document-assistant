<script setup>
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

  defineProps({
    data: { type: Object, required: true },
    options: { type: Object, default: () => ({}) },
  })
</script>

<template>
  <Bar :data="data" :options="options" />
</template>
