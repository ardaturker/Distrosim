<template>
  <div class="min-h-screen flex flex-col">
    <!-- Header -->
    <header class="border-b border-surface-800 bg-surface-900/80 backdrop-blur-sm sticky top-0 z-10">
      <div class="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <NuxtLink to="/" class="flex items-center gap-3 hover:opacity-80 transition-opacity">
            <div class="w-8 h-8 bg-brand-400 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-surface-950" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10" />
              </svg>
            </div>
            <span class="text-white font-semibold text-lg tracking-tight">DistroSim</span>
          </NuxtLink>
          <span class="text-surface-700">/</span>
          <span class="text-surface-400 text-sm">{{ t('nav_simulator') }}</span>
        </div>
        <nav class="flex items-center gap-3 text-sm">
          <NuxtLink to="/news" class="text-surface-400 hover:text-white transition-colors flex items-center gap-1.5">
            <span class="w-1.5 h-1.5 bg-sky-400 rounded-full animate-pulse-slow"></span>
            <span class="hidden sm:inline">{{ t('nav_news') }}</span>
          </NuxtLink>
          <LangToggle />
        </nav>
      </div>
    </header>

    <!-- Hero -->
    <section class="bg-surface-900 border-b border-surface-800">
      <div class="max-w-6xl mx-auto px-6 py-14">
        <div class="max-w-2xl">
          <div class="inline-flex items-center gap-2 bg-brand-400/10 border border-brand-400/20 rounded-full px-3 py-1 text-brand-400 text-xs font-medium mb-5">
            <span>Shanghai → Aarhus</span>
            <span class="opacity-50">•</span>
            <span>All distribution routes</span>
            <span class="opacity-50">•</span>
            <span>ML-powered</span>
          </div>
          <h1 class="text-4xl font-bold text-white leading-tight mb-4">
            Supply Chain<br/>
            <span class="text-brand-400">Distribution Simulator</span>
          </h1>
          <p class="text-surface-400 text-lg leading-relaxed">
            Enter your product details and instantly see all possible distribution routes
            from China to Denmark — with real cost data, lead times, and ML-calibrated error margins.
          </p>
        </div>
      </div>
    </section>

    <!-- Main content -->
    <main class="flex-1 max-w-6xl mx-auto w-full px-4 md:px-6 py-10">
      <form @submit.prevent="handleSubmit" class="space-y-8">

        <!-- Product Details -->
        <section>
          <h2 class="text-white font-semibold text-base mb-5 flex items-center gap-2">
            <span class="w-6 h-6 bg-surface-800 rounded text-brand-400 text-xs flex items-center justify-center font-bold">1</span>
            Product Details
          </h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Product name -->
            <div class="md:col-span-2">
              <label class="block text-xs text-surface-400 mb-1.5 font-medium uppercase tracking-wide">Product Name</label>
              <input
                v-model="store.form.product_name"
                type="text"
                placeholder="Electronic Thermostat"
                class="w-full bg-surface-800 border border-surface-700 rounded-lg px-4 py-2.5 text-white placeholder-surface-500 focus:outline-none focus:border-brand-400 focus:ring-1 focus:ring-brand-400/30 transition-colors"
              />
            </div>

            <!-- HS Code with autocomplete -->
            <div class="relative">
              <label class="block text-xs text-surface-400 mb-1.5 font-medium uppercase tracking-wide">
                HS Code
                <span class="ml-1 text-surface-500 normal-case">(6-digit Harmonized System)</span>
              </label>
              <input
                v-model="store.form.hs_code"
                type="text"
                placeholder="9032.10"
                @input="onHsInput"
                class="w-full bg-surface-800 border border-surface-700 rounded-lg px-4 py-2.5 text-white placeholder-surface-500 focus:outline-none focus:border-brand-400 font-mono transition-colors"
              />
              <!-- Autocomplete dropdown -->
              <div
                v-if="store.hsSuggestions.length > 0"
                class="absolute z-20 left-0 right-0 top-full mt-1 bg-surface-800 border border-surface-700 rounded-lg shadow-xl overflow-hidden"
              >
                <button
                  v-for="s in store.hsSuggestions"
                  :key="s.code"
                  type="button"
                  @click="selectHs(s)"
                  class="w-full text-left px-4 py-2.5 hover:bg-surface-700 transition-colors border-b border-surface-700 last:border-0"
                >
                  <span class="font-mono text-brand-400 text-sm">{{ s.code }}</span>
                  <span class="text-surface-400 text-sm ml-3">{{ s.description }}</span>
                </button>
              </div>
            </div>

            <!-- Annual volume -->
            <div>
              <label class="block text-xs text-surface-400 mb-1.5 font-medium uppercase tracking-wide">Annual Volume <span class="text-surface-500 normal-case">(units/year)</span></label>
              <input
                v-model.number="store.form.annual_volume"
                type="number"
                min="1"
                placeholder="5000"
                class="w-full bg-surface-800 border border-surface-700 rounded-lg px-4 py-2.5 text-white placeholder-surface-500 focus:outline-none focus:border-brand-400 transition-colors"
              />
            </div>

            <!-- Costs -->
            <div>
              <label class="block text-xs text-surface-400 mb-1.5 font-medium uppercase tracking-wide">Production Cost <span class="text-surface-500 normal-case">(USD/unit)</span></label>
              <div class="relative">
                <span class="absolute left-3 top-1/2 -translate-y-1/2 text-surface-500">$</span>
                <input
                  v-model.number="store.form.production_cost_usd"
                  type="number"
                  step="0.01"
                  min="0"
                  placeholder="8.00"
                  class="w-full bg-surface-800 border border-surface-700 rounded-lg pl-7 pr-4 py-2.5 text-white placeholder-surface-500 focus:outline-none focus:border-brand-400 transition-colors"
                />
              </div>
            </div>

            <div>
              <label class="block text-xs text-surface-400 mb-1.5 font-medium uppercase tracking-wide">Declared Product Value <span class="text-surface-500 normal-case">(USD/unit, for duty calc)</span></label>
              <div class="relative">
                <span class="absolute left-3 top-1/2 -translate-y-1/2 text-surface-500">$</span>
                <input
                  v-model.number="store.form.product_value_usd"
                  type="number"
                  step="0.01"
                  min="0"
                  placeholder="35.00"
                  class="w-full bg-surface-800 border border-surface-700 rounded-lg pl-7 pr-4 py-2.5 text-white placeholder-surface-500 focus:outline-none focus:border-brand-400 transition-colors"
                />
              </div>
            </div>
          </div>
        </section>

        <!-- Physical Dimensions -->
        <section>
          <h2 class="text-white font-semibold text-base mb-5 flex items-center gap-2">
            <span class="w-6 h-6 bg-surface-800 rounded text-brand-400 text-xs flex items-center justify-center font-bold">2</span>
            Physical Dimensions <span class="text-surface-500 font-normal text-sm">(per unit)</span>
          </h2>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <label class="block text-xs text-surface-400 mb-1.5 font-medium uppercase tracking-wide">Weight <span class="text-surface-500 normal-case">(kg)</span></label>
              <input v-model.number="store.form.weight_kg" type="number" step="0.01" min="0.001" placeholder="0.5"
                class="w-full bg-surface-800 border border-surface-700 rounded-lg px-4 py-2.5 text-white placeholder-surface-500 focus:outline-none focus:border-brand-400 transition-colors" />
            </div>
            <div>
              <label class="block text-xs text-surface-400 mb-1.5 font-medium uppercase tracking-wide">Length <span class="text-surface-500 normal-case">(cm)</span></label>
              <input v-model.number="store.form.length_cm" type="number" step="0.1" min="0.1" placeholder="15"
                class="w-full bg-surface-800 border border-surface-700 rounded-lg px-4 py-2.5 text-white placeholder-surface-500 focus:outline-none focus:border-brand-400 transition-colors" />
            </div>
            <div>
              <label class="block text-xs text-surface-400 mb-1.5 font-medium uppercase tracking-wide">Width <span class="text-surface-500 normal-case">(cm)</span></label>
              <input v-model.number="store.form.width_cm" type="number" step="0.1" min="0.1" placeholder="10"
                class="w-full bg-surface-800 border border-surface-700 rounded-lg px-4 py-2.5 text-white placeholder-surface-500 focus:outline-none focus:border-brand-400 transition-colors" />
            </div>
            <div>
              <label class="block text-xs text-surface-400 mb-1.5 font-medium uppercase tracking-wide">Height <span class="text-surface-500 normal-case">(cm)</span></label>
              <input v-model.number="store.form.height_cm" type="number" step="0.1" min="0.1" placeholder="3"
                class="w-full bg-surface-800 border border-surface-700 rounded-lg px-4 py-2.5 text-white placeholder-surface-500 focus:outline-none focus:border-brand-400 transition-colors" />
            </div>
          </div>
          <div v-if="cbmDisplay" class="mt-3 text-xs text-surface-500 font-mono">
            Volume: {{ cbmDisplay }} CBM/unit
          </div>
        </section>

        <!-- Destination -->
        <section>
          <h2 class="text-white font-semibold text-base mb-5 flex items-center gap-2">
            <span class="w-6 h-6 bg-surface-800 rounded text-brand-400 text-xs flex items-center justify-center font-bold">3</span>
            {{ t('sec_destination') }}
            <span class="text-surface-500 font-normal text-sm">— {{ t('lbl_dest_select') }}</span>
          </h2>
          <div v-if="destinations.length" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
            <button
              v-for="dest in destinations"
              :key="dest.id"
              type="button"
              @click="store.form.destination_id = dest.id"
              :class="store.form.destination_id === dest.id
                ? 'bg-brand-400/15 border-brand-400 text-white'
                : 'bg-surface-800 border-surface-700 hover:border-surface-500 text-surface-300'"
              class="flex items-center gap-2 px-3 py-2.5 rounded-lg border text-sm font-medium transition-colors text-left"
            >
              <span class="text-base">{{ dest.flag }}</span>
              <span class="text-xs leading-tight">{{ lang === 'tr' ? dest.name_tr : dest.name }}</span>
            </button>
          </div>
          <div v-else class="text-surface-600 text-sm">Loading destinations…</div>
        </section>

        <!-- Route Preferences -->
        <section>
          <h2 class="text-white font-semibold text-base mb-5 flex items-center gap-2">
            <span class="w-6 h-6 bg-surface-800 rounded text-brand-400 text-xs flex items-center justify-center font-bold">4</span>
            {{ t('sec_route_prefs') }}
          </h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Freight mode -->
            <div>
              <label class="block text-xs text-surface-400 mb-2 font-medium uppercase tracking-wide">Freight Mode</label>
              <div class="flex gap-2 flex-wrap">
                <button v-for="opt in freightModeOptions" :key="opt.value" type="button"
                  @click="store.form.freight_mode_preference = opt.value"
                  :class="store.form.freight_mode_preference === opt.value
                    ? 'bg-brand-400 text-surface-950 border-brand-400'
                    : 'bg-surface-800 text-surface-300 border-surface-700 hover:border-surface-500'"
                  class="px-4 py-2 rounded-lg border text-sm font-medium transition-colors">
                  {{ opt.label }}
                </button>
              </div>
            </div>

            <!-- Last mile -->
            <div>
              <label class="block text-xs text-surface-400 mb-2 font-medium uppercase tracking-wide">Last-Mile Delivery</label>
              <div class="flex gap-2 flex-wrap">
                <button v-for="opt in lastMileOptions" :key="opt.value" type="button"
                  @click="store.form.last_mile_preference = opt.value"
                  :class="store.form.last_mile_preference === opt.value
                    ? 'bg-brand-400 text-surface-950 border-brand-400'
                    : 'bg-surface-800 text-surface-300 border-surface-700 hover:border-surface-500'"
                  class="px-4 py-2 rounded-lg border text-sm font-medium transition-colors">
                  {{ opt.label }}
                </button>
              </div>
            </div>
          </div>
        </section>

        <!-- ML Weights -->
        <section>
          <h2 class="text-white font-semibold text-base mb-5 flex items-center gap-2">
            <span class="w-6 h-6 bg-surface-800 rounded text-brand-400 text-xs flex items-center justify-center font-bold">5</span>
            {{ t('sec_ranking') }}
          </h2>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div v-for="w in weightSliders" :key="w.key">
              <div class="flex justify-between items-center mb-2">
                <label class="text-sm text-surface-300">{{ w.label }}</label>
                <span class="font-mono text-brand-400 text-sm">{{ Math.round(store.form[w.key] * 100) }}%</span>
              </div>
              <input
                type="range" min="0" max="1" step="0.05"
                :value="store.form[w.key]"
                @input="updateWeight(w.key, $event)"
                class="w-full h-1.5 bg-surface-700 rounded-full appearance-none cursor-pointer accent-amber-400"
              />
            </div>
          </div>
        </section>

        <!-- Tariff Scenario -->
        <section>
          <h2 class="text-white font-semibold text-base mb-5 flex items-center gap-2">
            <span class="w-6 h-6 bg-surface-800 rounded text-brand-400 text-xs flex items-center justify-center font-bold">6</span>
            {{ t('sec_tariff') }}
            <span class="text-surface-500 font-normal text-sm">({{ t('tariff_note') }})</span>
          </h2>
          <div class="flex gap-2 flex-wrap">
            <button
              v-for="opt in tariffOptions"
              :key="opt.pct"
              type="button"
              @click="store.form.tariff_surcharge_pct = opt.pct"
              :class="store.form.tariff_surcharge_pct === opt.pct
                ? 'bg-brand-400 text-surface-950 border-brand-400'
                : 'bg-surface-800 text-surface-300 border-surface-700 hover:border-surface-500'"
              class="px-4 py-2 rounded-lg border text-sm font-medium transition-colors"
            >
              {{ opt.label }}
            </button>
          </div>
          <div v-if="store.form.tariff_surcharge_pct > 0" class="mt-3 text-xs text-amber-400/80 flex items-center gap-1.5">
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            +{{ store.form.tariff_surcharge_pct }}% applied to import duties on all routes
          </div>
        </section>

        <!-- Error message -->
        <div v-if="store.error" class="bg-red-900/30 border border-red-700/50 rounded-lg px-5 py-4 text-red-400 text-sm">
          {{ store.error }}
        </div>

        <!-- Submit + Share -->
        <div class="pt-2 flex flex-col sm:flex-row gap-3 items-start">
          <button
            type="submit"
            :disabled="store.loading"
            class="w-full sm:w-auto inline-flex items-center justify-center gap-3 bg-brand-400 hover:bg-brand-300 disabled:opacity-60 disabled:cursor-not-allowed text-surface-950 font-bold px-10 py-3.5 rounded-xl transition-all text-base shadow-lg shadow-brand-400/20"
          >
            <template v-if="store.loading">
              <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              {{ t('btn_running') }}
            </template>
            <template v-else>
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              {{ t('btn_run') }}
            </template>
          </button>

          <!-- Share button -->
          <button
            type="button"
            @click="handleShare"
            class="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-surface-800 hover:bg-surface-700 border border-surface-700 text-surface-300 hover:text-white font-medium px-5 py-3.5 rounded-xl transition-all text-sm"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
            </svg>
            {{ shareCopied ? t('btn_copied') : t('btn_share') }}
          </button>
        </div>

      </form>
    </main>

    <!-- Footer -->
    <footer class="border-t border-surface-800 mt-auto py-6 px-6">
      <div class="max-w-6xl mx-auto flex flex-col md:flex-row justify-between gap-2 text-xs text-surface-600">
        <span>DistroSim — Supply Chain Distribution Simulator</span>
        <span>Data sources: WTO Tariff API · World Bank LPI · ECB Exchange Rates · Industry benchmarks (Freightos, IATA, CBRE)</span>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { useSimulationStore } from '~/stores/simulation'

