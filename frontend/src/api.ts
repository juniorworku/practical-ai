export async function api<T>(path: string, options: RequestInit = {}, authenticated = true): Promise<T> {
  const token = authenticated ? sessionStorage.getItem('academy-token') : null
  const response = await fetch(`/api/${path}`, { ...options, headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Token ${token}` } : {}), ...options.headers } })
  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    if (response.status === 401) { sessionStorage.removeItem('academy-token'); window.dispatchEvent(new Event('academy-expired')) }
    throw new Error(data.detail ? String(data.detail) : Object.values(data).flat().join(' ') || `Request failed (${response.status})`)
  }
  return response.status === 204 ? undefined as T : response.json()
}
