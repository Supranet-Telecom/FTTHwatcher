<template>
  <UDashboardPanel grow>
    <template #header>
      <UDashboardNavbar title="Usuários" />
    </template>

    <template #body>
      <div class="flex flex-col gap-6">
        <!-- Novo usuário -->
        <UCard>
          <template #header>
            <span class="font-semibold text-sm">Novo usuário</span>
          </template>

          <form class="grid grid-cols-1 md:grid-cols-2 gap-4" @submit.prevent="criar">
            <UFormField label="Usuário *">
              <UInput v-model="novo.username" class="w-full" />
            </UFormField>
            <UFormField label="E-mail">
              <UInput v-model="novo.email" type="email" class="w-full" />
            </UFormField>
            <UFormField label="Nome">
              <UInput v-model="novo.first_name" class="w-full" />
            </UFormField>
            <UFormField label="Sobrenome">
              <UInput v-model="novo.last_name" class="w-full" />
            </UFormField>
            <UFormField label="Senha *">
              <UInput v-model="novo.password" type="password" class="w-full" />
            </UFormField>
            <div class="flex items-center gap-2 pt-6">
              <USwitch v-model="novo.is_admin" />
              <span class="text-sm">Administrador</span>
            </div>

            <div class="md:col-span-2 flex items-center gap-3">
              <UButton type="submit" :loading="criando">Criar usuário</UButton>
              <UAlert v-if="msg" :color="msgColor" variant="soft" :title="msg" class="flex-1" />
            </div>
          </form>
        </UCard>

        <!-- Lista de usuários -->
        <UCard>
          <template #header>
            <div class="flex items-center justify-between">
              <span class="font-semibold text-sm">Usuários cadastrados</span>
              <UBadge color="neutral" variant="soft">{{ users.length }}</UBadge>
            </div>
          </template>

          <div v-if="pending" class="flex justify-center py-8">
            <UIcon name="i-heroicons-arrow-path" class="animate-spin size-6 text-primary" />
          </div>

          <div v-else class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="text-muted border-b border-default">
                <tr>
                  <th class="text-left font-medium py-2 px-3">Usuário</th>
                  <th class="text-left font-medium py-2 px-3">E-mail</th>
                  <th class="text-left font-medium py-2 px-3">Papel</th>
                  <th class="text-left font-medium py-2 px-3">Status</th>
                  <th class="text-right font-medium py-2 px-3">Ações</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="u in users" :key="u.id" class="border-b border-default/50">
                  <td class="py-2 px-3">
                    <div class="font-medium">{{ u.username }}</div>
                    <div class="text-xs text-muted">{{ [u.first_name, u.last_name].filter(Boolean).join(' ') || '—' }}</div>
                  </td>
                  <td class="py-2 px-3 text-muted">{{ u.email || '—' }}</td>
                  <td class="py-2 px-3">
                    <UBadge :color="u.is_admin ? 'primary' : 'neutral'" variant="soft">
                      {{ u.is_admin ? 'Admin' : 'Usuário' }}
                    </UBadge>
                  </td>
                  <td class="py-2 px-3">
                    <UBadge :color="u.is_active ? 'success' : 'error'" variant="soft">
                      {{ u.is_active ? 'Ativo' : 'Inativo' }}
                    </UBadge>
                  </td>
                  <td class="py-2 px-3">
                    <div class="flex items-center justify-end gap-2">
                      <UButton
                        size="xs" variant="ghost" color="neutral"
                        :disabled="u.id === user?.id"
                        @click="toggleAdmin(u)"
                      >
                        {{ u.is_admin ? 'Rebaixar' : 'Tornar admin' }}
                      </UButton>
                      <UButton
                        size="xs" variant="ghost"
                        :color="u.is_active ? 'error' : 'success'"
                        :disabled="u.id === user?.id"
                        @click="toggleAtivo(u)"
                      >
                        {{ u.is_active ? 'Desativar' : 'Reativar' }}
                      </UButton>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </UCard>
      </div>
    </template>
  </UDashboardPanel>
</template>

<script setup lang="ts">
interface ApiUser {
  id: number
  username: string
  first_name: string
  last_name: string
  email: string
  is_admin: boolean
  is_active: boolean
}

const { $api } = useNuxtApp()
const { user } = useAuth()

const users = ref<ApiUser[]>([])
const pending = ref(true)

const novo = reactive({
  username: '', email: '', first_name: '', last_name: '', password: '', is_admin: false,
})
const criando = ref(false)
const msg = ref('')
const msgColor = ref<'success' | 'error'>('success')

async function carregar() {
  pending.value = true
  try {
    const res = await $api<{ results: ApiUser[] }>('/api/users/?page_size=500')
    users.value = res.results
  } finally {
    pending.value = false
  }
}

async function criar() {
  msg.value = ''
  criando.value = true
  try {
    await $api('/api/users/', { method: 'POST', body: { ...novo } })
    msgColor.value = 'success'
    msg.value = `Usuário "${novo.username}" criado.`
    Object.assign(novo, { username: '', email: '', first_name: '', last_name: '', password: '', is_admin: false })
    await carregar()
  } catch (e: any) {
    msgColor.value = 'error'
    const d = e?.data
    msg.value = d?.username?.[0] ?? d?.password?.[0] ?? d?.detail ?? 'Erro ao criar usuário.'
  } finally {
    criando.value = false
  }
}

async function toggleAdmin(u: ApiUser) {
  await $api(`/api/users/${u.id}/`, { method: 'PATCH', body: { is_admin: !u.is_admin } })
  await carregar()
}

async function toggleAtivo(u: ApiUser) {
  if (u.is_active) {
    await $api(`/api/users/${u.id}/`, { method: 'DELETE' }) // soft-delete → desativa
  } else {
    await $api(`/api/users/${u.id}/`, { method: 'PATCH', body: { is_active: true } })
  }
  await carregar()
}

onMounted(carregar)
</script>
