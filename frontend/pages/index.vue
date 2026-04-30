<template>
  <div class="min-h-screen flex flex-col">

    <!-- Nav -->
    <header class="border-b border-surface-800 bg-surface-900/80 backdrop-blur-sm sticky top-0 z-10">
      <div class="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 bg-brand-400 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-surface-950" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10" />
            </svg>
          </div>
          <span class="text-white font-semibold text-lg tracking-tight">DistroSim</span>
        </div>
        <nav class="flex items-center gap-3 text-sm">
          <a href="#how-it-works" class="text-surface-400 hover:text-white transition-colors hidden md:inline">{{ t('cta_how_it_works') }}</a>
          <NuxtLink to="/news" class="text-surface-400 hover:text-white transition-colors flex items-center gap-1.5 hidden sm:flex">
            <span class="w-1.5 h-1.5 bg-sky-400 rounded-full animate-pulse-slow"></span>
            {{ t('nav_news') }}
          </NuxtLink>
          <LangToggle />
          <NuxtLink to="/simulator"
            class="bg-brand-400 hover:bg-brand-300 text-surface-950 font-semibold px-4 py-1.5 rounded-lg transition-colors text-sm">
            {{ t('cta_launch') }}
          </NuxtLink>
        </nav>
      </div>
    </header>

    <!-- Hero -->
    <section class="relative overflow-hidden bg-surface-950 border-b border-surface-800">
      <!-- Grid background -->
      <div class="absolute inset-0 bg-grid-pattern opacity-20 pointer-events-none"></div>
      <!-- Glow -->
      <div class="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-brand-400/5 rounded-full blur-3xl pointer-events-none"></div>

      <div class="relative max-w-6xl mx-auto px-6 py-24 flex flex-col items-center text-center">
        <div class="inline-flex items-center gap-2 bg-brand-400/10 border border-brand-400/20 rounded-full px-4 py-1.5 text-brand-400 text-xs font-medium mb-7">
          <span class="w-1.5 h-1.5 bg-brand-400 rounded-full"></span>
          {{ t('hero_badge') }}
        </div>

        <h1 class="text-5xl md:text-6xl font-bold text-white leading-tight mb-6 max-w-3xl">
          {{ t('hero_title_1') }}<br/>
          <span class="text-brand-400">{{ t('hero_title_2') }}</span>
        </h1>

        <p class="text-surface-400 text-lg md:text-xl leading-relaxed max-w-2xl mb-10">
          {{ t('hero_subtitle') }}
        </p>

        <div class="flex flex-col sm:flex-row gap-4 mb-16">
          <NuxtLink to="/simulator"
            class="inline-flex items-center gap-2.5 bg-brand-400 hover:bg-brand-300 text-surface-950 font-bold px-8 py-3.5 rounded-xl transition-all shadow-lg shadow-brand-400/20 text-base">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            {{ t('hero_cta_sim') }}
          </NuxtLink>
          <NuxtLink to="/news"
            class="inline-flex items-center gap-2 border border-surface-700 hover:border-surface-500 text-surface-300 hover:text-white px-8 py-3.5 rounded-xl transition-all text-base">
            <span class="w-1.5 h-1.5 bg-sky-400 rounded-full animate-pulse-slow"></span>
            {{ t('hero_cta_news') }}
          </NuxtLink>
        </div>

        <!-- Stats strip -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-px bg-surface-800 rounded-2xl overflow-hidden w-full max-w-3xl border border-surface-800">
          <div class="bg-surface-900 px-6 py-5 text-center">
            <div class="text-2xl font-bold text-white mb-1">6+</div>
            <div class="text-xs text-surface-500">{{ t('hero_stat_routes') }}</div>
          </div>
          <div class="bg-surface-900 px-6 py-5 text-center">
            <div class="text-2xl font-bold text-white mb-1">12</div>
            <div class="text-xs text-surface-500">{{ t('hero_stat_steps') }}</div>
          </div>
          <div class="bg-surface-900 px-6 py-5 text-center">
            <div class="text-2xl font-bold text-white mb-1">90%</div>
            <div class="text-xs text-surface-500">{{ t('hero_stat_ci') }}</div>
          </div>
          <div class="bg-surface-900 px-6 py-5 text-center">
            <div class="text-2xl font-bold text-white mb-1">3</div>
            <div class="text-xs text-surface-500">{{ t('hero_stat_apis') }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- How it works -->
    <section id="how-it-works" class="bg-surface-950 py-20 border-b border-surface-800">
      <div class="max-w-6xl mx-auto px-6">
        <div class="text-center mb-14">
          <div class="text-brand-400 text-xs font-semibold uppercase tracking-widest mb-3">{{ t('hiw_badge') }}</div>
          <h2 class="text-3xl font-bold text-white">{{ t('hiw_title') }}</h2>
          <p class="text-surface-400 mt-3 max-w-xl mx-auto">{{ t('hiw_subtitle') }}</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <!-- Step 1 -->
          <div class="bg-surface-900 border border-surface-800 rounded-xl p-6 relative">
            <div class="w-10 h-10 bg-brand-400/10 border border-brand-400/20 rounded-lg flex items-center justify-center mb-4">
              <span class="text-brand-400 font-bold text-lg">1</span>
            </div>
            <h3 class="text-white font-semibold mb-2">{{ t('hiw_step1_title') }}</h3>
            <p class="text-surface-500 text-sm leading-relaxed">{{ t('hiw_step1_body') }}</p>
            <div class="mt-4 pt-4 border-t border-surface-800 flex flex-wrap gap-2">
              <span class="text-xs bg-surface-800 text-surface-400 px-2 py-0.5 rounded">{{ t('hiw_step1_tag1') }}</span>
              <span class="text-xs bg-surface-800 text-surface-400 px-2 py-0.5 rounded">{{ t('hiw_step1_tag2') }}</span>
            </div>
          </div>

          <!-- Step 2 -->
          <div class="bg-surface-900 border border-surface-800 rounded-xl p-6">
            <div class="w-10 h-10 bg-sky-500/10 border border-sky-500/20 rounded-lg flex items-center justify-center mb-4">
              <span class="text-sky-400 font-bold text-lg">2</span>
            </div>
            <h3 class="text-white font-semibold mb-2">{{ t('hiw_step2_title') }}</h3>
            <p class="text-surface-500 text-sm leading-relaxed">{{ t('hiw_step2_body') }}</p>
            <div class="mt-4 pt-4 border-t border-surface-800 flex flex-wrap gap-2">
              <span class="text-xs bg-sky-500/10 text-sky-400 px-2 py-0.5 rounded border border-sky-500/20">World Bank</span>
              <span class="text-xs bg-sky-500/10 text-sky-400 px-2 py-0.5 rounded border border-sky-500/20">WTO</span>
              <span class="text-xs bg-sky-500/10 text-sky-400 px-2 py-0.5 rounded border border-sky-500/20">ECB</span>
            </div>
          </div>

          <!-- Step 3 -->
          <div class="bg-surface-900 border border-surface-800 rounded-xl p-6">
            <div class="w-10 h-10 bg-purple-500/10 border border-purple-500/20 rounded-lg flex items-center justify-center mb-4">
              <span class="text-purple-400 font-bold text-lg">3</span>
            </div>
            <h3 class="text-white font-semibold mb-2">{{ t('hiw_step3_title') }}</h3>
            <p class="text-surface-500 text-sm leading-relaxed">{{ t('hiw_step3_body') }}</p>
            <div class="mt-4 pt-4 border-t border-surface-800 flex flex-wrap gap-2">
              <span class="text-xs bg-purple-500/10 text-purple-400 px-2 py-0.5 rounded border border-purple-500/20">XGBoost</span>
              <span class="text-xs bg-purple-500/10 text-purple-400 px-2 py-0.5 rounded border border-purple-500/20">MAPIE 90% CI</span>
            </div>
          </div>

          <!-- Step 4 -->
          <div class="bg-surface-900 border border-surface-800 rounded-xl p-6">
            <div class="w-10 h-10 bg-emerald-500/10 border border-emerald-500/20 rounded-lg flex items-center justify-center mb-4">
              <span class="text-emerald-400 font-bold text-lg">4</span>
            </div>
            <h3 class="text-white font-semibold mb-2">{{ t('hiw_step4_title') }}</h3>
            <p class="text-surface-500 text-sm leading-relaxed">{{ t('hiw_step4_body') }}</p>
            <div class="mt-4 pt-4 border-t border-surface-800 flex flex-wrap gap-2">
              <span class="text-xs bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/20">{{ t('hiw_step4_tag1') }}</span>
              <span class="text-xs bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/20">{{ t('hiw_step4_tag2') }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Routes explained -->
    <section class="bg-surface-900 py-20 border-b border-surface-800">
      <div class="max-w-6xl mx-auto px-6">
        <div class="text-center mb-14">
          <div class="text-brand-400 text-xs font-semibold uppercase tracking-widest mb-3">{{ t('rc_badge') }}</div>
          <h2 class="text-3xl font-bold text-white">{{ t('rc_title') }}</h2>
          <p class="text-surface-400 mt-3 max-w-xl mx-auto">{{ t('rc_subtitle') }}</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          <!-- Ocean FCL -->
          <div class="bg-surface-950 border border-surface-800 rounded-xl p-6">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-9 h-9 bg-blue-500/10 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div>
                <div class="text-white font-semibold text-sm">{{ t('rc_fcl_title') }}</div>
                <div class="text-surface-500 text-xs">{{ t('rc_fcl_sub') }}</div>
              </div>
            </div>
            <p class="text-surface-500 text-sm leading-relaxed mb-4">{{ t('rc_fcl_body') }}</p>
            <div class="space-y-1.5">
              <div class="flex justify-between text-xs text-surface-600">
                <span>{{ t('rc_typical_cost') }}</span><span class="text-surface-400 font-mono">~$23/unit</span>
              </div>
              <div class="flex justify-between text-xs text-surface-600">
                <span>{{ t('rc_lead_time_label') }}</span><span class="text-surface-400 font-mono">~33 days</span>
              </div>
              <div class="flex justify-between text-xs text-surface-600">
                <span>{{ t('rc_lm_variants') }}</span><span class="text-surface-400">B2B + B2C</span>
              </div>
            </div>
          </div>

          <!-- Ocean LCL -->
          <div class="bg-surface-950 border border-surface-800 rounded-xl p-6">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-9 h-9 bg-teal-500/10 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-teal-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10" />
                </svg>
              </div>
              <div>
                <div class="text-white font-semibold text-sm">{{ t('rc_lcl_title') }}</div>
                <div class="text-surface-500 text-xs">{{ t('rc_lcl_sub') }}</div>
              </div>
            </div>
            <p class="text-surface-500 text-sm leading-relaxed mb-4">{{ t('rc_lcl_body') }}</p>
            <div class="space-y-1.5">
              <div class="flex justify-between text-xs text-surface-600">
                <span>{{ t('rc_typical_cost') }}</span><span class="text-surface-400 font-mono">~$25/unit</span>
              </div>
              <div class="flex justify-between text-xs text-surface-600">
                <span>{{ t('rc_lead_time_label') }}</span><span class="text-surface-400 font-mono">~38 days</span>
              </div>
              <div class="flex justify-between text-xs text-surface-600">
                <span>{{ t('rc_lm_variants') }}</span><span class="text-surface-400">B2B + B2C</span>
              </div>
            </div>
          </div>

          <!-- Air -->
          <div class="bg-surface-950 border border-surface-800 rounded-xl p-6">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-9 h-9 bg-orange-500/10 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-orange-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </div>
              <div>
                <div class="text-white font-semibold text-sm">{{ t('rc_air_title') }}</div>
                <div class="text-surface-500 text-xs">{{ t('rc_air_sub') }}</div>
              </div>
            </div>
            <p class="text-surface-500 text-sm leading-relaxed mb-4">{{ t('rc_air_body') }}</p>
            <div class="space-y-1.5">
              <div class="flex justify-between text-xs text-surface-600">
                <span>{{ t('rc_typical_cost') }}</span><span class="text-surface-400 font-mono">~$30/unit</span>
              </div>
              <div class="flex justify-between text-xs text-surface-600">
                <span>{{ t('rc_lead_time_label') }}</span><span class="text-surface-400 font-mono">~12 days</span>
              </div>
              <div class="flex justify-between text-xs text-surface-600">
                <span>{{ t('rc_lm_variants') }}</span><span class="text-surface-400">B2B + B2C</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 12-step breakdown visual -->
        <div class="bg-surface-950 border border-surface-800 rounded-xl p-6">
          <div class="text-xs text-surface-500 uppercase tracking-wide font-medium mb-4">{{ t('rc_steps_label') }}</div>
          <div class="flex flex-wrap gap-2">
            <div v-for="step in steps" :key="step.num"
              class="flex items-center gap-2 bg-surface-800 border border-surface-700 rounded-lg px-3 py-2">
              <div class="w-5 h-5 rounded text-xs flex items-center justify-center font-bold shrink-0"
                :class="step.color">{{ step.num }}</div>
              <div>
                <div class="text-white text-xs font-medium">{{ step.name }}</div>
                <div class="text-surface-600 text-xs">{{ step.note }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Data Sources -->
    <section id="data-sources" class="bg-surface-950 py-20 border-b border-surface-800">
      <div class="max-w-6xl mx-auto px-6">
        <div class="text-center mb-14">
          <div class="text-brand-400 text-xs font-semibold uppercase tracking-widest mb-3">{{ t('ds_badge') }}</div>
          <h2 class="text-3xl font-bold text-white">{{ t('ds_title') }}</h2>
          <p class="text-surface-400 mt-3 max-w-xl mx-auto">{{ t('ds_subtitle') }}</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">

          <div class="bg-surface-900 border border-surface-800 rounded-xl p-5">
            <div class="flex items-center gap-3 mb-3">
              <div class="w-8 h-8 bg-sky-500/10 rounded-lg flex items-center justify-center shrink-0">
                <svg class="w-4 h-4 text-sky-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064" />
                </svg>
              </div>
              <div>
                <div class="text-white font-semibold text-sm">World Bank LPI</div>
                <div class="text-xs text-emerald-400 font-medium">{{ t('ds_live') }}</div>
              </div>
            </div>
            <p class="text-surface-500 text-sm leading-relaxed">{{ t('ds_wb_body') }}</p>
          </div>

          <div class="bg-surface-900 border border-surface-800 rounded-xl p-5">
            <div class="flex items-center gap-3 mb-3">
              <div class="w-8 h-8 bg-sky-500/10 rounded-lg flex items-center justify-center shrink-0">
                <svg class="w-4 h-4 text-sky-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <div class="text-white font-semibold text-sm">WTO Tariff API</div>
                <div class="text-xs text-emerald-400 font-medium">{{ t('ds_live') }}</div>
              </div>
            </div>
            <p class="text-surface-500 text-sm leading-relaxed">{{ t('ds_wto_body') }}</p>
          </div>

          <div class="bg-surface-900 border border-surface-800 rounded-xl p-5">
            <div class="flex items-center gap-3 mb-3">
              <div class="w-8 h-8 bg-sky-500/10 rounded-lg flex items-center justify-center shrink-0">
                <svg class="w-4 h-4 text-sky-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <div class="text-white font-semibold text-sm">ECB Exchange Rates</div>
                <div class="text-xs text-emerald-400 font-medium">{{ t('ds_live') }}</div>
              </div>
            </div>
            <p class="text-surface-500 text-sm leading-relaxed">{{ t('ds_ecb_body') }}</p>
          </div>

          <div class="bg-surface-900 border border-surface-800 rounded-xl p-5">
            <div class="flex items-center gap-3 mb-3">
              <div class="w-8 h-8 bg-brand-400/10 rounded-lg flex items-center justify-center shrink-0">
                <svg class="w-4 h-4 text-brand-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div>
                <div class="text-white font-semibold text-sm">Freightos Baltic Index</div>
                <div class="text-xs text-brand-400 font-medium">{{ t('ds_benchmark_label') }}</div>
              </div>
            </div>
            <p class="text-surface-500 text-sm leading-relaxed">{{ t('ds_fbi_body') }}</p>
          </div>

          <div class="bg-surface-900 border border-surface-800 rounded-xl p-5">
            <div class="flex items-center gap-3 mb-3">
              <div class="w-8 h-8 bg-brand-400/10 rounded-lg flex items-center justify-center shrink-0">
                <svg class="w-4 h-4 text-brand-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </div>
              <div>
                <div class="text-white font-semibold text-sm">IATA Air Cargo Rates</div>
                <div class="text-xs text-brand-400 font-medium">{{ t('ds_benchmark_label') }}</div>
              </div>
            </div>
            <p class="text-surface-500 text-sm leading-relaxed">{{ t('ds_iata_body') }}</p>
          </div>

          <div class="bg-surface-900 border border-surface-800 rounded-xl p-5">
            <div class="flex items-center gap-3 mb-3">
              <div class="w-8 h-8 bg-sky-500/10 rounded-lg flex items-center justify-center shrink-0">
                <svg class="w-4 h-4 text-sky-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                </svg>
              </div>
              <div>
                <div class="text-white font-semibold text-sm">RSS News Feeds</div>
                <div class="text-xs text-emerald-400 font-medium">{{ t('ds_live_hourly') }}</div>
              </div>
            </div>
            <p class="text-surface-500 text-sm leading-relaxed">{{ t('ds_rss_body') }}</p>
          </div>

        </div>
      </div>
    </section>

    <!-- Demo product CTA -->
    <section class="bg-surface-900 py-20">
      <div class="max-w-6xl mx-auto px-6">
        <div class="bg-surface-950 border border-brand-400/20 rounded-2xl p-10 flex flex-col md:flex-row items-center gap-10">
          <div class="flex-1">
            <div class="text-brand-400 text-xs font-semibold uppercase tracking-widest mb-3">{{ t('demo_badge') }}</div>
            <h2 class="text-2xl font-bold text-white mb-3">{{ t('demo_title') }}</h2>
            <p class="text-surface-400 leading-relaxed mb-6">{{ t('demo_body') }}</p>
            <NuxtLink to="/simulator"
              class="inline-flex items-center gap-2.5 bg-brand-400 hover:bg-brand-300 text-surface-950 font-bold px-7 py-3 rounded-xl transition-all shadow-lg shadow-brand-400/20">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              {{ t('demo_open') }}
            </NuxtLink>
          </div>
          <!-- Demo card -->
          <div class="w-full md:w-72 bg-surface-900 border border-surface-700 rounded-xl p-5 shrink-0">
            <div class="text-xs text-surface-500 uppercase tracking-wide mb-3">{{ t('demo_prod_label') }}</div>
            <div class="text-white font-semibold mb-1">Electronic Thermostat</div>
            <div class="font-mono text-brand-400 text-sm mb-4">HS 9032.10</div>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="text-surface-500">{{ t('demo_prod_cost') }}</span>
                <span class="text-surface-300 font-mono">$8.00/unit</span>
              </div>
              <div class="flex justify-between">
                <span class="text-surface-500">{{ t('demo_prod_val') }}</span>
                <span class="text-surface-300 font-mono">$35.00/unit</span>
              </div>
              <div class="flex justify-between">
                <span class="text-surface-500">{{ t('demo_weight') }}</span>
                <span class="text-surface-300 font-mono">0.5 kg</span>
              </div>
              <div class="flex justify-between">
                <span class="text-surface-500">{{ t('demo_vol') }}</span>
                <span class="text-surface-300 font-mono">5 000 units</span>
              </div>
              <div class="flex justify-between">
                <span class="text-surface-500">{{ t('demo_duty') }}</span>
                <span class="text-surface-300 font-mono">1.7%</span>
              </div>
              <div class="flex justify-between">
                <span class="text-surface-500">{{ t('demo_vat') }}</span>
                <span class="text-surface-300 font-mono">25%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="border-t border-surface-800 py-8 px-6 bg-surface-950">
      <div class="max-w-6xl mx-auto flex flex-col md:flex-row justify-between gap-3 text-xs text-surface-600">
        <span class="text-surface-500">DistroSim — Supply Chain Distribution Simulator · China → Europe</span>
        <div class="flex flex-wrap gap-x-4 gap-y-1">
          <span>WTO Tariff API</span>
          <span>World Bank LPI</span>
          <span>ECB Exchange Rates</span>
          <span>Freightos Baltic Index</span>
          <span>IATA Air Cargo</span>
        </div>
      </div>
    </footer>

  </div>
</template>

<script setup lang="ts">
const { t } = useI18n()

const steps = computed(() => [
  { num: '1',  name: t('step_ex_works'),     note: t('step_ex_works_note'),   color: 'bg-surface-700 text-surface-400' },
  { num: '2',  name: t('step_inland_o'),     note: t('step_inland_o_note'),   color: 'bg-surface-700 text-surface-400' },
  { num: '3',  name: t('step_customs_e'),    note: t('step_customs_e_note'),  color: 'bg-surface-700 text-surface-400' },
  { num: '4',  name: t('step_thc_o'),        note: t('step_thc_o_note'),      color: 'bg-surface-700 text-surface-400' },
  { num: '5',  name: t('step_intl_freight'), note: t('step_intl_note'),       color: 'bg-blue-500/20 text-blue-400' },
  { num: '6',  name: t('step_insurance'),    note: t('step_insurance_note'),  color: 'bg-surface-700 text-surface-400' },
  { num: '7',  name: t('step_thc_d'),        note: t('step_thc_d_note'),      color: 'bg-surface-700 text-surface-400' },
  { num: '8',  name: t('step_customs_i'),    note: t('step_customs_i_note'),  color: 'bg-amber-500/20 text-amber-400' },
  { num: '9',  name: t('step_inland_d'),     note: t('step_inland_d_note'),   color: 'bg-surface-700 text-surface-400' },
  { num: '10', name: t('step_warehouse'),    note: t('step_warehouse_note'),  color: 'bg-surface-700 text-surface-400' },
  { num: '11', name: t('step_lm_b2b'),       note: t('step_lm_b2b_note'),     color: 'bg-emerald-500/20 text-emerald-400' },
  { num: '12', name: t('step_lm_b2c'),       note: t('step_lm_b2c_note'),     color: 'bg-purple-500/20 text-purple-400' },
])
</script>
