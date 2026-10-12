<script lang="ts">
	import { onMount } from 'svelte';
	import { Download, Eye, Mail, Pencil, Share2, Trash2 } from '@lucide/svelte';
	import { ApiError, api } from '../../../lib/api/client';
	import Button from '../../../lib/components/Button.svelte';
	import DataTable from '../../../lib/components/DataTable.svelte';
	import InlineAlert from '../../../lib/components/InlineAlert.svelte';
	import Modal from '../../../lib/components/Modal.svelte';
	import PageHeader from '../../../lib/components/PageHeader.svelte';
	import Paginator from '../../../lib/components/Paginator.svelte';
	import StatusBadge from '../../../lib/components/StatusBadge.svelte';
	import { formatCurrency, formatDate } from '../../../lib/format';
	import type { Page } from '../../../lib/types';
	import { inputClass, labelClass, labelTextClass } from '../../../lib/ui';

	type ClienteResumen = { id: number; rfc: string; nombre: string };
	type Cotizacion = {
		id: number;
		folio: string;
		cliente: ClienteResumen;
		fecha: string;
		estado: 'borrador' | 'enviada' | 'aceptada' | 'rechazada' | 'cancelada';
		total: number;
	};
	type Contacto = { nombre: string; email: string };

	let cotizaciones = $state<Cotizacion[]>([]);
	let total = $state(0);
	let pages = $state(0);
	let page = $state(1);
	let loading = $state(true);
	let error = $state('');
	let search = $state('');
	let estado = $state('');

	let showSend = $state(false);
	let sending = $state(false);
	let sendError = $state('');
	let sendOk = $state('');
	let current = $state<Cotizacion | null>(null);
	let send = $state({ destinatarios: '', cc: '', asunto: '', mensaje: '' });

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

	async function load(targetPage = 1) {
		loading = true;
		error = '';
		page = targetPage;
		try {
			const params = new URLSearchParams({ page: String(targetPage), page_size: '20' });
			if (search) params.set('search', search);
			if (estado) params.set('estado', estado);
			const data = await api.get<Page<Cotizacion>>(`/cotizaciones?${params.toString()}`);
			cotizaciones = data.items;
			total = data.total;
			pages = data.pages;
		} catch {
			error = 'No se pudieron cargar las cotizaciones.';
		} finally {
			loading = false;
		}
	}

	onMount(() => load(1));

	async function descargarPdf(cotizacion: Cotizacion) {
		try {
			const blob = await api.blob(`/cotizaciones/${cotizacion.id}/pdf`);
			const url = URL.createObjectURL(blob);
			const link = document.createElement('a');
			link.href = url;
			link.download = `cotizacion-${cotizacion.folio}.pdf`;
			link.click();
			setTimeout(() => URL.revokeObjectURL(url), 10000);
		} catch {
			error = 'No se pudo generar el PDF.';
		}
	}

	async function previewPdf(cotizacion: Cotizacion) {
		try {
			const blob = await api.blob(`/cotizaciones/${cotizacion.id}/pdf`);
			const url = URL.createObjectURL(blob);
			window.open(url, '_blank');
			setTimeout(() => URL.revokeObjectURL(url), 60000);
		} catch {
			error = 'No se pudo generar el PDF.';
		}
	}

	async function compartirPdf(cotizacion: Cotizacion) {
		try {
			const blob = await api.blob(`/cotizaciones/${cotizacion.id}/pdf`);
			const filename = `cotizacion-${cotizacion.folio}.pdf`;
			const file = new File([blob], filename, { type: 'application/pdf' });
			const nav = navigator as Navigator & { canShare?: (data: ShareData) => boolean };
			if (nav.share && nav.canShare?.({ files: [file] })) {
				await nav.share({ files: [file], title: `Cotización ${cotizacion.folio}` });
			} else {
				const url = URL.createObjectURL(blob);
				const link = document.createElement('a');
				link.href = url;
				link.download = filename;
				link.click();
				setTimeout(() => URL.revokeObjectURL(url), 10000);
			}
		} catch (err) {
			if ((err as Error).name !== 'AbortError') error = 'No se pudo compartir el PDF.';
		}
	}

	async function openSend(cotizacion: Cotizacion) {
		current = cotizacion;
		sendError = '';
		sendOk = '';
		send = { destinatarios: '', cc: '', asunto: '', mensaje: '' };
		showSend = true;
		try {
			const cliente = await api.get<{ contactos: Contacto[] }>(
				`/clientes/${cotizacion.cliente.id}`
			);
			send.destinatarios = cliente.contactos.map((c) => c.email).join(', ');
		} catch {
			/* sin contactos */
		}
	}

	async function enviar() {
		if (!current) return;
		sendError = '';
		sendOk = '';
		const destinatarios = send.destinatarios
			.split(',')
			.map((s) => s.trim())
			.filter(Boolean);
		if (destinatarios.length === 0) {
			sendError = 'Agrega al menos un destinatario.';
			return;
		}
		sending = true;
		try {
			await api.post(`/cotizaciones/${current.id}/enviar`, {
				destinatarios,
				cc: send.cc
					.split(',')
					.map((s) => s.trim())
					.filter(Boolean),
				asunto: send.asunto || undefined,
				mensaje: send.mensaje || undefined
			});
			sendOk = 'Cotización enviada por correo.';
			await load(page);
		} catch (err) {
			sendError = err instanceof ApiError ? err.message : 'No se pudo enviar.';
		} finally {
			sending = false;
		}
	}

	async function cancelar(cotizacion: Cotizacion) {
		if (!confirm(`¿Cancelar la cotización ${cotizacion.folio}?`)) return;
		await api.delete(`/cotizaciones/${cotizacion.id}`);
		await load(page);
	}
