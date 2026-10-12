<script lang="ts">
	import { onMount } from 'svelte';
	import { Download, Pencil, Trash2 } from '@lucide/svelte';
	import { api } from '../../../lib/api/client';
	import Button from '../../../lib/components/Button.svelte';
	import DataTable from '../../../lib/components/DataTable.svelte';
	import InlineAlert from '../../../lib/components/InlineAlert.svelte';
	import PageHeader from '../../../lib/components/PageHeader.svelte';
	import StatusBadge from '../../../lib/components/StatusBadge.svelte';
	import { formatCurrency, formatDate } from '../../../lib/format';

	type Cotizacion = {
		id: number;
		folio: string;
		cliente: { numero_cliente: string; nombre: string };
		fecha: string;
		estado: 'borrador' | 'enviada' | 'aceptada' | 'rechazada' | 'cancelada';
		total: number;
	};

	let cotizaciones = $state<Cotizacion[]>([]);
	let loading = $state(true);
	let error = $state('');

	const estados: Record<
		Cotizacion['estado'],
		{ status: 'active' | 'warning' | 'critical' | 'unknown'; label: string }
	> = {
		borrador: { status: 'unknown', label: 'Borrador' },
		enviada: { status: 'warning', label: 'Enviada' },
		aceptada: { status: 'active', label: 'Aceptada' },
		rechazada: { status: 'critical', label: 'Rechazada' },
		cancelada: { status: 'critical', label: 'Cancelada' }
	};

	async function load() {
		loading = true;
		error = '';
		try {
			cotizaciones = await api.get<Cotizacion[]>('/cotizaciones');
		} catch {
			error = 'No se pudieron cargar las cotizaciones.';
		} finally {
			loading = false;
		}
	}

	onMount(load);

	async function descargarPdf(cotizacion: Cotizacion) {
		try {
			const blob = await api.blob(`/cotizaciones/${cotizacion.id}/pdf`);
			const url = URL.createObjectURL(blob);
			window.open(url, '_blank');
			setTimeout(() => URL.revokeObjectURL(url), 10000);
		} catch {
			error = 'No se pudo generar el PDF.';
		}
	}

	async function cancelar(cotizacion: Cotizacion) {
		if (!confirm(`¿Cancelar la cotización ${cotizacion.folio}?`)) return;
		await api.delete(`/cotizaciones/${cotizacion.id}`);
		await load();
	}
</script>

<PageHeader title="Cotizaciones" subtitle="Cotizaciones de servicio y materiales">
	{#snippet actions()}
		<Button variant="primary" href="/cotizaciones/nueva">Nueva cotización</Button>
	{/snippet}
</PageHeader>

<div class="mt-6 flex flex-col gap-4">
	{#if error}<InlineAlert tone="error">{error}</InlineAlert>{/if}

	{#if loading}
		<p class="text-[14px] text-ink-3">Cargando…</p>
	{:else}
		<DataTable
			columns={[
				{ key: 'folio', label: 'Folio' },
				{ key: 'cliente', label: 'Cliente' },
				{ key: 'fecha', label: 'Fecha' },
				{ key: 'total', label: 'Total' }
			]}
			rows={cotizaciones.map((c) => ({
				...c,
				cliente: `${c.cliente.numero_cliente} · ${c.cliente.nombre}`,
				fecha: formatDate(c.fecha),
				total: formatCurrency(c.total)
			}))}
			emptyTitle="Sin cotizaciones"
			emptyDescription="Crea la primera con «Nueva cotización»."
		>
			{#snippet actions(row)}
				{@const current = cotizaciones.find((c) => c.id === (row as { id: number }).id)}
				{#if current}
					<div class="flex items-center justify-end gap-1">
						<StatusBadge
							status={estados[current.estado].status}
							label={estados[current.estado].label}
						/>
						<a
							href={`/cotizaciones/${current.id}`}
							class="inline-flex h-9 w-9 items-center justify-center rounded-[10px] hover:bg-surface-2"
							title="Editar"
						>
							<Pencil size={16} aria-hidden="true" />
						</a>
						<button
							class="inline-flex h-9 w-9 items-center justify-center rounded-[10px] hover:bg-surface-2"
							title="PDF"
							onclick={() => descargarPdf(current)}
						>
							<Download size={16} aria-hidden="true" />
						</button>
						<button
							class="inline-flex h-9 w-9 items-center justify-center rounded-[10px] text-danger hover:bg-surface-2"
							title="Cancelar"
							onclick={() => cancelar(current)}
						>
							<Trash2 size={16} aria-hidden="true" />
						</button>
					</div>
				{/if}
			{/snippet}
		</DataTable>
	{/if}
</div>
