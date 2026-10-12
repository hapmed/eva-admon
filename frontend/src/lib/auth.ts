import { writable } from 'svelte/store';

export type Rol = 'admin' | 'ventas' | 'consulta';

export type User = {
	id: number;
	email: string;
	nombre: string;
	rol: Rol;
	activo: boolean;
};

const TOKEN_KEY = 'admon_token';

export const user = writable<User | null>(null);

export function getToken(): string | null {
	if (typeof localStorage === 'undefined') return null;
	return localStorage.getItem(TOKEN_KEY);
}

export function setSession(token: string, current: User): void {
	localStorage.setItem(TOKEN_KEY, token);
	user.set(current);
}

export function clearSession(): void {
	if (typeof localStorage !== 'undefined') localStorage.removeItem(TOKEN_KEY);
	user.set(null);
}

export function isAdmin(value: User | null): boolean {
	return value?.rol === 'admin';
}
