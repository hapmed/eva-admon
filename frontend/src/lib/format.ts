export function formatDate(value: string | null | undefined): string {
	return value ? value.slice(0, 10) : '—';
}

export function joinOrDash(values: string[]): string {
	return values.length ? values.join(', ') : '—';
}

export function formatCurrency(value: number | string | null | undefined, moneda = 'MXN'): string {
	if (value == null) return '—';
	const amount = typeof value === 'string' ? Number(value) : value;
	if (Number.isNaN(amount)) return '—';
	return new Intl.NumberFormat('es-MX', { style: 'currency', currency: moneda }).format(amount);
}
