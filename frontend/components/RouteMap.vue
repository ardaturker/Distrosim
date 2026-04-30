<template>
  <div ref="mapEl" class="w-full rounded-xl overflow-hidden" style="height: 320px; background: #0f172a;"></div>
</template>

<script setup lang="ts">
const props = defineProps<{
  activeMode?: string      // "ocean_fcl" | "ocean_lcl" | "air"
  destinationId?: string   // e.g. "dk_aarhus", "de_hamburg", "tr_istanbul"
}>()

const config = useRuntimeConfig()
const apiBase = config.public.apiBase

const mapEl = ref<HTMLElement | null>(null)
let mapInstance: any = null

// Static intermediate waypoints along the main shipping corridor
const OCEAN_INTERMEDIATE: [number, number][] = [
  [1.3521,  103.8198],   // Singapore
  [12.3657,  43.5900],   // Aden
  [30.0626,  32.5490],   // Suez
  [38.1157,  13.3615],   // Palermo
]
const AIR_INTERMEDIATE: [number, number][] = [
  [43.0, 87.0],   // Urumqi area
  [55.0, 50.0],   // Russia
]

async function renderMap() {
  if (!mapEl.value) return

  const L = (await import('leaflet')).default

  delete (L.Icon.Default.prototype as any)._getIconUrl
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  })

  // Fetch dynamic route geometry from backend
  const destId = props.destinationId || 'dk_aarhus'
  let mapData: any = null
  try {
    mapData = await $fetch(`${apiBase}/route-map?destination_id=${destId}`)
  } catch {
    // Fallback to static Denmark coords if API is unavailable
    mapData = {
      waypoints: [
        { name: 'Shanghai (CNSHA)', lat: 31.2304, lng: 121.4737 },
        { name: 'Port of Rotterdam (NLRTM)', lat: 51.9225, lng: 4.4791 },
        { name: 'Aarhus', lat: 56.1629, lng: 10.2039 },
      ],
      air_waypoints: [
        { name: 'Shanghai Pudong (PVG)', lat: 31.1434, lng: 121.8052 },
        { name: 'Copenhagen Airport (CPH)', lat: 55.6181, lng: 12.6560 },
      ],
    }
  }

  // Extract coords from API response
  const origin    = mapData.waypoints[0]
  const hub       = mapData.waypoints[1]
  const destCity  = mapData.waypoints[2]
  const airOrigin = mapData.air_waypoints[0]
  const airDest   = mapData.air_waypoints[1]

  if (!mapInstance) {
    mapInstance = L.map(mapEl.value, {
      center: [45, 55],
      zoom: 3,
      zoomControl: true,
      scrollWheelZoom: false,
    })
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '© OpenStreetMap contributors © CARTO',
      maxZoom: 19,
    }).addTo(mapInstance)
  } else {
    // Clear non-tile layers
    mapInstance.eachLayer((layer: any) => {
      if (layer._url === undefined) mapInstance.removeLayer(layer)
    })
  }

  const isAir = props.activeMode === 'air'

  const oceanPoints: [number, number][] = [
    [origin.lat, origin.lng],
    ...OCEAN_INTERMEDIATE,
    [hub.lat, hub.lng],
    [destCity.lat, destCity.lng],
  ]

  const airPoints: [number, number][] = [
    [airOrigin.lat, airOrigin.lng],
    ...AIR_INTERMEDIATE,
    [airDest.lat, airDest.lng],
  ]

  const activePoints = isAir ? airPoints : oceanPoints
  const color = isAir ? '#38bdf8' : '#fbbf24'

  L.polyline(activePoints, {
    color,
    weight: 2.5,
    opacity: 0.85,
    dashArray: isAir ? '6 4' : undefined,
  }).addTo(mapInstance)

  // Markers
  const markerStyle = (label: string, c: string) =>
    L.divIcon({
      html: `<div style="background:${c};color:#0f172a;padding:2px 7px;border-radius:999px;font-size:11px;font-weight:700;white-space:nowrap;box-shadow:0 1px 4px #0008">${label}</div>`,
      className: '',
      iconAnchor: [0, 10],
    })

  if (isAir) {
    L.marker([airOrigin.lat, airOrigin.lng], { icon: markerStyle('PVG', '#38bdf8') }).addTo(mapInstance)
    const airCode = (airDest.name || 'DEST').split(' ')[0].replace(/[^A-Z]/g, '') || 'DEST'
    L.marker([airDest.lat, airDest.lng], { icon: markerStyle(airCode, '#38bdf8') }).addTo(mapInstance)
  } else {
    L.marker([origin.lat, origin.lng],  { icon: markerStyle('CNSHA', '#fbbf24') }).addTo(mapInstance)
    L.marker([hub.lat, hub.lng],         { icon: markerStyle('HUB',   '#fbbf24') }).addTo(mapInstance)
    L.marker([destCity.lat, destCity.lng], { icon: markerStyle('DEST', '#34d399') }).addTo(mapInstance)
  }
}

onMounted(renderMap)

onUnmounted(() => {
  mapInstance?.remove()
  mapInstance = null
})

watch([() => props.activeMode, () => props.destinationId], renderMap)
</script>
