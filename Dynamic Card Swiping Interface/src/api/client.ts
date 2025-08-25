export function getBaseUrl(): string {
	const fromEnv = (import.meta as any).env?.VITE_API_BASE_URL as string | undefined;
	if (fromEnv && typeof fromEnv === 'string' && fromEnv.trim().length > 0) return fromEnv.trim().replace(/\/$/, '');
	return window.location.origin;
}

export function getAccessToken(): string | null {
	const fromEnv = (import.meta as any).env?.VITE_TEST_ACCESS_TOKEN as string | undefined;
	if (fromEnv && typeof fromEnv === 'string' && fromEnv.trim().length > 0) return fromEnv.trim();
	try {
		const fromStorage = window.localStorage.getItem('access_token');
		return fromStorage && fromStorage.length > 0 ? fromStorage : null;
	} catch {
		return null;
	}
}

export async function apiGet<T>(path: string, init?: RequestInit): Promise<T> {
	const baseUrl = getBaseUrl();
	const token = getAccessToken();
	const resp = await fetch(`${baseUrl}${path}`, {
		method: 'GET',
		headers: {
			'Accept': 'application/json',
			...(token ? { 'Authorization': `Bearer ${token}` } : {}),
			...(init?.headers || {}),
		},
		...init,
	});
	if (!resp.ok) {
		const text = await resp.text().catch(() => '');
		throw new Error(`GET ${path} failed: ${resp.status} ${text}`);
	}
	return resp.json() as Promise<T>;
}

export async function apiPost<T>(path: string, body?: unknown, init?: RequestInit): Promise<T> {
	const baseUrl = getBaseUrl();
	const token = getAccessToken();
	const resp = await fetch(`${baseUrl}${path}`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'Accept': 'application/json',
			...(token ? { 'Authorization': `Bearer ${token}` } : {}),
			...(init?.headers || {}),
		},
		body: body !== undefined ? JSON.stringify(body) : undefined,
		...init,
	});
	if (!resp.ok) {
		const text = await resp.text().catch(() => '');
		throw new Error(`POST ${path} failed: ${resp.status} ${text}`);
	}
	const contentType = resp.headers.get('Content-Type') || '';
	if (!contentType.includes('application/json')) return undefined as unknown as T;
	return resp.json() as Promise<T>;
} 