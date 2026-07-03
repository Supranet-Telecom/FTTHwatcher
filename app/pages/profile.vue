<template>
  <UDashboardPanel grow>
    <template #header>
      <UDashboardNavbar title="Meu Perfil" />
    </template>

    <template #body>
      <div class="flex flex-col gap-6 max-w-lg">
        <!-- Dados da conta -->
        <UCard>
          <template #header>
            <span class="font-semibold text-sm">Dados da conta</span>
          </template>
          <div class="flex flex-col gap-3 text-sm">
            <div class="flex justify-between">
              <span class="text-muted">Usuário</span>
              <span class="font-medium">{{ user?.username }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-muted">E-mail</span>
              <span class="font-medium">{{ user?.email || '—' }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-muted">Papel</span>
              <UBadge :color="user?.is_admin ? 'primary' : 'neutral'" variant="soft">
                {{ user?.is_admin ? 'Administrador' : 'Usuário' }}
              </UBadge>
            </div>
          </div>
        </UCard>

        <!-- Trocar senha -->
        <UCard>
          <template #header>
            <span class="font-semibold text-sm">Trocar senha</span>
          </template>

          <form class="flex flex-col gap-4" @submit.prevent="onSubmit">
            <UFormField label="Senha atual">
              <UInput v-model="current" type="password" class="w-full" />
            </UFormField>
            <UFormField label="Nova senha">
              <UInput v-model="novaSenha" type="password" class="w-full" />
            </UFormField>
            <UFormField label="Confirmar nova senha">
              <UInput v-model="confirma" type="password" class="w-full" />
            </UFormField>

            <UAlert v-if="msg" :color="msgColor" variant="soft" :title="msg" />

            <UButton type="submit" :loading="loading" class="self-start">Salvar</UButton>
          </form>
        </UCard>
      </div>
    </template>
  </UDashboardPanel>
</template>

<script setup lang="ts">
const { user, changePassword } = useAuth()

const current = ref('')
const novaSenha = ref('')
const confirma = ref('')
const loading = ref(false)
const msg = ref('')
const msgColor = ref<'success' | 'error'>('success')

async function onSubmit() {
  msg.value = ''
  if (novaSenha.value !== confirma.value) {
    msgColor.value = 'error'
    msg.value = 'A confirmação não corresponde à nova senha.'
    return
  }
  loading.value = true
  try {
    await changePassword(current.value, novaSenha.value)
    msgColor.value = 'success'
    msg.value = 'Senha alterada com sucesso.'
    current.value = novaSenha.value = confirma.value = ''
  } catch (e: any) {
    msgColor.value = 'error'
    const detail = e?.data
    msg.value = detail?.current_password?.[0]
      ?? detail?.new_password?.[0]
      ?? detail?.detail
      ?? 'Não foi possível alterar a senha.'
  } finally {
    loading.value = false
  }
}
</script>