const store = useSimulationStore()
const router = useRouter()
const { t, lang } = useI18n()
const config = useRuntimeConfig()

interface Destination { id: string; name: string; name_tr: string; flag: string }
const destinations = ref<Destination[]>([])

onMounted(async () => {
  store.loadFormFromUrl()
  try {
    destinations.value = await $fetch<Destination[]>(`${config.public.apiBase}/destinations`)
  } catch { /* backend not running yet */ }
})

const freightModeOptions = [
  { value: 'all',   label: 'All Modes' },
  { value: 'ocean', label: 'Ocean Only' },
  { value: 'air',   label: 'Air Only' },
]

const lastMileOptions = [
  { value: 'both', label: 'B2B + B2C' },
  { value: 'b2b',  label: 'B2B Pallet' },
  { value: 'b2c',  label: 'B2C Parcel' },
]

const weightSliders = [
  { key: 'weight_cost' as const,        label: 'Cost Priority' },
  { key: 'weight_time' as const,        label: 'Speed Priority' },
  { key: 'weight_reliability' as const, label: 'Reliability Priority' },
]

const tariffOptions = [
  { pct: 0,  label: 'Standard (MFN only)' },
  { pct: 25, label: 'China +301 (+25%)' },
  { pct: 50, label: 'Custom +50%' },
  { pct: 100, label: 'Custom +100%' },
]

