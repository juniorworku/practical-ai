export function csrfToken() {
  return decodeURIComponent(
    document.cookie
      .split("; ")
      .find((value) => value.startsWith("csrftoken="))
      ?.split("=")
      .slice(1)
      .join("=") || "",
  );
}
export function legacyHeaders(): Record<string, string> {
  const token = sessionStorage.getItem("academy-token");
  return token ? { Authorization: `Token ${token}` } : {};
}
export async function api<T>(
  path: string,
  options: RequestInit = {},
  authenticated = true,
): Promise<T> {
  const response = await fetch(`/api/${path}`, {
    ...options,
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      ...(authenticated ? legacyHeaders() : {}),
      ...(csrfToken() ? { "X-CSRFToken": csrfToken() } : {}),
      ...options.headers,
    },
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    if (response.status === 401 && authenticated) {
      sessionStorage.removeItem("academy-token");
      window.dispatchEvent(new Event("academy-expired"));
    }
    throw new Error(
      data.detail
        ? String(data.detail)
        : Object.values(data).flat().join(" ") ||
          `Request failed (${response.status})`,
    );
  }
  return response.status === 204 ? (undefined as T) : response.json();
}
