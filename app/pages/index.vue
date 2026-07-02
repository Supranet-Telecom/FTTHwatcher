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
            <span class="font-semibold text-sm">Acessos Por Empresa — Banda Larga Fixa</span>
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

      <!-- Card: Pressão Competitiva (placar da cidade) -->
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <span class="font-semibold text-sm">
              Pressão Competitiva
              <span class="text-muted font-normal">— {{ activeMunicipio || activeUf || 'Brasil' }}</span>
            </span>
            <UBadge v-if="pressao" color="neutral" variant="soft"> {{ pressao.mes }}</UBadge>
          </div>
        </template>

        <div v-if="pendingEmpresas" class="flex items-center justify-center h-40">
          <UIcon name="i-heroicons-arrow-path" class="animate-spin size-6 text-primary" />
        </div>
        <div v-else-if="!pressao" class="h-40 flex items-center justify-center text-muted text-sm">
          Sem dados para este filtro.
        </div>
        <div v-else class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="flex flex-col gap-1 p-4 rounded-lg bg-elevated/50">
            <span class="text-xs text-muted">Concorrentes ativos</span>
            <span class="text-2xl font-bold">{{ pressao.numConcorrentes }}</span>
          </div>
          <div class="flex flex-col gap-1 p-4 rounded-lg bg-elevated/50">
            <span class="text-xs text-muted">Posição da Supranet</span>
            <span class="text-2xl font-bold" :class="pressao.supraRank ? 'text-orange-500' : 'text-muted'">
              {{ pressao.supraRank ? `${pressao.supraRank}º` : '—' }}
            </span>
          </div>
          <div class="flex flex-col gap-1 p-4 rounded-lg bg-elevated/50">
            <span class="text-xs text-muted">Share da Supranet</span>
            <span class="text-2xl font-bold text-orange-500">
              {{ pressao.supraShare != null ? `${pressao.supraShare.toFixed(1)}%` : '—' }}
            </span>
          </div>
          <div class="flex flex-col gap-1 p-4 rounded-lg bg-elevated/50">
            <span class="text-xs text-muted">Cresc. médio concorrentes</span>
            <span class="text-2xl font-bold"
                  :class="pressao.crescMedioConc == null ? 'text-muted'
                          : pressao.crescMedioConc >= 0 ? 'text-green-500' : 'text-red-500'">
              {{ pressao.crescMedioConc != null
                 ? `${pressao.crescMedioConc >= 0 ? '+' : ''}${pressao.crescMedioConc.toFixed(1)}%`
                 : '—' }}
            </span>
          </div>
        </div>
        <p v-if="pressao && pressao.supraCresc != null" class="mt-4 text-sm text-muted">
          A Supranet cresceu
          <span :class="pressao.supraCresc >= 0 ? 'text-green-500 font-semibold' : 'text-red-500 font-semibold'">
            {{ pressao.supraCresc >= 0 ? '+' : '' }}{{ pressao.supraCresc.toFixed(1) }}%
          </span>
          no último mês vs.
          <span :class="(pressao.crescMedioConc ?? 0) >= 0 ? 'text-green-500' : 'text-red-500'">
            {{ (pressao.crescMedioConc ?? 0) >= 0 ? '+' : '' }}{{ (pressao.crescMedioConc ?? 0).toFixed(1) }}%
          </span>
          da média dos concorrentes.
        </p>
      </UCard>

      <!-- Card: Crescimento mensal por empresa -->
      <UCard>
        <template #header>
          <div class="flex items-center justify-between gap-3 flex-wrap">
            <span class="font-semibold text-sm">Crescimento Mensal por Empresa</span>
            <div class="flex items-center gap-3">
              <UButtonGroup size="xs">
                <UButton
                  :variant="crescMode === 'pct' ? 'solid' : 'outline'"
                  :color="crescMode === 'pct' ? 'primary' : 'neutral'"
                  @click="crescMode = 'pct'"
                >
                  %
                </UButton>
                <UButton
                  :variant="crescMode === 'abs' ? 'solid' : 'outline'"
                  :color="crescMode === 'abs' ? 'primary' : 'neutral'"
                  @click="crescMode = 'abs'"
                >
                  Nº de acessos
                </UButton>
              </UButtonGroup>
              <UBadge v-if="crescInfo" color="neutral" variant="soft">
                {{ crescInfo.de }} → {{ crescInfo.para }}
              </UBadge>
            </div>
          </div>
        </template>
        <ChartContainer :pending="pendingEmpresas" :error="errorEmpresas">
          <EChart :option="chartCrescimento" />
        </ChartContainer>
      </UCard>

      <!-- Card: Segmento PF vs PJ -->
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <span class="font-semibold text-sm">Perfil de Clientes — PF vs PJ</span>
            <UBadge v-if="segmentoInfo" color="neutral" variant="soft">{{ segmentoInfo }}</UBadge>
          </div>
        </template>
        <ChartContainer :pending="pendingSegmento" :error="errorSegmento">
          <EChart :option="chartSegmento" />
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
interface AcessoPorSegmento { ano: number; mes: number; empresa: string | null; tipo_pessoa: string | null; acessos: number }
interface PagedResponse<T> { count: number; next: string | null; previous: string | null; results: T[] }

