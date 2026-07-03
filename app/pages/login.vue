<template>
  <div class="min-h-svh flex items-center justify-center p-6 bg-default">
    <UCard class="w-full max-w-sm">
      <template #header>
        <div class="flex items-center gap-2">
          <UIcon name="i-heroicons-signal" class="text-primary size-7" />
          <div>
            <p class="font-semibold">FTTHWatcher</p>
            <p class="text-xs text-muted">Acesse o painel</p>
          </div>
        </div>
      </template>

      <form class="flex flex-col gap-4" @submit.prevent="onSubmit">
        <UFormField label="Usuário">
          <UInput v-model="username" autofocus placeholder="admin" class="w-full" />
        </UFormField>

        <UFormField label="Senha">
          <UInput v-model="password" type="password" placeholder="••••••••" class="w-full" />
        </UFormField>

        <UAlert
          v-if="error"
          color="error"
          variant="soft"
          :title="error"
          icon="i-heroicons-exclamation-triangle"
        />

        <UButton type="submit" block :loading="loading">Entrar</UButton>
      </form>
    </UCard>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const { login } = useAuth()
const router = useRouter()

async function onSubmit() {
  error.value = ''
  loading.value = true
  try {
    await login(username.value, password.value)
    await router.push('/')
  } catch (e: any) {
    error.value = e?.data?.detail ?? 'Não foi possível entrar. Verifique suas credenciais.'
  } finally {
    loading.value = false
  }
}
</script>
