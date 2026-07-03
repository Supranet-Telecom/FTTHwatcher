/**
 * Fornece um cliente `$api` baseado em $fetch que:
 *  - envia cookies (sessão) em toda requisição
 *  - injeta o header X-CSRFToken nas requisições que alteram dados (POST/PUT/PATCH/DELETE)
 *
 * GETs do dashboard podem continuar usando $fetch direto — cookies same-origin
 * são enviados automaticamente e métodos seguros não precisam de CSRF.
 */
function getCookie(name: string): string | null {
  if (!import.meta.client) return null
  const match = document.cookie.match(new RegExp('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)'))
  return match ? decodeURIComponent(match.pop()!) : null
}

export default defineNuxtPlugin(() => {
  const api = $fetch.create({
    credentials: 'include',
    onRequest({ options }) {
      const method = (options.method ?? 'GET').toUpperCase()
      if (!['GET', 'HEAD', 'OPTIONS'].includes(method)) {
        const token = getCookie('csrftoken')
        if (token) {
          const headers = new Headers(options.headers as HeadersInit)
          headers.set('X-CSRFToken', token)
          options.headers = headers
        }
      }
    },
  })

  return { provide: { api } }
})