const SUPRANET = 'Supranet'

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
// Helper compartilhado: transforma a lista plana de porEmpresa em estrutura útil
// ---------------------------------------------------------------------------
function agrupaEmpresas(list: AcessoPorEmpresa[]) {
  const periodosSet = new Set<string>()
  const grupos = new Map<string, Map<string, number>>()
  for (const row of list) {
    const nome = row.grupo_economico ?? '(sem nome)'
    const p = periodoLabel(row.ano, row.mes)
    periodosSet.add(p)
    if (!grupos.has(nome)) grupos.set(nome, new Map())
    grupos.get(nome)!.set(p, (grupos.get(nome)!.get(p) ?? 0) + row.acessos)
  }
  return { periodos: [...periodosSet].sort(), grupos }
}

// ---------------------------------------------------------------------------
// FEATURE 1 — Crescimento mensal (toggle entre % e nº absoluto de acessos)
// ---------------------------------------------------------------------------
// 'pct' = variação percentual | 'abs' = ganho/perda absoluto de acessos (net adds)
const crescMode = ref<'pct' | 'abs'>('pct')

const chartCrescimento = computed(() => {
  const list = porEmpresa.value ?? []
  if (list.length < 2) return buildBarChart([], [], {})

  const { periodos, grupos } = agrupaEmpresas(list)
  if (periodos.length < 2) return buildBarChart([], [], {})

  const last = periodos.at(-1)!
  const prev = periodos.at(-2)!

  // Empresas ordenadas por tamanho no último mês (para pegar as relevantes)
  const porTamanho = [...grupos.entries()]
    .map(([nome, m]) => ({ nome, atual: m.get(last) ?? 0, anterior: m.get(prev) ?? 0 }))
    .filter((e) => e.atual > 0 || e.anterior > 0)
    .sort((a, b) => b.atual - a.atual)

  const top = porTamanho.slice(0, 8)
  if (!top.some((e) => e.nome === SUPRANET)) {
    const s = porTamanho.find((e) => e.nome === SUPRANET)
    if (s) { top.pop(); top.push(s) }
  }

  const isPct = crescMode.value === 'pct'

  // pct: variação % (só quem tinha base); abs: ganho líquido de acessos
  const comCresc = top.map((e) => ({
    nome: e.nome,
    valor: isPct
      ? (e.anterior > 0 ? Math.round(((e.atual - e.anterior) / e.anterior) * 1000) / 10 : null)
      : e.atual - e.anterior,
  })).filter((e) => e.valor !== null) as { nome: string; valor: number }[]

  // Ordena crescente para o maior aparecer no topo do gráfico horizontal
  comCresc.sort((a, b) => a.valor - b.valor)

  return buildBarChart(
    comCresc.map((e) => e.nome),
    comCresc.map((e) => e.valor),
    {
      suffix: isPct ? '%' : '',
      integer: !isPct,
      // verde se cresceu, vermelho se caiu; Supranet sempre laranja
      colorFn: (nome, val) =>
        nome === SUPRANET ? '#f97316' : val >= 0 ? '#22c55e' : '#ef4444',
    },
  )
})

