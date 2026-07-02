<template>
  <UDashboardPanel grow>
    <template #header>
      <UDashboardNavbar title="Dashboard" />
    </template>

    <template #body>
    <div class="flex flex-col gap-6">

      <!-- Barra de filtros -->
      <UCard :ui="{ root: 'rounded-lg overflow-visible' }"  >
        <div class="flex flex-wrap gap-x-4 gap-y-3 items-end">
          <div class="flex flex-col gap-1">
            <span class="text-sm font-medium text-muted">Estado (UF)</span>
            <USelect
              v-model="pendingUfModel"
              :items="UFS"
              placeholder="Todos"
              class="w-28"
            />
          </div>

          <div class="flex flex-col gap-1">
            <span class="text-sm font-medium text-muted">Município</span>
            <UInput
              v-model="pendingMunicipio"
              placeholder="Ex: Uberlândia"
              class="w-56"
              @keydown.enter="applyFilters"
            />
          </div>

          <div class="flex flex-col gap-1">
            <span class="text-sm font-medium text-muted">A partir de</span>
            <USelect
              v-model="pendingAnoGte"
              :items="ANOS"
              class="w-28"
            />
          </div>

          <div class="flex gap-2">
            <UButton @click="applyFilters">Aplicar</UButton>
            <UButton color="neutral" variant="ghost" @click="resetFilters">Limpar</UButton>
          </div>
        </div>
      </UCard>

      <!-- Card 1: Total Nacional -->
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <span class="font-semibold text-sm">
              Acessos de Banda Larga Fixa — Total
              <span v-if="activeUf" class="text-primary">({{ activeUf }}{{ activeMunicipio ? ` · ${activeMunicipio}` : '' }})</span>
            </span>
            <UBadge v-if="latestTotal" color="primary" variant="soft">
              {{ formatMillions(latestTotal.acessos) }} em {{ latestTotal.ano }}/{{ pad(latestTotal.mes) }}
            </UBadge>
          </div>
        </template>
        <ChartContainer :pending="pendingTotais" :error="errorTotais">
          <EChart :option="chartTotalNacional" />
        </ChartContainer>
      </UCard>

      <!-- Card 2: Acessos absolutos por grupo econômico -->
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <span class="font-semibold text-sm">Acessos — Banda Larga Fixa</span>
            <UBadge color="neutral" variant="soft">top {{ totalGrupos }} grupos</UBadge>
          </div>
        </template>
        <ChartContainer :pending="pendingEmpresas" :error="errorEmpresas">
          <EChart :option="chartPorEmpresa" />
        </ChartContainer>
      </UCard>

      <!-- Card 3: Participação de mercado (%) -->
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <span class="font-semibold text-sm">Participação de Mercado — Banda Larga Fixa (%)</span>
            <UBadge color="neutral" variant="soft">top {{ totalGrupos }} grupos</UBadge>
          </div>
        </template>
        <ChartContainer :pending="pendingEmpresas" :error="errorEmpresas">
          <EChart :option="chartParticipacao" />
        </ChartContainer>
      </UCard>

      <!-- Card 4: Acessos por tecnologia -->
      <UCard>
        <template #header>
          <span class="font-semibold text-sm">Acessos por Tecnologia</span>
        </template>
        <ChartContainer :pending="pendingTecnologia" :error="errorTecnologia">
          <EChart :option="chartPorTecnologia" />
        </ChartContainer>
      </UCard>

    </div>
    </template>
  </UDashboardPanel>
</template>

<script setup lang="ts">
// ---------------------------------------------------------------------------
// Constantes
// ---------------------------------------------------------------------------
const UFS = [
  'AC','AL','AP','AM','BA','CE','DF','ES','GO','MA',
  'MT','MS','MG','PA','PB','PR','PE','PI','RJ','RN',
  'RS','RO','RR','SC','SP','SE','TO',
]

const ANOS = ['2007','2010','2013','2015','2016','2017','2018','2019','2020','2021','2022','2023','2024','2025','2026']

// ---------------------------------------------------------------------------
// Tipos
// ---------------------------------------------------------------------------
interface Total { ano: number; mes: number; acessos: number }
interface AcessoPorEmpresa { ano: number; mes: number; grupo_economico: string | null; acessos: number }
interface AcessoPorTecnologia { ano: number; mes: number; tecnologia: string | null; acessos: number }
interface PagedResponse<T> { count: number; next: string | null; previous: string | null; results: T[] }

// ---------------------------------------------------------------------------
// Filtros — sincronizados com URL
// ---------------------------------------------------------------------------
const route  = useRoute()
const router = useRouter()

// "pending" = o que o usuário está editando no formulário
const pendingUf        = ref((route.query.uf        as string) || 'MG')
const pendingMunicipio = ref((route.query.municipio as string) || '')
const pendingAnoGte    = ref((route.query.ano__gte  as string) || '2018')

