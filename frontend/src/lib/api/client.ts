import { getToken } from '../auth';

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

export class ApiError extends Error {
	readonly status: number;

	constructor(status: number, message: string) {
		super(message);
		this.name = 'ApiError';
		this.status = status;
	}
}

function authHeaders(): Record<string, string> {
	const token = getToken();
	return token ? { Authorization: `Bearer ${token}` } : {};
}

function detailFrom(data: unknown, status: number): string {
	if (data && typeof data === 'object' && 'detail' in data) {
		const detail = (data as { detail: unknown }).detail;
		if (typeof detail === 'string') return detail;
		if (Array.isArray(detail)) return 'Datos inválidos en el formulario.';
	}
	return `Error ${status}`;
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
	const headers: Record<string, string> = { Accept: 'application/json', ...authHeaders() };
	if (body !== undefined) headers['Content-Type'] = 'application/json';

	const response = await fetch(`${BASE_URL}${path}`, {
		method,
		headers,
		body: body !== undefined ? JSON.stringify(body) : undefined
	});

	const text = await response.text();
	const data = text ? JSON.parse(text) : null;
	if (!response.ok) throw new ApiError(response.status, detailFrom(data, response.status));
	return data as T;
}

export const api = {
	get: <T>(path: string) => request<T>('GET', path),
	post: <T>(path: string, body: unknown = {}) => request<T>('POST', path, body),
	patch: <T>(path: string, body: unknown) => request<T>('PATCH', path, body),
	put: <T>(path: string, body: unknown) => request<T>('PUT', path, body),
	delete: <T = void>(path: string) => request<T>('DELETE', path),
	async upload<T>(path: string, form: FormData): Promise<T> {
		const response = await fetch(`${BASE_URL}${path}`, {
			method: 'POST',
			headers: { Accept: 'application/json', ...authHeaders() },
			body: form
		});
		const text = await response.text();
		const data = text ? JSON.parse(text) : null;
		if (!response.ok) throw new ApiError(response.status, detailFrom(data, response.status));
		return data as T;
	},
	async blob(path: string): Promise<Blob> {
		const response = await fetch(`${BASE_URL}${path}`, { headers: authHeaders() });
		if (!response.ok) {
			const text = await response.text();
			let data: unknown = null;
			try {
				data = text ? JSON.parse(text) : null;
			} catch {
				data = null;
			}
			throw new ApiError(response.status, detailFrom(data, response.status));
		}
		return response.blob();
	}
};