</script>

<PageHeader title="Cotizaciones" subtitle="Cotizaciones de servicio y materiales">
	{#snippet actions()}
		<Button variant="primary" href="/cotizaciones/nueva">Nueva cotización</Button>
	{/snippet}
</PageHeader>

<div class="mt-6 flex flex-col gap-4">
	<div class="flex flex-wrap items-end gap-3">
		<input
			class="{inputClass} max-w-sm"
			placeholder="Buscar por folio o cliente"
			bind:value={search}
			oninput={() => load(1)}
		/>
		<label class="flex flex-col gap-1 text-[14px]">
			<span class={labelTextClass}>Estado</span>
			<select class={inputClass} bind:value={estado} onchange={() => load(1)}>
				<option value="">Todos</option>
				<option value="borrador">Borrador</option>
				<option value="enviada">Enviada</option>
				<option value="aceptada">Aceptada</option>
				<option value="rechazada">Rechazada</option>
				<option value="cancelada">Cancelada</option>
			</select>
		</label>
	</div>

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
				cliente: `${c.cliente.rfc} · ${c.cliente.nombre}`,
				fecha: formatDate(c.fecha),
				total: formatCurrency(c.total)
			}))}
			emptyTitle="Sin cotizaciones"
			emptyDescription="Crea la primera con «Nueva cotización»."
		>
			{#snippet actions(row)}
				{@const item = cotizaciones.find((c) => c.id === (row as { id: number }).id)}
				{#if item}
					<div class="flex flex-wrap items-center justify-end gap-1">
						<StatusBadge status={estados[item.estado].status} label={estados[item.estado].label} />
						<a
							href={`/cotizaciones/${item.id}`}
							class="inline-flex h-9 w-9 items-center justify-center rounded-[10px] hover:bg-surface-2"
							title="Editar"
						>
							<Pencil size={16} aria-hidden="true" />
						</a>
						<button
							class="inline-flex h-9 w-9 items-center justify-center rounded-[10px] hover:bg-surface-2"
							title="Preview del PDF"
							onclick={() => previewPdf(item)}
						>
							<Eye size={16} aria-hidden="true" />
						</button>
						<button
							class="inline-flex h-9 w-9 items-center justify-center rounded-[10px] hover:bg-surface-2"
							title="Descargar PDF"
							onclick={() => descargarPdf(item)}
						>
							<Download size={16} aria-hidden="true" />
						</button>
						<button
							class="inline-flex h-9 w-9 items-center justify-center rounded-[10px] hover:bg-surface-2"
							title="Compartir PDF"
							onclick={() => compartirPdf(item)}
						>
							<Share2 size={16} aria-hidden="true" />
						</button>
						<button
							class="inline-flex h-9 w-9 items-center justify-center rounded-[10px] hover:bg-surface-2"
							title="Enviar por correo"
							onclick={() => openSend(item)}
						>
							<Mail size={16} aria-hidden="true" />
						</button>
						<button
							class="inline-flex h-9 w-9 items-center justify-center rounded-[10px] text-danger hover:bg-surface-2"
							title="Cancelar"
							onclick={() => cancelar(item)}
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

<Modal bind:open={showSend} title="Enviar cotización por correo">
	<div class="flex flex-col gap-3 text-[14px]">
		{#if current}
			<p class="text-ink-2">Cotización <span class="font-medium text-ink">{current.folio}</span></p>
		{/if}
		<label class={labelClass}>
			<span class={labelTextClass}>Destinatarios (separados por coma)</span>
			<input class={inputClass} bind:value={send.destinatarios} placeholder="cliente@ejemplo.com" />
		</label>
		<label class={labelClass}>
			<span class={labelTextClass}>Copia (CC, opcional)</span>
			<input class={inputClass} bind:value={send.cc} />
		</label>
		<label class={labelClass}>
			<span class={labelTextClass}>Asunto (opcional)</span>
			<input class={inputClass} bind:value={send.asunto} />
		</label>
		<label class={labelClass}>
			<span class={labelTextClass}>Mensaje (opcional)</span>
			<textarea class="{inputClass} py-2" rows="3" bind:value={send.mensaje}></textarea>
		</label>
		{#if sendError}<InlineAlert tone="error">{sendError}</InlineAlert>{/if}
		{#if sendOk}<InlineAlert tone="success">{sendOk}</InlineAlert>{/if}
	</div>
	{#snippet footer()}
		<Button variant="secondary" onclick={() => (showSend = false)}>Cerrar</Button>
		<Button variant="primary" onclick={enviar} disabled={sending}
			>{sending ? 'Enviando…' : 'Enviar'}</Button
		>
	{/snippet}
</Modal>
