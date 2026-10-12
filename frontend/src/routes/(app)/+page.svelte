<script lang="ts">
	import { onMount } from 'svelte';
	import { FileText, Users, UserCog, Wallet } from '@lucide/svelte';
	import { api } from '../../lib/api/client';
	import InlineAlert from '../../lib/components/InlineAlert.svelte';
	import PageHeader from '../../lib/components/PageHeader.svelte';
	import { formatCurrency } from '../../lib/format';

	type Summary = {
		clientes: number;
		usuarios: number;
		cotizaciones: number;
		cotizaciones_borrador: number;
		total_cotizado: number;
	};

	let summary = $state<Summary | null>(null);
	let error = $state('');

	onMount(async () => {
		try {
			summary = await api.get<Summary>('/dashboard');
		} catch {
			error = 'No se pudo cargar el resumen.';
		}
	});

	const cards = $derived([
		{ label: 'Clientes activos', icon: Users, value: summary ? String(summary.clientes) : '—' },
		{ label: 'Usuarios activos', icon: UserCog, value: summary ? String(summary.usuarios) : '—' },
		{
			label: 'Cotizaciones',
			icon: FileText,
			value: summary ? String(summary.cotizaciones) : '—'
		},
		{
			label: 'Total cotizado',
			icon: Wallet,
			value: summary ? formatCurrency(summary.total_cotizado) : '—'
		}
	]);
</script>

<PageHeader title="Dashboard" subtitle="Resumen del sistema" />

{#if error}
	<div class="mt-6"><InlineAlert tone="error">{error}</InlineAlert></div>
{/if}

<section class="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
	{#each cards as card (card.label)}
		{@const Icon = card.icon}
		<div class="rounded-brand border border-line bg-surface p-4">
			<div class="flex items-center gap-2 text-ink-2">
				<Icon size={16} aria-hidden="true" />
				<span class="text-[13px] font-medium">{card.label}</span>
			</div>
			<p class="mt-2 text-[28px] font-semibold">{card.value}</p>
		</div>
	{/each}
</section>

{#if summary}
	<p class="mt-6 rounded-brand border border-line bg-surface-2 px-4 py-3 text-[14px] text-ink-2">
		Cotizaciones en borrador: <span class="font-medium text-ink"
			>{summary.cotizaciones_borrador}</span
		>
	</p>
{/if}
