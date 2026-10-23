export function storageKey(kind: string, lesson: number | string) {
  return `academy:v1:${sessionStorage.getItem("academy-user") || "guest"}:${kind}:${lesson}`;
}
export function readLocal<T>(key: string): T | null {
  try {
    return JSON.parse(localStorage.getItem(key) || "null") as T | null;
  } catch {
    return null;
  }
}
export function writeLocal(key: string, value: unknown) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch {
    return false;
  }
}
export function removeLocal(key: string) {
  try {
    localStorage.removeItem(key);
  } catch {
    /* Browser storage can be disabled. */
  }
}
