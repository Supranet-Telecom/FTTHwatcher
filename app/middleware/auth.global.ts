/**
 * Middleware global de autenticação (roda apenas no cliente, pois a sessão
 * depende do cookie do navegador). Redireciona para /login quando não autenticado
 * e bloqueia /admin para quem não é administrador.
 */
export default defineNuxtRouteMiddleware(async (to) => {
  // A sessão vive no cookie do navegador — só verificamos no cliente.
  if (import.meta.server) return

  const { user, isAdmin, fetchMe } = useAuth()

  // Primeira navegação: descobre se há sessão ativa
  if (user.value === undefined) {
    await fetchMe()
  }

  const publicPages = ['/login']
  const isPublic = publicPages.includes(to.path)

  if (!user.value && !isPublic) {
    return navigateTo('/login')
  }

  if (user.value && to.path === '/login') {
    return navigateTo('/')
  }

  // Rotas de admin exigem papel de administrador
  if (to.path.startsWith('/admin') && !isAdmin.value) {
    return navigateTo('/')
  }
})
