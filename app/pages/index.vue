<template>
  <UDashboardPanel grow>
    <template #header>
      <UDashboardNavbar title="Dashboard" />
    </template>

    <div class="p-6 flex flex-col gap-6 overflow-y-auto">
      <!-- Card 1: Total Nacional -->
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <span class="font-semibold text-sm">Acessos de Banda Larga Fixa — Total Nacional</span>
            <UBadge v-if="latestTotal" color="primary" variant="soft">
              {{ formatMillions(latestTotal.acessos) }} em {{ latestTotal.ano }}/{{ pad(latestTotal.mes) }}
            </UBadge>
          </div>
        </template>
        <ChartContainer :pending="pendingTotais" :error="errorTotais">
          <EChart :option="chartTotalNacional" />
        </ChartContainer>
      </UCard>

      <!-- Card 2: Market share por grupo econômico -->
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <span class="font-semibold text-sm">Acessos por Grupo Econômico (desde 2018)</span>
            <UBadge color="neutral" variant="soft">{{ totalGrupos }} grupos</UBadge>
          </div>
        </template>
        <ChartContainer :pending="pendingEmpresas" :error="errorEmpresas">
          <EChart :option="chartPorEmpresa" />
        </ChartContainer>
      </UCard>

      <!-- Card 3: Crescimento por tecnologia -->
      <UCard>
        <template #header>
          <span class="font-semibold text-sm">Acessos por Tecnologia (desde 2018)</span>
        </template>
        <ChartContainer :pending="pendingTecnologia" :error="errorTecnologia">
          <EChart :option="chartPorTecnologia" />
        </ChartContainer>
      </UCard>
    </div>
  </UDashboardPanel>
</template>

<script setup lang="ts">
// ---------------------------------------------------------------------------
// Tipos
// ---------------------------------------------------------------------------
interface Total {
  ano: number
  mes: number
  acessos: number
}

interface AcessoPorEmpresa {
  ano: number
  mes: number
  grupo_economico: string | null
  acessos: number
}

interface AcessoPorTecnologia {
  ano: number
  mes: number
  tecnologia: string | null
  acessos: number
}

interface PagedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// ---------------------------------------------------------------------------
// Utilitários
// ---------------------------------------------------------------------------
function pad(n: number) {
  return String(n).padStart(2, '0')
}