// "active" = o que está efetivamente aplicado nos gráficos
const activeUf        = ref(pendingUf.value)
const activeMunicipio = ref(pendingMunicipio.value)
const activeAnoGte    = ref(pendingAnoGte.value)

function applyFilters() {
  activeUf.value        = pendingUf.value
  activeMunicipio.value = pendingMunicipio.value
  activeAnoGte.value    = pendingAnoGte.value

  // Salva na URL para persistir entre recarregamentos
  router.replace({
    query: {
      ...(activeUf.value        ? { uf:        activeUf.value }        : {}),
      ...(activeMunicipio.value ? { municipio: activeMunicipio.value } : {}),
      ...(activeAnoGte.value    ? { ano__gte:  activeAnoGte.value }    : {}),
    },
  })
}

function resetFilters() {
  pendingUf.value        = 'MG'
  pendingMunicipio.value = ''
  pendingAnoGte.value    = '2018'
  applyFilters()
}

// Permite limpar a UF clicando no item selecionado (valor vira undefined → sem filtro)
const pendingUfModel = computed({
  get: () => pendingUf.value || undefined,
  set: (v) => { pendingUf.value = v ?? '' },
})

// ---------------------------------------------------------------------------
// Utilitários
// ---------------------------------------------------------------------------
function pad(n: number) { return String(n).padStart(2, '0') }

function formatMillions(n: number) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000)     return `${(n / 1_000).toFixed(1)}k`
  return String(n)
}

function periodoLabel(ano: number, mes: number) {
  return `${ano}-${pad(mes)}`
}

async function fetchAllPages<T>(url: string): Promise<T[]> {
  const all: T[] = []
  let next: string | null = url
  while (next) {
    const page = await $fetch<PagedResponse<T>>(next)
    all.push(...page.results)
    next = page.next ? page.next.replace(/^https?:\/\/[^/]+/, '') : null
  }
  return all
}

/** Monta a query string de filtros a partir dos valores ativos. */
function buildQuery(extra: Record<string, string> = {}) {
  const p = new URLSearchParams({ page_size: '5000', tipo_produto: 'INTERNET' })
  if (activeUf.value)        p.set('uf',        activeUf.value)
  if (activeMunicipio.value) p.set('municipio', activeMunicipio.value)
  if (activeAnoGte.value)    p.set('ano__gte',  activeAnoGte.value)
  for (const [k, v] of Object.entries(extra)) p.set(k, v)
  return p.toString()
}

// ---------------------------------------------------------------------------
// 1. Total — reutiliza o endpoint /totais/ mas filtrando via /acessos/por-uf/
//    quando há filtro de UF (totais/ não aceita filtros)
// ---------------------------------------------------------------------------
const { data: totais, pending: pendingTotais, error: errorTotais } =
  useAsyncData(
    () => `totais-${activeUf.value}-${activeMunicipio.value}-${activeAnoGte.value}`,
    () => {
      if (!activeUf.value && !activeMunicipio.value) {
        return fetchAllPages<Total>(`/api/totais/?ordering=ano,mes&page_size=5000`)
      }
      return fetchAllPages<Total>(`/api/acessos/por-uf/?ordering=ano,mes&${buildQuery()}`)
    },
    { lazy: true, server: false },
  )

const latestTotal = computed(() => {
  const list = totais.value
  return list?.length ? list[list.length - 1] : null
})

const chartTotalNacional = computed(() => {
  const list = [...(totais.value ?? [])].sort((a, b) => a.ano - b.ano || a.mes - b.mes)
  return buildLineChart(
    list.map((t) => periodoLabel(t.ano, t.mes)),
    [{ name: 'Total', data: list.map((t) => t.acessos) }],
    { initialMonths: 36 },
  )
})

// ---------------------------------------------------------------------------
// 2. Por Grupo Econômico
// ---------------------------------------------------------------------------
const { data: porEmpresa, pending: pendingEmpresas, error: errorEmpresas } =
  useAsyncData(
    () => `porEmpresa-${activeUf.value}-${activeMunicipio.value}-${activeAnoGte.value}`,
    () => fetchAllPages<AcessoPorEmpresa>(`/api/acessos/por-empresa/?${buildQuery()}`),
    { lazy: true, server: false },
  )

