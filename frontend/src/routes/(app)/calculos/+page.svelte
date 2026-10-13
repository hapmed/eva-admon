<script lang="ts">
	import { onMount } from 'svelte';
	import { Pencil, Trash2 } from '@lucide/svelte';
	import { api } from '../../../lib/api/client';
	import Button from '../../../lib/components/Button.svelte';
	import DataTable from '../../../lib/components/DataTable.svelte';
	import InlineAlert from '../../../lib/components/InlineAlert.svelte';
	import PageHeader from '../../../lib/components/PageHeader.svelte';
	import Paginator from '../../../lib/components/Paginator.svelte';
	import { formatCurrency, formatDate } from '../../../lib/format';
	import type { Page } from '../../../lib/types';
	import { inputClass } from '../../../lib/ui';

	type Calculo = {
		id: number;
		folio: string;
		cliente: { id: number; rfc: string; nombre: string };
		fecha: string;
		moneda: string;
		venta_total: number;
		ganancia_total: number;
	};

	let calculos = $state<Calculo[]>([]);
	let total = $state(0);
	let pages = $state(0);
	let page = $state(1);
	let loading = $state(true);
	let error = $state('');
	let search = $state('');

	async function load(targetPage = 1) {
		loading = true;
		error = '';
		page = targetPage;
		try {
			const params = new URLSearchParams({ page: String(targetPage), page_size: '20' });
			if (search) params.set('search', search);
			const data = await api.get<Page<Calculo>>(`/calculos?${params.toString()}`);
			calculos = data.items;
			total = data.total;
			pages = data.pages;
		} catch {
			error = 'No se pudieron cargar los cálculos.';
		} finally {
			loading = false;
		}
	}

	onMount(() => load(1));

	async function eliminar(calculo: Calculo) {
		if (!confirm(`¿Eliminar el cálculo ${calculo.folio}?`)) return;
		await api.delete(`/calculos/${calculo.id}`);
		await load(page);
	}
</script>

<PageHeader title="Cálculos" subtitle="Estimación de costo y margen (interno)">
	{#snippet actions()}
		<Button variant="primary" href="/calculos/nuevo">Nuevo cálculo</Button>
	{/snippet}
</PageHeader>

<div class="mt-6 flex flex-col gap-4">
	<input
		class="{inputClass} max-w-sm"
		placeholder="Buscar por folio o cliente"
		bind:value={search}
		oninput={() => load(1)}
	/>

	{#if error}<InlineAlert tone="error">{error}</InlineAlert>{/if}

	{#if loading}
		<p class="text-[14px] text-ink-3">Cargando…</p>
	{:else}
		<DataTable
			columns={[
				{ key: 'folio', label: 'Folio' },
				{ key: 'cliente', label: 'Cliente' },
				{ key: 'fecha', label: 'Fecha' },
				{ key: 'venta_total', label: 'Venta total' },
				{ key: 'ganancia_total', label: 'Ganancia' }
			]}
			rows={calculos.map((c) => ({
				...c,
				cliente: `${c.cliente.rfc} · ${c.cliente.nombre}`,
				fecha: formatDate(c.fecha),
				venta_total: formatCurrency(c.venta_total, c.moneda),
				ganancia_total: formatCurrency(c.ganancia_total, c.moneda)
			}))}
			emptyTitle="Sin cálculos"
			emptyDescription="Crea el primero con «Nuevo cálculo»."
		>
			{#snippet actions(row)}
				{@const item = calculos.find((c) => c.id === (row as { id: number }).id)}
				{#if item}
					<div class="flex items-center justify-end gap-1">
						<a
							href={`/calculos/${item.id}`}
							class="inline-flex h-9 w-9 items-center justify-center rounded-[10px] hover:bg-surface-2"
							title="Editar"
						>
							<Pencil size={16} aria-hidden="true" />
						</a>
						<button
							class="inline-flex h-9 w-9 items-center justify-center rounded-[10px] text-danger hover:bg-surface-2"
							title="Eliminar"
							onclick={() => eliminar(item)}
						>
							<Trash2 size={16} aria-hidden="true" />
						</button>
					</div>
				{/if}
			{/snippet}
		</DataTable>
		<Paginator {page} {pages} {total} onPage={load} />
	{/if}
</div>