function formatMillions(n: number) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}k`
  return String(n)
}

/** Rótulo legível para o eixo X: "2024-03" */
function periodoLabel(ano: number, mes: number) {
  return `${ano}-${pad(mes)}`
}

/**
 * Busca todas as páginas de um endpoint paginado e retorna um array com
 * todos os resultados. O Nuxt/Django pagina em blocos de 100 por padrão,
 * então precisamos seguir o campo "next" até acabar.
 */
async function fetchAllPages<T>(url: string): Promise<T[]> {
  const all: T[] = []
  let next: string | null = url

  while (next) {
    const page = await $fetch<PagedResponse<T>>(next)
    all.push(...page.results)
    // Remove o host para funcionar pelo proxy do Nuxt (/api/**)
    next = page.next ? page.next.replace(/^https?:\/\/[^/]+/, '') : null
  }

  return all
}

// ---------------------------------------------------------------------------
// 1. Total Nacional
// ---------------------------------------------------------------------------
const { data: totais, pending: pendingTotais, error: errorTotais } =
  await useAsyncData('totais', () =>
    fetchAllPages<Total>('/api/totais/?ordering=ano,mes&page_size=500'),
  )

const latestTotal = computed(() => {
  const list = totais.value
  return list?.length ? list[list.length - 1] : null
})

const chartTotalNacional = computed(() => {
  const list = totais.value ?? []

  // Agrega por mês para manter granularidade mas com zoom inicial em 3 anos
  const sorted = [...list].sort((a, b) => a.ano - b.ano || a.mes - b.mes)
  const xData = sorted.map((t) => periodoLabel(t.ano, t.mes))
  const yData = sorted.map((t) => t.acessos)

  return buildLineChart(xData, [{ name: 'Total', data: yData }], { initialMonths: 36 })
})

// ---------------------------------------------------------------------------
// 2. Por Grupo Econômico
// ---------------------------------------------------------------------------
const { data: porEmpresa, pending: pendingEmpresas, error: errorEmpresas } =
  await useAsyncData('porEmpresa', () =>
    fetchAllPages<AcessoPorEmpresa>(
      '/api/acessos/por-empresa/?ano__gte=2018&page_size=500',
    ),
  )

/**
 * Transforma a lista plana em um mapa:
 *   grupo_economico → Map<"ano-mes", acessos>
 * Limita aos top 10 grupos por total de acessos para não poluir a legenda.
 */
const chartPorEmpresa = computed(() => {
  const list = porEmpresa.value ?? []

  const periodosSet = new Set<string>()
  for (const row of list) periodosSet.add(periodoLabel(row.ano, row.mes))
  const periodos = [...periodosSet].sort()

  // Agrupa por empresa e soma o total de acessos de cada uma
  const grupos = new Map<string, Map<string, number>>()
  const totaisPorGrupo = new Map<string, number>()
  for (const row of list) {
    const nome = row.grupo_economico ?? '(sem grupo)'
    if (!grupos.has(nome)) grupos.set(nome, new Map())
    const p = periodoLabel(row.ano, row.mes)
    grupos.get(nome)!.set(p, (grupos.get(nome)!.get(p) ?? 0) + row.acessos)
    totaisPorGrupo.set(nome, (totaisPorGrupo.get(nome) ?? 0) + row.acessos)
  }

  // Pega apenas os 10 maiores para a legenda não sufocar o gráfico
  const top10 = [...totaisPorGrupo.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([nome]) => nome)

  const series = top10.map((nome) => ({
    name: nome,
    data: periodos.map((p) => grupos.get(nome)!.get(p) ?? null),
  }))

  return buildLineChart(periodos, series)
})

const totalGrupos = computed(() => {
  const list = porEmpresa.value ?? []
  return new Set(list.map((r) => r.grupo_economico ?? '(sem grupo)')).size
})

// ---------------------------------------------------------------------------
// 3. Por Tecnologia
// ---------------------------------------------------------------------------
const { data: porTecnologia, pending: pendingTecnologia, error: errorTecnologia } =
  await useAsyncData('porTecnologia', () =>
    fetchAllPages<AcessoPorTecnologia>(
      '/api/acessos/por-tecnologia/?ano__gte=2018&page_size=500',
    ),
  )

const chartPorTecnologia = computed(() => {
  const list = porTecnologia.value ?? []

  const periodosSet = new Set<string>()
  for (const row of list) periodosSet.add(periodoLabel(row.ano, row.mes))
  const periodos = [...periodosSet].sort()

  const tecnologias = new Map<string, Map<string, number>>()
  for (const row of list) {
    const nome = row.tecnologia ?? '(desconhecida)'
    if (!tecnologias.has(nome)) tecnologias.set(nome, new Map())
    const p = periodoLabel(row.ano, row.mes)
    tecnologias.get(nome)!.set(p, (tecnologias.get(nome)!.get(p) ?? 0) + row.acessos)
  }

  const series = [...tecnologias.entries()].map(([nome, dados]) => ({
    name: nome,
    data: periodos.map((p) => dados.get(p) ?? null),
  }))

  return buildLineChart(periodos, series)
})

// ---------------------------------------------------------------------------
// Fábrica de opções ECharts (line chart reutilizável)
// ---------------------------------------------------------------------------
function buildLineChart(
  xData: string[],
  series: { name: string; data: (number | null)[] }[],
  opts: { initialMonths?: number } = {},
) {
  // Por padrão mostra os últimos 24 meses no zoom inicial
  const totalPoints = xData.length
  const show = opts.initialMonths ?? 24
  const zoomStart = totalPoints > show
    ? Math.round(((totalPoints - show) / totalPoints) * 100)
    : 0

  return {
    tooltip: {
      trigger: 'axis',
      confine: true,
      formatter: (params: any[]) => {
        const header = `<b>${params[0].axisValue}</b><br/>`
        const rows = params
          .filter((p) => p.value != null)
          .sort((a, b) => b.value - a.value)
          .map((p) => `${p.marker}${p.seriesName}: <b>${p.value.toLocaleString('pt-BR')}</b>`)
          .join('<br/>')
        return header + rows
      },
    },
    legend: {
      type: 'scroll',
      top: 4,
      left: 'center',
      itemWidth: 14,
      itemHeight: 10,
      textStyle: { fontSize: 11 },
    },
    grid: { left: 70, right: 24, top: 48, bottom: 60 },
    xAxis: {
      type: 'category',
      data: xData,
      axisLabel: {
        rotate: 30,
        // mostra 1 label a cada 6 meses para não empilhar
        interval: (idx: number) => idx % 6 === 0,
        fontSize: 11,
      },
    },
    yAxis: {
      type: 'value',
      axisLabel: { formatter: (v: number) => formatMillions(v) },
    },
    dataZoom: [
      { type: 'inside', start: zoomStart, end: 100 },
      { type: 'slider', start: zoomStart, end: 100, height: 18, bottom: 8 },
    ],
    series: series.map((s) => ({
      name: s.name,
      type: 'line',
      data: s.data,
      smooth: true,
      showSymbol: false,
      lineStyle: { width: 2 },
      connectNulls: false,
    })),
  }
}
</script>
