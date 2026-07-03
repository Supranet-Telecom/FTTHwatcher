/**
 * Estado global de autenticação. `user` é compartilhado via useState,
 * então todos os componentes veem o mesmo estado de login.
 */
export interface AuthUser {
  id: number
  username: string
  first_name: string
  last_name: string
  email: string
  is_admin: boolean
}

export function useAuth() {
  // undefined = ainda não verificado | null = não logado | objeto = logado
  const user = useState<AuthUser | null | undefined>('auth-user', () => undefined)
  const { $api } = useNuxtApp()

  async function fetchMe() {
    try {
      user.value = await $api<AuthUser>('/api/auth/me/')
    } catch {
      user.value = null
    }
    return user.value
  }

  async function login(username: string, password: string) {
    // Garante o cookie CSRF antes do POST de login
    await $api('/api/auth/csrf/')
    user.value = await $api<AuthUser>('/api/auth/login/', {
      method: 'POST',
      body: { username, password },
    })
    return user.value
  }

  async function logout() {
    try {
      await $api('/api/auth/logout/', { method: 'POST' })
    } finally {
      user.value = null
    }
  }

  async function changePassword(current_password: string, new_password: string) {
    return $api('/api/auth/change-password/', {
      method: 'POST',
      body: { current_password, new_password },
    })
  }

  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => !!user.value?.is_admin)

  return { user, isAuthenticated, isAdmin, fetchMe, login, logout, changePassword }
}