const chartPorEmpresa = computed(() => {
  const list = porEmpresa.value ?? []

  const periodosSet = new Set<string>()
  for (const row of list) periodosSet.add(periodoLabel(row.ano, row.mes))
  const periodos = [...periodosSet].sort()

  const grupos    = new Map<string, Map<string, number>>()
  const totaisPorGrupo = new Map<string, number>()
  for (const row of list) {
    const nome = row.grupo_economico ?? '(sem grupo)'
    if (!grupos.has(nome)) grupos.set(nome, new Map())
    const p = periodoLabel(row.ano, row.mes)
    grupos.get(nome)!.set(p, (grupos.get(nome)!.get(p) ?? 0) + row.acessos)
    totaisPorGrupo.set(nome, (totaisPorGrupo.get(nome) ?? 0) + row.acessos)
  }

  const ranked = [...totaisPorGrupo.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([nome]) => nome)

  // Sempre inclui a Supranet; completa com as maiores até 7 empresas
  const top7 = ranked.slice(0, 7)
  if (!top7.includes('Supranet') && grupos.has('Supranet')) {
    top7.pop()
    top7.push('Supranet')
  }

  return buildLineChart(
    periodos,
    top7.map((nome) => ({ name: nome, data: periodos.map((p) => grupos.get(nome)!.get(p) ?? null) })),
  )
})

const totalGrupos = computed(() =>
  Math.min(
    new Set((porEmpresa.value ?? []).map((r) => r.grupo_economico ?? '(sem grupo)')).size,
    10,
  ),
)

/**
 * Participação de mercado em % — calculado a partir dos mesmos dados de porEmpresa.
 * Para cada período: % de cada grupo = acessos_do_grupo / total_do_período * 100
 * Reutiliza os top 10 grupos já identificados no chartPorEmpresa.
 */
const chartParticipacao = computed(() => {
  const list = porEmpresa.value ?? []
  if (!list.length) return buildLineChart([], [])

  const periodosSet = new Set<string>()
  for (const row of list) periodosSet.add(periodoLabel(row.ano, row.mes))
  const periodos = [...periodosSet].sort()

  // Agrupa por empresa e calcula total por período
  const grupos = new Map<string, Map<string, number>>()
  const totalPorPeriodo = new Map<string, number>()
  const totaisPorGrupo = new Map<string, number>()

  for (const row of list) {
    const nome = row.grupo_economico ?? '(sem grupo)'
    const p = periodoLabel(row.ano, row.mes)
    if (!grupos.has(nome)) grupos.set(nome, new Map())
    grupos.get(nome)!.set(p, (grupos.get(nome)!.get(p) ?? 0) + row.acessos)
    totalPorPeriodo.set(p, (totalPorPeriodo.get(p) ?? 0) + row.acessos)
    totaisPorGrupo.set(nome, (totaisPorGrupo.get(nome) ?? 0) + row.acessos)
  }

  const ranked = [...totaisPorGrupo.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([nome]) => nome)

  const top7 = ranked.slice(0, 7)
  if (!top7.includes('Supranet') && grupos.has('Supranet')) {
    top7.pop()
    top7.push('Supranet')
  }

  const series = top7.map((nome) => ({
    name: nome,
    data: periodos.map((p) => {
      const total = totalPorPeriodo.get(p) ?? 0
      const val = grupos.get(nome)!.get(p) ?? 0
      return total > 0 ? Math.round((val / total) * 1000) / 10 : null // 1 casa decimal
    }),
  }))

  return buildLineChart(periodos, series, { yAxisSuffix: '%' })
})

// ---------------------------------------------------------------------------
// 3. Por Tecnologia
// ---------------------------------------------------------------------------
const { data: porTecnologia, pending: pendingTecnologia, error: errorTecnologia } =
  useAsyncData(
    () => `porTecnologia-${activeUf.value}-${activeMunicipio.value}-${activeAnoGte.value}`,
    () => fetchAllPages<AcessoPorTecnologia>(`/api/acessos/por-tecnologia/?${buildQuery()}`),
    { lazy: true, server: false },
  )

const chartPorTecnologia = computed(() => {
  const list = porTecnologia.value ?? []

  const periodosSet = new Set<string>()
  for (const row of list) periodosSet.add(periodoLabel(row.ano, row.mes))
  const periodos = [...periodosSet].sort()

  const tecMap = new Map<string, Map<string, number>>()
  const totaisPorTec = new Map<string, number>()
  for (const row of list) {
    const nome = row.tecnologia ?? '(desconhecida)'
    if (!tecMap.has(nome)) tecMap.set(nome, new Map())
    const p = periodoLabel(row.ano, row.mes)
    tecMap.get(nome)!.set(p, (tecMap.get(nome)!.get(p) ?? 0) + row.acessos)
    totaisPorTec.set(nome, (totaisPorTec.get(nome) ?? 0) + row.acessos)
  }

  const top10 = [...totaisPorTec.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 7)
    .map(([nome]) => nome)

  return buildLineChart(
    periodos,
    top10.map((nome) => ({
      name: nome,
      data: periodos.map((p) => tecMap.get(nome)!.get(p) ?? null),
    })),
  )
})