const crescInfo = computed(() => {
  const list = porEmpresa.value ?? []
  const { periodos } = agrupaEmpresas(list)
  if (periodos.length < 2) return null
  return { de: periodos.at(-2)!, para: periodos.at(-1)! }
})

// ---------------------------------------------------------------------------
// FEATURE 3 — Pressão competitiva (placar da cidade filtrada)
// ---------------------------------------------------------------------------
const pressao = computed(() => {
  const list = porEmpresa.value ?? []
  if (!list.length) return null

  const { periodos, grupos } = agrupaEmpresas(list)
  if (!periodos.length) return null
  const last = periodos.at(-1)!
  const prev = periodos.length >= 2 ? periodos.at(-2)! : null

  // Fatia do último mês por empresa
  const doMes = [...grupos.entries()]
    .map(([nome, m]) => ({ nome, atual: m.get(last) ?? 0, anterior: prev ? (m.get(prev) ?? 0) : 0 }))
    .filter((e) => e.atual > 0)

  const totalMercado = doMes.reduce((s, e) => s + e.atual, 0)
  const ranking = [...doMes].sort((a, b) => b.atual - a.atual)

  const supra = doMes.find((e) => e.nome === SUPRANET)
  const supraRank = supra ? ranking.findIndex((e) => e.nome === SUPRANET) + 1 : null
  const supraShare = supra && totalMercado > 0 ? (supra.atual / totalMercado) * 100 : null

  // Crescimento médio dos concorrentes (exclui Supranet, só quem tinha base)
  const concorrentes = doMes.filter((e) => e.nome !== SUPRANET)
  const comBase = concorrentes.filter((e) => e.anterior > 0)
  const crescMedioConc = comBase.length
    ? comBase.reduce((s, e) => s + ((e.atual - e.anterior) / e.anterior) * 100, 0) / comBase.length
    : null
  const supraCresc = supra && supra.anterior > 0
    ? ((supra.atual - supra.anterior) / supra.anterior) * 100
    : null

  return {
    mes: last,
    numConcorrentes: concorrentes.length,
    totalMercado,
    supraShare,
    supraRank,
    supraAcessos: supra?.atual ?? 0,
    crescMedioConc,
    supraCresc,
  }
})

// ---------------------------------------------------------------------------
// FEATURE 5 — Segmento PF vs PJ por concorrente (último mês)
// ---------------------------------------------------------------------------
const { data: porSegmento, pending: pendingSegmento, error: errorSegmento } =
  useAsyncData(
    () => `porSegmento-${activeUf.value}-${activeMunicipio.value}-${activeAnoGte.value}`,
    () => fetchAllPages<AcessoPorSegmento>(`/api/acessos/por-segmento/?${buildQuery()}`),
    { lazy: true, server: false },
  )

const chartSegmento = computed(() => {
  const list = porSegmento.value ?? []
  if (!list.length) return buildStackedBar([], [], [])

  // Último período disponível
  let maxPeriodo = ''
  for (const row of list) {
    const p = periodoLabel(row.ano, row.mes)
    if (p > maxPeriodo) maxPeriodo = p
  }

  // empresa -> { pf, pj }
  const porEmpresaSeg = new Map<string, { pf: number; pj: number }>()
  for (const row of list) {
    if (periodoLabel(row.ano, row.mes) !== maxPeriodo) continue
    const nome = row.empresa ?? '(sem nome)'
    if (!porEmpresaSeg.has(nome)) porEmpresaSeg.set(nome, { pf: 0, pj: 0 })
    const bucket = porEmpresaSeg.get(nome)!
    if ((row.tipo_pessoa ?? '').toLowerCase().includes('jurídica')) bucket.pj += row.acessos
    else bucket.pf += row.acessos
  }

  const ranked = [...porEmpresaSeg.entries()]
    .map(([nome, v]) => ({ nome, ...v, total: v.pf + v.pj }))
    .sort((a, b) => b.total - a.total)

  const top = ranked.slice(0, 8)
  if (!top.some((e) => e.nome === SUPRANET)) {
    const s = ranked.find((e) => e.nome === SUPRANET)
    if (s) { top.pop(); top.push(s) }
  }

  // Ordena crescente para o maior no topo (barra horizontal)
  top.reverse()

  return buildStackedBar(
    top.map((e) => e.nome),
    top.map((e) => e.pf),
    top.map((e) => e.pj),
  )
})

