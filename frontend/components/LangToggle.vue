<template>
  <button
    @click="toggle"
    class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-surface-700 hover:border-surface-500 text-surface-400 hover:text-white transition-colors text-sm font-medium"
    :title="lang === 'en' ? 'Switch to Turkish' : 'İngilizce\'ye geç'"
  >
    <span>{{ lang === 'en' ? '🇬🇧 EN' : '🇹🇷 TR' }}</span>
  </button>
</template>

<script setup lang="ts">
const { lang, setLang } = useI18n()
function toggle() {
  setLang(lang.value === 'en' ? 'tr' : 'en')
}
</script>