// ---------------------------------------------------------------------------
// Cores fixas por empresa — Supranet sempre laranja
// ---------------------------------------------------------------------------
const COMPANY_COLORS: Record<string, string> = {
  'Supranet':          '#f97316', // laranja
  'VERO':              '#3b82f6', // azul
  'CLARO':             '#ef4444', // vermelho
  'VIVO':              '#a855f7', // roxo
  'OI':                '#facc15', // amarelo
  'TIM':               '#06b6d4', // ciano
  'Ibi Telecom':       '#10b981', // verde
  'Brnet':             '#64748b', // cinza-azulado
  'Valenet':           '#f43f5e', // rosa
  'STARLINK BRAZIL SERVICOS DE INTERNET LTDA.': '#e2e8f0', // branco suave
}

const FALLBACK_COLORS = [
  '#8b5cf6','#14b8a6','#f59e0b','#84cc16','#ec4899',
  '#0ea5e9','#d946ef','#fb923c','#a3e635','#2dd4bf',
]

function getColor(name: string, index: number): string {
  return COMPANY_COLORS[name] ?? FALLBACK_COLORS[index % FALLBACK_COLORS.length]
}

// ---------------------------------------------------------------------------
// Fábrica de opções ECharts
// ---------------------------------------------------------------------------
function buildLineChart(
  xData: string[],
  series: { name: string; data: (number | null)[] }[],
  opts: { initialMonths?: number; yAxisSuffix?: string } = {},
) {
  const totalPoints = xData.length
  const show = opts.initialMonths ?? 24
  const zoomStart = totalPoints > show
    ? Math.round(((totalPoints - show) / totalPoints) * 100)
    : 0
  const suffix = opts.yAxisSuffix ?? ''

  return {
    tooltip: {
      trigger: 'axis',
      confine: true,
      backgroundColor: 'rgba(15,23,42,0.92)',
      borderColor: '#334155',
      textStyle: { color: '#e2e8f0', fontSize: 12 },
      formatter: (params: any[]) => {
        const header = `<div style="font-weight:600;margin-bottom:4px">${params[0].axisValue}</div>`
        const rows = params
          .filter((p) => p.value != null)
          .sort((a, b) => b.value - a.value)
          .map((p) => {
            const isSupra = p.seriesName === 'Supranet'
            const style = isSupra ? 'font-weight:700;color:#f97316' : ''
            return `<div style="${style}">${p.marker} ${p.seriesName}: <b>${p.value.toLocaleString('pt-BR')}${suffix}</b></div>`
          })
          .join('')
        return header + rows
      },
    },
    legend: {
      type: 'scroll',
      top: 4,
      left: 'center',
      itemWidth: 16,
      itemHeight: 3,
      textStyle: { fontSize: 11, color: '#94a3b8' },
    },
    grid: { left: 70, right: 24, top: 44, bottom: 60 },
    xAxis: {
      type: 'category',
      data: xData,
      axisLine: { lineStyle: { color: '#334155' } },
      axisTick: { lineStyle: { color: '#334155' } },
      axisLabel: {
        rotate: 30,
        interval: (idx: number) => idx % 6 === 0,
        fontSize: 11,
        color: '#64748b',
      },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#1e293b' } },
      axisLabel: {
        color: '#64748b',
        formatter: suffix
          ? (v: number) => `${v}${suffix}`
          : (v: number) => formatMillions(v),
      },
    },
    dataZoom: [
      { type: 'inside', start: zoomStart, end: 100 },
      { type: 'slider', start: zoomStart, end: 100, height: 18, bottom: 8,
        borderColor: '#334155', fillerColor: 'rgba(99,102,241,0.15)',
        handleStyle: { color: '#6366f1' } },
    ],
    series: series.map((s, i) => {
      const isSupra = s.name === 'Supranet'
      const color = getColor(s.name, i)

      // Rótulo no último ponto da linha
      const lastIndex = [...s.data].reverse().findIndex(v => v != null)
      const labelIndex = lastIndex === -1 ? -1 : s.data.length - 1 - lastIndex

      return {
        name: s.name,
        type: 'line',
        data: s.data.map((v, idx) => ({
          value: v,
          label: idx === labelIndex
            ? { show: true, formatter: s.name, position: 'right', fontSize: 11,
                color, fontWeight: isSupra ? 700 : 400,
                backgroundColor: 'rgba(15,23,42,0.7)', padding: [2, 4],
                borderRadius: 3 }
            : { show: false },
        })),
        smooth: true,
        showSymbol: isSupra,
        symbolSize: 5,
        lineStyle: { width: isSupra ? 3 : 1.5, color },
        itemStyle: { color },
        emphasis: { lineStyle: { width: isSupra ? 4 : 2.5 } },
        connectNulls: false,
        z: isSupra ? 10 : 1,
      }
    }),
  }
}
</script>
