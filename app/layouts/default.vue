<template>
  <UDashboardGroup>
    <UDashboardSidebar collapsible :default-size="18" :min-size="14" :max-size="25">
      <template #header>
        <div class="flex items-center gap-2 px-2 py-1">
          <UIcon name="i-heroicons-signal" class="text-primary size-6 shrink-0" />
          <span class="font-semibold text-sm truncate">FFTHWatcher</span>
        </div>
      </template>

      <UNavigationMenu
        :items="links"
        orientation="vertical"
        class="px-2"
      />

      <template #footer>
        <UDropdownMenu :items="userMenu" class="w-full">
          <UButton
            color="neutral"
            variant="ghost"
            class="w-full justify-start"
            icon="i-heroicons-user-circle"
            :label="user?.username ?? 'Conta'"
          />
        </UDropdownMenu>
      </template>
    </UDashboardSidebar>

    <slot />
  </UDashboardGroup>
</template>

<script setup lang="ts">
const { user, isAdmin, logout } = useAuth()
const router = useRouter()

const links = computed(() => {
  const base = [
    { label: 'Dashboard', icon: 'i-heroicons-home', to: '/' },
  ]
  if (isAdmin.value) {
    base.push({ label: 'Usuários', icon: 'i-heroicons-users', to: '/admin/users' })
  }
  return [base]
})

const userMenu = computed(() => [
  [
    { label: user.value?.username ?? '', type: 'label' as const },
  ],
  [
    { label: 'Meu perfil', icon: 'i-heroicons-user', to: '/profile' },
  ],
  [
    {
      label: 'Sair',
      icon: 'i-heroicons-arrow-right-on-rectangle',
      onSelect: async () => {
        await logout()
        await router.push('/login')
      },
    },
  ],
])
</script>