const segmentoInfo = computed(() => {
  const list = porSegmento.value ?? []
  let maxPeriodo = ''
  for (const row of list) {
    const p = periodoLabel(row.ano, row.mes)
    if (p > maxPeriodo) maxPeriodo = p
  }
  return maxPeriodo || null
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

// ---------------------------------------------------------------------------
// Barra horizontal simples com cor por valor (usado no crescimento mensal)
// ---------------------------------------------------------------------------
function buildBarChart(
  categories: string[],
  values: number[],
  opts: { suffix?: string; integer?: boolean; colorFn?: (nome: string, val: number) => string },
) {
  const suffix = opts.suffix ?? ''
  const fmt = (v: number) => {
    const sign = v > 0 ? '+' : ''
    const num = opts.integer ? Math.round(v).toLocaleString('pt-BR') : v
    return `${sign}${num}${suffix}`
  }
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(15,23,42,0.92)',
      borderColor: '#334155',
      textStyle: { color: '#e2e8f0' },
      formatter: (p: any[]) => `${p[0].name}: <b>${fmt(p[0].value)}</b>`,
    },
    grid: { left: 120, right: 70, top: 16, bottom: 24 },
    xAxis: {
      type: 'value',
      axisLabel: {
        color: '#64748b',
        formatter: (v: number) => opts.integer ? formatMillions(v) : `${v}${suffix}`,
      },
      splitLine: { lineStyle: { color: '#1e293b' } },
    },
    yAxis: {
      type: 'category',
      data: categories,
      axisLabel: { color: '#cbd5e1', fontSize: 12 },
      axisLine: { lineStyle: { color: '#334155' } },
    },
    series: [{
      type: 'bar',
      data: values.map((v, i) => ({
        value: v,
        itemStyle: { color: opts.colorFn ? opts.colorFn(categories[i], v) : '#3b82f6', borderRadius: 3 },
      })),
      barMaxWidth: 22,
      label: {
        show: true,
        position: 'right',
        color: '#cbd5e1',
        fontSize: 11,
        formatter: (p: any) => fmt(p.value),
      },
    }],
  }
}

// ---------------------------------------------------------------------------
// Barra horizontal empilhada PF vs PJ (usado no segmento)
// ---------------------------------------------------------------------------
function buildStackedBar(categories: string[], pf: number[], pj: number[]) {
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(15,23,42,0.92)',
      borderColor: '#334155',
      textStyle: { color: '#e2e8f0' },
    },
    legend: {
      data: ['Pessoa Física', 'Pessoa Jurídica'],
      top: 4,
      textStyle: { color: '#94a3b8' },
    },
    grid: { left: 120, right: 50, top: 40, bottom: 24 },
    xAxis: {
      type: 'value',
      axisLabel: { color: '#64748b', formatter: (v: number) => formatMillions(v) },
      splitLine: { lineStyle: { color: '#1e293b' } },
    },
    yAxis: {
      type: 'category',
      data: categories,
      axisLabel: {
        color: (val: string) => (val === 'Supranet' ? '#f97316' : '#cbd5e1'),
        fontSize: 12,
      },
      axisLine: { lineStyle: { color: '#334155' } },
    },
    series: [
      {
        name: 'Pessoa Física',
        type: 'bar',
        stack: 'total',
        data: pf,
        itemStyle: { color: '#3b82f6' },
        barMaxWidth: 22,
      },
      {
        name: 'Pessoa Jurídica',
        type: 'bar',
        stack: 'total',
        data: pj,
        itemStyle: { color: '#f59e0b' },
        barMaxWidth: 22,
      },
    ],
  }
}
</script>