const cbmDisplay = computed(() => {
  const { length_cm, width_cm, height_cm } = store.form
  if (!length_cm || !width_cm || !height_cm) return null
  const cbm = (length_cm * width_cm * height_cm) / 1_000_000
  return cbm.toFixed(5)
})

let hsDebounce: ReturnType<typeof setTimeout> | null = null
function onHsInput(e: Event) {
  const val = (e.target as HTMLInputElement).value
  store.form.hs_code = val
  if (hsDebounce) clearTimeout(hsDebounce)
  hsDebounce = setTimeout(() => store.searchHsCodes(val), 300)
}

function selectHs(s: { code: string; description: string; weight_kg?: number }) {
  store.form.hs_code = s.code
  if (s.weight_kg) store.form.weight_kg = s.weight_kg
  store.hsSuggestions = []
}

function updateWeight(key: 'weight_cost' | 'weight_time' | 'weight_reliability', e: Event) {
  store.form[key] = parseFloat((e.target as HTMLInputElement).value)
}

async function handleSubmit() {
  const ok = await store.runSimulation()
  if (ok) router.push('/results')
}

const shareCopied = ref(false)
function handleShare() {
  store.copyShareUrl()
  shareCopied.value = true
  setTimeout(() => { shareCopied.value = false }, 2000)
}
</script>
