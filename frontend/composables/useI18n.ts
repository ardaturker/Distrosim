/**
 * Minimal i18n — English / Turkish toggle.
 * Usage: const { t, lang, setLang } = useI18n()
 *        {{ t('run_simulation') }}
 */

type Lang = 'en' | 'tr'

const TRANSLATIONS: Record<string, Record<Lang, string>> = {
  // ── Navigation ────────────────────────────────────────────────────────────
  nav_simulator:        { en: 'Simulator',          tr: 'Simülatör' },
  nav_news:             { en: 'Port News',           tr: 'Liman Haberleri' },
  nav_results:          { en: 'Results',             tr: 'Sonuçlar' },
  nav_new_sim:          { en: '← New Simulation',   tr: '← Yeni Simülasyon' },
  nav_lane:             { en: 'China → Destination', tr: 'Çin → Varış Noktası' },

  // ── Landing page ─────────────────────────────────────────────────────────
  hero_badge:           { en: 'China → Europe & Beyond',  tr: 'Çin → Avrupa ve Ötesi' },
  hero_title_1:         { en: 'Distribution Cost',        tr: 'Dağıtım Maliyet' },
  hero_title_2:         { en: 'Simulator',                tr: 'Simülatörü' },
  hero_subtitle:        { en: 'Calculate real landed costs, lead times, and carbon footprint for any route from China — powered by live APIs and ML models.', tr: 'Çin\'den herhangi bir rotaya gerçek teslim maliyetlerini, teslimat sürelerini ve karbon ayak izini hesaplayın — canlı API\'ler ve ML modelleri ile güçlendirilmiştir.' },
  cta_try_now:          { en: 'Try it now →',             tr: 'Hemen dene →' },
  cta_view_news:        { en: 'View port news',           tr: 'Liman haberlerini gör' },

  // ── Simulator form ────────────────────────────────────────────────────────
  sim_title:            { en: 'Distribution Simulator',   tr: 'Dağıtım Simülatörü' },
  sim_subtitle:         { en: 'Enter your product details and see all distribution routes from China — with live cost data and ML-calibrated error margins.', tr: 'Ürün detaylarınızı girin ve Çin\'den tüm dağıtım rotalarını görün — canlı maliyet verileri ve ML ile kalibre edilmiş hata aralıkları ile.' },

  sec_product:          { en: 'Product Details',          tr: 'Ürün Detayları' },
  sec_dimensions:       { en: 'Physical Dimensions',      tr: 'Fiziksel Boyutlar' },
  sec_per_unit:         { en: 'per unit',                 tr: 'birim başına' },
  sec_destination:      { en: 'Destination',              tr: 'Varış Noktası' },
  sec_route_prefs:      { en: 'Route Preferences',        tr: 'Rota Tercihleri' },
  sec_ranking:          { en: 'Ranking Priority',         tr: 'Sıralama Önceliği' },
  sec_tariff:           { en: 'Tariff Scenario',          tr: 'Tarife Senaryosu' },
  tariff_note:          { en: 'duty surcharge on top of WTO MFN rate', tr: 'WTO MFN oranına ek gümrük vergisi' },

  lbl_product_name:     { en: 'Product Name',             tr: 'Ürün Adı' },
  lbl_hs_code:          { en: 'HS Code',                  tr: 'HS Kodu' },
  lbl_hs_hint:          { en: '6-digit Harmonized System', tr: '6 haneli Uyumlaştırılmış Sistem' },
  lbl_annual_vol:       { en: 'Annual Volume',            tr: 'Yıllık Hacim' },
  lbl_units_year:       { en: 'units/year',               tr: 'birim/yıl' },
  lbl_prod_cost:        { en: 'Production Cost',          tr: 'Üretim Maliyeti' },
  lbl_usd_unit:         { en: 'USD/unit',                 tr: 'USD/birim' },
  lbl_value:            { en: 'Declared Product Value',   tr: 'Beyan Edilen Ürün Değeri' },
  lbl_value_hint:       { en: 'USD/unit, for duty calc',  tr: 'USD/birim, gümrük hesabı için' },
  lbl_weight:           { en: 'Weight',                   tr: 'Ağırlık' },
  lbl_length:           { en: 'Length',                   tr: 'Uzunluk' },
  lbl_width:            { en: 'Width',                    tr: 'Genişlik' },
  lbl_height:           { en: 'Height',                   tr: 'Yükseklik' },
  lbl_freight_mode:     { en: 'Freight Mode',             tr: 'Taşıma Modu' },
  lbl_last_mile:        { en: 'Last-Mile Delivery',       tr: 'Son Mil Teslimat' },
  lbl_cost_priority:    { en: 'Cost Priority',            tr: 'Maliyet Önceliği' },
  lbl_speed_priority:   { en: 'Speed Priority',           tr: 'Hız Önceliği' },
  lbl_rel_priority:     { en: 'Reliability Priority',     tr: 'Güvenilirlik Önceliği' },

  freight_all:          { en: 'All Modes',                tr: 'Tüm Modlar' },
  freight_ocean:        { en: 'Ocean Only',               tr: 'Sadece Deniz' },
  freight_air:          { en: 'Air Only',                 tr: 'Sadece Hava' },

  last_mile_both:       { en: 'B2B + B2C',               tr: 'B2B + B2C' },
  last_mile_b2b:        { en: 'B2B Pallet',              tr: 'B2B Palet' },
  last_mile_b2c:        { en: 'B2C Parcel',              tr: 'B2C Paket' },

  tariff_standard:      { en: 'Standard (MFN only)',      tr: 'Standart (Sadece MFN)' },
  tariff_301:           { en: 'China +301 (+25%)',        tr: 'Çin +301 (+%25)' },
  tariff_50:            { en: 'Custom +50%',              tr: 'Özel +%50' },
  tariff_100:           { en: 'Custom +100%',             tr: 'Özel +%100' },

  btn_run:              { en: 'Run Simulation',           tr: 'Simülasyonu Başlat' },
  btn_running:          { en: 'Simulating Routes…',       tr: 'Rotalar Simüle Ediliyor…' },
  btn_share:            { en: 'Share Setup',              tr: 'Ayarları Paylaş' },
  btn_copied:           { en: 'Link Copied!',             tr: 'Bağlantı Kopyalandı!' },

  lbl_dest_select:      { en: 'Choose destination country/port', tr: 'Varış noktası ülke/limanı seçin' },

  // ── Results page ──────────────────────────────────────────────────────────
  res_product:          { en: 'Product',                  tr: 'Ürün' },
  res_lane:             { en: 'Lane',                     tr: 'Güzergah' },
  res_volume:           { en: 'Volume',                   tr: 'Hacim' },
  res_tariff:           { en: 'Tariff Scenario',          tr: 'Tarife Senaryosu' },
  res_landed_cost:      { en: 'Landed Cost',              tr: 'Teslim Maliyeti' },
  res_lead_time:        { en: 'Lead Time',                tr: 'Teslim Süresi' },
  res_co2:              { en: 'CO₂/unit',                 tr: 'CO₂/birim' },
  res_confidence:       { en: 'ML Confidence',            tr: 'ML Güven' },
  res_cheapest:         { en: 'CHEAPEST',                 tr: 'EN UCUZ' },
  res_fastest:          { en: 'FASTEST',                  tr: 'EN HIZLI' },
  res_reliable:         { en: 'MOST RELIABLE',            tr: 'EN GÜVENİLİR' },
  res_lowest_cost:      { en: 'Lowest landed cost',       tr: 'En düşük teslim maliyeti' },
  res_shortest_lead:    { en: 'Shortest lead time',       tr: 'En kısa teslim süresi' },
  res_highest_conf:     { en: 'Highest ML confidence',    tr: 'En yüksek ML güveni' },
  res_comparison:       { en: 'Route Comparison',         tr: 'Rota Karşılaştırması' },
  res_comparison_sub:   { en: 'All routes side-by-side. Green = best in category.', tr: 'Tüm rotalar yan yana. Yeşil = kategoride en iyi.' },
  res_export_csv:       { en: 'Export CSV',               tr: 'CSV İndir' },
  res_data_sources:     { en: 'Data Transparency — Sources & Freshness', tr: 'Veri Şeffaflığı — Kaynaklar ve Tazelik' },
  res_live_risks:       { en: 'Live Route Intelligence',  tr: 'Canlı Rota İstihbaratı' },
  res_new_sim:          { en: '← New Simulation',         tr: '← Yeni Simülasyon' },

  chart_cost:           { en: 'Cost Chart',               tr: 'Maliyet Grafiği' },
  chart_time:           { en: 'Lead Time',                tr: 'Teslim Süresi' },
  chart_waterfall:      { en: 'Cost Waterfall',           tr: 'Maliyet Şelalesi' },
  chart_map:            { en: 'Route Map',                tr: 'Rota Haritası' },

  // ── News page ─────────────────────────────────────────────────────────────
  news_title:           { en: 'Port Supply Chain News',   tr: 'Liman Tedarik Zinciri Haberleri' },
  news_subtitle:        { en: 'Live port updates, freight rate movements, and container shipping news relevant to your route.', tr: 'Rotanızla ilgili canlı liman güncellemeleri, navlun fiyat hareketleri ve konteyner taşımacılığı haberleri.' },
  news_live_badge:      { en: 'Live RSS · Updated hourly', tr: 'Canlı RSS · Saatlik Güncelleme' },
  news_region_label:    { en: 'Select Port / Region',     tr: 'Liman / Bölge Seçin' },
  news_direct:          { en: 'Port Direct',              tr: 'Doğrudan Liman' },
  news_other:           { en: 'Other Supply Chain News',  tr: 'Diğer Tedarik Zinciri Haberleri' },
  news_empty:           { en: 'No articles in this category right now.', tr: 'Bu kategoride şu an haber yok.' },
  news_sources:         { en: 'Sources:',                 tr: 'Kaynaklar:' },
  news_failed:          { en: 'Failed:',                  tr: 'Başarısız:' },
  news_refresh:         { en: 'Refresh',                  tr: 'Yenile' },
  news_loading:         { en: 'Loading…',                 tr: 'Yükleniyor…' },
  news_updated:         { en: 'Updated',                  tr: 'Güncellendi' },
  news_cat_all:         { en: 'All',                      tr: 'Tümü' },
  news_cat_port:        { en: 'Port Official',            tr: 'Resmi Liman' },
  news_cat_shipping:    { en: 'Shipping',                 tr: 'Denizcilik' },
  news_cat_container:   { en: 'Container',                tr: 'Konteyner' },
  news_cat_sc:          { en: 'Supply Chain',             tr: 'Tedarik Zinciri' },
  news_cat_freight:     { en: 'Freight',                  tr: 'Kargo' },

  // ── Risk / Intelligence ──────────────────────────────────────────────────
  risk_live_intel:      { en: 'Live Route Intelligence',  tr: 'Canlı Rota İstihbaratı' },
  risk_signals:         { en: 'active signal',            tr: 'aktif sinyal' },
  risk_signals_pl:      { en: 'active signals',           tr: 'aktif sinyal' },
  risk_route_signals:   { en: 'Route Risk Signals',       tr: 'Rota Risk Sinyalleri' },
  risk_from_news:       { en: 'from live news',           tr: 'canlı haberlerden' },
  risk_affects:         { en: 'Affects:',                 tr: 'Etkiler:' },
  risk_live:            { en: 'live risks',               tr: 'canlı risk' },

  // ── Landing page — hero ──────────────────────────────────────────────────
  hero_cta_sim:         { en: 'Run a Free Simulation',   tr: 'Ücretsiz Simülasyon Çalıştır' },
  hero_cta_news:        { en: 'Port News',               tr: 'Liman Haberleri' },
  hero_stat_routes:     { en: 'Route Variants',          tr: 'Rota Varyantı' },
  hero_stat_steps:      { en: 'Cost Steps Modelled',     tr: 'Maliyet Adımı' },
  hero_stat_ci:         { en: 'Prediction Intervals',    tr: 'Tahmin Aralıkları' },
  hero_stat_apis:       { en: 'Live Free APIs',          tr: 'Canlı Ücretsiz API' },

  // ── Landing page — How It Works ──────────────────────────────────────────
  hiw_badge:            { en: 'How It Works',            tr: 'Nasıl Çalışır' },
  hiw_title:            { en: 'From product details to full cost breakdown', tr: 'Ürün detaylarından tam maliyet dökümüne' },
  hiw_subtitle:         { en: 'Four steps from input to decision-ready output — no paid subscriptions or manual research required.', tr: 'Girişten karar verilmeye hazır çıktıya dört adım — ücretli abonelik veya manuel araştırma gerektirmez.' },
  hiw_step1_title:      { en: 'Enter Product Details',   tr: 'Ürün Detaylarını Girin' },
  hiw_step1_body:       { en: 'Provide your product name, HS code, production cost, declared value, dimensions, weight, and annual volume. A thermostat example is pre-filled so you can try immediately.', tr: 'Ürün adınızı, HS kodunu, üretim maliyetini, beyan edilen değeri, boyutları, ağırlığı ve yıllık hacmi girin. Hemen denemek için bir termostat örneği önceden doldurulmuştur.' },
  hiw_step1_tag1:       { en: 'HS Code lookup',          tr: 'HS Kodu arama' },
  hiw_step1_tag2:       { en: 'CBM calculator',          tr: 'CBM hesaplayıcı' },
  hiw_step2_title:      { en: 'Live Data is Fetched',    tr: 'Canlı Veriler Alınıyor' },
  hiw_step2_body:       { en: 'The backend calls three free APIs in parallel: World Bank LPI scores for origin and destination, WTO MFN tariff rates for your HS code, and ECB exchange rates for accurate currency conversion.', tr: 'Arka uç üç ücretsiz API\'yi paralel çağırır: kalkış ve varış için World Bank LPI puanları, HS kodunuz için WTO MFN tarife oranları ve ECB döviz kurları.' },
  hiw_step3_title:      { en: 'ML Adjusts the Estimates', tr: 'ML Tahminleri Ayarlıyor' },
  hiw_step3_body:       { en: 'XGBoost models (trained at startup on 600 synthetic samples) apply cost and lead-time multipliers based on LPI scores, product weight, and volume. MAPIE conformal prediction generates calibrated 90% intervals.', tr: 'XGBoost modelleri (600 sentetik örnekle eğitilmiş), LPI puanları, ürün ağırlığı ve hacmine göre çarpanlar uygular. MAPIE uyumlu tahmin kalibre edilmiş %90 aralıklar üretir.' },
  hiw_step4_title:      { en: 'Routes Are Ranked',       tr: 'Rotalar Sıralanıyor' },
  hiw_step4_body:       { en: 'All 6+ routes are ranked by your chosen priorities: cost (40%), speed (30%), and reliability (30%). The cheapest, fastest, and most reliable routes are highlighted with a full step-by-step breakdown.', tr: '6+ rota seçtiğiniz önceliklere göre sıralanır: maliyet (%40), hız (%30) ve güvenilirlik (%30). En ucuz, en hızlı ve en güvenilir rotalar adım adım döküm ile vurgulanır.' },
  hiw_step4_tag1:       { en: 'Adjustable weights',      tr: 'Ayarlanabilir ağırlıklar' },
  hiw_step4_tag2:       { en: 'Export CSV',              tr: 'CSV İndir' },

  // ── Landing page — Route Coverage ────────────────────────────────────────
  rc_badge:             { en: 'Route Coverage',          tr: 'Rota Kapsamı' },
  rc_title:             { en: 'Every viable route, modelled in full', tr: 'Her uygulanabilir rota, tam olarak modellendi' },
  rc_subtitle:          { en: 'Each route is broken into up to 12 individual cost steps — from ex-works to the final doorstep delivery.', tr: 'Her rota, fabrikadan kapıya teslimatına kadar 12 ayrı maliyet adımına bölünmüştür.' },
  rc_fcl_title:         { en: 'Ocean FCL',               tr: 'Deniz FCL' },
  rc_fcl_sub:           { en: 'Full Container Load',     tr: 'Tam Konteyner Yükü' },
  rc_fcl_body:          { en: 'Dedicated 40ft container via hub port. Lowest cost per unit for volumes above ~800 units, longest transit at ~30 days.', tr: 'Hub limanı üzerinden özel 40 ft konteyner. ~800 birim üzeri hacimlerde en düşük birim maliyeti, ~30 gün transit.' },
  rc_lcl_title:         { en: 'Ocean LCL',               tr: 'Deniz LCL' },
  rc_lcl_sub:           { en: 'Less than Container Load', tr: 'Konteyner Doldurmayan Yük' },
  rc_lcl_body:          { en: 'Shared container, billed by CBM. Ideal for smaller volumes. Adds consolidation/deconsolidation time but avoids paying for empty container space.', tr: 'Paylaşımlı konteyner, CBM\'e göre faturalanır. Küçük hacimler için ideal. Konsolidasyon süresi ekler ancak boş konteyner alanı ödemeyi önler.' },
  rc_air_title:         { en: 'Air Freight',             tr: 'Hava Kargo' },
  rc_air_sub:           { en: 'PVG → Destination airport', tr: 'PVG → Varış Havalimanı' },
  rc_air_body:          { en: 'Fastest option at ~7–12 days total. Billed by chargeable weight. Best for high-value, time-critical, or light products.', tr: 'Toplam ~7–12 gün en hızlı seçenek. Yüksek değerli veya zamana duyarlı ürünler için idealdir.' },
  rc_typical_cost:      { en: 'Typical cost',            tr: 'Tipik maliyet' },
  rc_lead_time_label:   { en: 'Lead time',               tr: 'Teslim süresi' },
  rc_lm_variants:       { en: 'Last-mile variants',      tr: 'Son mil varyantları' },
  rc_steps_label:       { en: 'The 12 Cost Steps Modelled per Ocean Route', tr: 'Deniz Rotası Başına Modellenen 12 Maliyet Adımı' },

  // ── Landing page — step names (visual strip) ─────────────────────────────
  step_ex_works:        { en: 'Ex-Works',                tr: 'Ex-Works' },
  step_ex_works_note:   { en: 'Factory gate cost',       tr: 'Fabrika kapı maliyeti' },
  step_inland_o:        { en: 'Origin Inland',           tr: 'Kalkış İç Taşıma' },
  step_inland_o_note:   { en: 'Factory → port',          tr: 'Fabrika → liman' },
  step_customs_e:       { en: 'Export Customs',          tr: 'İhracat Gümrüğü' },
  step_customs_e_note:  { en: 'CN export broker',        tr: 'CN ihracat komisyoncusu' },
  step_thc_o:           { en: 'THC Origin',              tr: 'Kalkış THC' },
  step_thc_o_note:      { en: 'Port handling (CNSHA)',   tr: 'Liman işleme (CNSHA)' },
  step_intl_freight:    { en: 'Intl. Freight',           tr: 'Uluslararası Kargo' },
  step_intl_note:       { en: 'Ocean FCL/LCL/Air',       tr: 'Deniz FCL/LCL/Hava' },
  step_insurance:       { en: 'Insurance',               tr: 'Sigorta' },
  step_insurance_note:  { en: 'CIF 0.3%',                tr: 'CIF %0.3' },
  step_thc_d:           { en: 'THC Destination',         tr: 'Varış THC' },
  step_thc_d_note:      { en: 'Port handling (hub)',     tr: 'Liman işleme (hub)' },
  step_customs_i:       { en: 'Import Customs',          tr: 'İthalat Gümrüğü' },
  step_customs_i_note:  { en: 'MFN + VAT',               tr: 'MFN + KDV' },
  step_inland_d:        { en: 'Dest. Inland',            tr: 'Varış İç Taşıma' },
  step_inland_d_note:   { en: 'Port → warehouse',        tr: 'Liman → depo' },
  step_warehouse:       { en: 'Warehousing',             tr: 'Depolama' },
  step_warehouse_note:  { en: '30-day storage',          tr: '30 günlük depolama' },
  step_lm_b2b:          { en: 'Last-Mile B2B',           tr: 'Son Mil B2B' },
  step_lm_b2b_note:     { en: 'Pallet to distributor',  tr: 'Distribütöre palet' },
  step_lm_b2c:          { en: 'Last-Mile B2C',           tr: 'Son Mil B2C' },
  step_lm_b2c_note:     { en: 'Parcel to customer',      tr: 'Müşteriye paket' },

  // ── Landing page — Data Sources ──────────────────────────────────────────
  ds_badge:             { en: 'Data Transparency',       tr: 'Veri Şeffaflığı' },
  ds_title:             { en: 'Where the numbers come from', tr: 'Sayılar nereden geliyor' },
  ds_subtitle:          { en: 'Every data point is sourced, stamped, and labelled as live, cached, or benchmark so you always know how fresh it is.', tr: 'Her veri noktası kaynaklanmış, damgalanmış ve canlı, önbellekli veya kıyaslama olarak etiketlenmiştir.' },
  ds_wb_body:           { en: 'Logistics Performance Index scores for China and destination country. Used to calibrate ML cost and lead-time multipliers. Cached 7 days.', tr: 'Çin ve varış ülkesi için Lojistik Performans Endeksi puanları. ML maliyet ve teslimat süresi çarpanlarını kalibre etmek için kullanılır. 7 gün önbellek.' },
  ds_wto_body:          { en: 'Most-Favoured-Nation (MFN) duty rate for your HS code. Falls back to benchmark chapter rates if API is unavailable. Cached 24 hours.', tr: 'HS kodunuz için En Çok Kayrılan Ülke (MFN) gümrük oranı. API kullanılamıyorsa kıyaslama bölüm oranlarına döner. 24 saat önbellek.' },
  ds_ecb_body:          { en: 'EUR/CNY and EUR/local rates from the European Central Bank SDMX REST API. Used for accurate CNY→USD cost conversion. Cached 1 hour.', tr: 'Avrupa Merkez Bankası SDMX REST API\'sinden EUR/CNY ve EUR/yerel kurlar. CNY→USD maliyet dönüşümü için kullanılır. 1 saat önbellek.' },
  ds_fbi_body:          { en: 'Ocean FCL/LCL freight rate benchmarks for the China–North Europe lane. Used as the base rate when live freight APIs are not configured.', tr: 'Çin–Kuzey Avrupa hattı için Deniz FCL/LCL navlun oranı kıyaslamaları. Canlı navlun API\'leri yapılandırılmadığında temel oran olarak kullanılır.' },
  ds_iata_body:         { en: 'Air freight rate benchmarks ($/kg) for the China–Europe corridor. Combined with volumetric weight calculation for accurate air cost estimates.', tr: 'Çin–Avrupa koridoru için hava kargo oranı kıyaslamaları ($/kg). Hacimsel ağırlık hesaplamasıyla birleştirilir.' },
  ds_rss_body:          { en: 'Port news and supply chain RSS feeds — aggregated, filtered for relevance, and cached 1 hour. Powers the News × Route Intelligence risk signals.', tr: 'Liman haberleri ve tedarik zinciri RSS beslemeleri — toplanmış, filtrelenmiş ve 1 saat önbelleklenmiş. Haber × Rota İstihbaratı risk sinyallerini destekler.' },
  ds_live:              { en: 'Live API · Free',         tr: 'Canlı API · Ücretsiz' },
  ds_benchmark_label:   { en: 'Benchmark · Q1 2024',     tr: 'Kıyaslama · Q1 2024' },
  ds_live_hourly:       { en: 'Live · Updated hourly',   tr: 'Canlı · Saatlik Güncelleme' },

  // ── Landing page — Demo CTA ──────────────────────────────────────────────
  demo_badge:           { en: 'Try It Now',              tr: 'Hemen Dene' },
  demo_title:           { en: 'Pre-filled demo: Electronic Thermostat', tr: 'Önceden doldurulmuş demo: Elektronik Termostat' },
  demo_body:            { en: 'The simulator opens with a realistic thermostat (HS 9032.10, 0.5 kg, $35 value, 5 000 units/year). Hit "Run Simulation" and get 6 ranked routes with live duty rates, LPI-adjusted costs, and 90% confidence intervals — in under 5 seconds.', tr: 'Simülatör gerçekçi bir termostat (HS 9032.10, 0,5 kg, $35 değer, yılda 5.000 birim) ile açılır. 5 saniyeden kısa sürede 6 sıralı rota alın.' },
  demo_open:            { en: 'Open Simulator',          tr: 'Simülatörü Aç' },
  demo_prod_cost:       { en: 'Production cost',         tr: 'Üretim maliyeti' },
  demo_prod_val:        { en: 'Product value',           tr: 'Ürün değeri' },
  demo_weight:          { en: 'Weight',                  tr: 'Ağırlık' },
  demo_vol:             { en: 'Annual volume',           tr: 'Yıllık hacim' },
  demo_duty:            { en: 'MFN duty (EU)',           tr: 'MFN gümrük (AB)' },
  demo_vat:             { en: 'Destination VAT',         tr: 'Varış KDV\'si' },
  demo_prod_label:      { en: 'Demo Product',            tr: 'Demo Ürün' },

  // ── Landing page nav ─────────────────────────────────────────────────────
  cta_how_it_works:     { en: 'How it works',            tr: 'Nasıl çalışır' },
  cta_launch:           { en: 'Launch Simulator',        tr: 'Simülatörü Aç' },

  // ── Common ────────────────────────────────────────────────────────────────
  days:                 { en: 'days',                     tr: 'gün' },
  per_unit:             { en: '/unit',                    tr: '/birim' },
  range:                { en: 'Range:',                   tr: 'Aralık:' },
  no_results:           { en: 'No simulation results yet.', tr: 'Henüz simülasyon sonucu yok.' },
  run_one:              { en: 'Run a simulation →',       tr: 'Bir simülasyon başlat →' },
  loading_map:          { en: 'Loading map…',             tr: 'Harita yükleniyor…' },
  conf_score:           { en: '% conf.',                  tr: '% güven' },
  best:                 { en: 'best',                     tr: 'en iyi' },
  fastest_label:        { en: 'fastest',                  tr: 'en hızlı' },
  greenest:             { en: 'greenest',                 tr: 'en yeşil' },
  none:                 { en: 'none',                     tr: 'yok' },
  show_more:            { en: 'Show',                     tr: 'Daha fazla göster' },
  more_suffix:          { en: 'more…',                    tr: '' },

  lbl_world_rank:       { en: 'World Rank',               tr: 'Dünya Sıralaması' },
  lbl_busiest:          { en: 'busiest port',             tr: 'en yoğun liman' },
  lbl_annual_teu:       { en: 'Annual TEU',               tr: 'Yıllık TEU' },
  lbl_throughput:       { en: '2023 throughput',          tr: '2023 hacmi' },
  lbl_connection:       { en: 'Connection',               tr: 'Bağlantı' },
}

// Singleton language state (reactive across all components)
const lang = ref<Lang>('en')

if (typeof window !== 'undefined') {
  const saved = localStorage.getItem('distrosim_lang') as Lang | null
  if (saved === 'tr' || saved === 'en') lang.value = saved
}

export function useI18n() {
  function t(key: string): string {
    const entry = TRANSLATIONS[key]
    if (!entry) return key
    return entry[lang.value] ?? entry['en'] ?? key
  }

  function setLang(l: Lang) {
    lang.value = l
    if (typeof window !== 'undefined') localStorage.setItem('distrosim_lang', l)
  }

  return { t, lang: readonly(lang), setLang }
}
