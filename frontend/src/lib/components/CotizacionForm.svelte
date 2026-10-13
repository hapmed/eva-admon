<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { Plus, Trash2 } from '@lucide/svelte';
	import { ApiError, api } from '../api/client';
	import { formatCurrency } from '../format';
	import type { Page } from '../types';
	import { inputClass, labelClass, labelTextClass } from '../ui';
	import Button from './Button.svelte';
	import InlineAlert from './InlineAlert.svelte';
	import PageHeader from './PageHeader.svelte';

	type Cliente = { id: number; rfc: string; nombre: string };
	type Catalogo = {
		id: number;
		codigo: string;
		nombre: string;
		unidad: string;
		precio_unitario: number;
	};
	type Item = {
		tipo: 'servicio' | 'material';
		descripcion: string;
		unidad: string;
		cantidad: number;
		precio_unitario: number;
		descuento_porcentaje: number;
		tiempo_entrega_dias: number;
	};
	type Cotizacion = {
		id: number;
		folio: string;
		cliente_id: number;
		fecha: string;
		valida_hasta: string | null;
		estado: string;
		iva_porcentaje: number;
		moneda: string;
		notas: string;
		calculo_id: number | null;
		items: Item[];
	};

	let { cotizacionId = null }: { cotizacionId?: number | null } = $props();

	let clientes = $state<Cliente[]>([]);
	let servicios = $state<Catalogo[]>([]);
	let materiales = $state<Catalogo[]>([]);
	let folio = $state('');
	let calculoOrigen = $state<number | null>(null);
	let loading = $state(true);
	let saving = $state(false);
	let error = $state('');

	let form = $state({
		cliente_id: 0,
		fecha: new Date().toISOString().slice(0, 10),
		valida_hasta: '',
		iva_porcentaje: 16,
		estado: 'borrador',
		moneda: 'MXN',
		notas: '',
		items: [] as Item[]
	});
	let tipoCambio = $state(0);

	const subtotal = $derived(
		form.items.reduce((sum, item) => sum + item.cantidad * item.precio_unitario, 0)
	);
	const descuento = $derived(
		form.items.reduce(
			(sum, item) => sum + item.cantidad * item.precio_unitario * (item.descuento_porcentaje / 100),
			0
		)
	);
	const ivaTotal = $derived((subtotal - descuento) * (form.iva_porcentaje / 100));
	const total = $derived(subtotal - descuento + ivaTotal);
	const tiempoEntrega = $derived(
		form.items.reduce((max, item) => Math.max(max, Number(item.tiempo_entrega_dias) || 0), 0)
	);

	onMount(async () => {
		try {
			const [cs, ss, ms, config] = await Promise.all([
				api.get<Page<Cliente>>('/clientes?page_size=100&activo=true'),
				api.get<Page<Catalogo>>('/servicios?page_size=100&activo=true'),
				api.get<Page<Catalogo>>('/materiales?page_size=100&activo=true'),
				api.get<{ iva_porcentaje: number; tipo_cambio_usd: number }>('/configuracion')
			]);
			clientes = cs.items;
			servicios = ss.items;
			materiales = ms.items;
			form.iva_porcentaje = Number(config.iva_porcentaje ?? 16);
			tipoCambio = Number(config.tipo_cambio_usd ?? 0);
			if (cotizacionId) {
				const cot = await api.get<Cotizacion>(`/cotizaciones/${cotizacionId}`);
				folio = cot.folio;
				calculoOrigen = cot.calculo_id ?? null;
				form = {
					cliente_id: cot.cliente_id,
					fecha: cot.fecha,
					valida_hasta: cot.valida_hasta ?? '',
					iva_porcentaje: Number(cot.iva_porcentaje),
					estado: cot.estado,
					moneda: cot.moneda ?? 'MXN',
					notas: cot.notas,
					items: cot.items.map((i) => ({ ...i, tipo: i.tipo }))
				};
			}
		} catch {
			error = 'No se pudo cargar la información.';
		} finally {
			loading = false;
		}
	});

	function addItem() {
		form.items = [
			...form.items,
			{
				tipo: 'servicio',
				descripcion: '',
				unidad: '',
				cantidad: 1,
				precio_unitario: 0,
				descuento_porcentaje: 0,
				tiempo_entrega_dias: 0
			}
		];
	}

	function removeItem(index: number) {
		form.items = form.items.filter((_, i) => i !== index);
	}

	function addFromCatalogo(tipo: 'servicio' | 'material', id: number) {
		if (!id) return;
		const source = tipo === 'servicio' ? servicios : materiales;
		const found = source.find((c) => c.id === id);
		if (!found) return;
		form.items = [
			...form.items,
			{
				tipo,
				descripcion: found.nombre,
				unidad: found.unidad,
				cantidad: 1,
				precio_unitario: Number(found.precio_unitario),
				descuento_porcentaje: 0,
				tiempo_entrega_dias: 0
			}
		];
	}

	async function save() {
		error = '';
		if (!form.cliente_id) {
			error = 'Selecciona un cliente.';
			return;
		}
		saving = true;
		try {
			const payload = {
				cliente_id: Number(form.cliente_id),
				fecha: form.fecha,
				valida_hasta: form.valida_hasta || null,
				iva_porcentaje: Number(form.iva_porcentaje),
				estado: form.estado,
				moneda: form.moneda,
				notas: form.notas,
				items: form.items.map((i) => ({
					...i,
					cantidad: Number(i.cantidad),
					precio_unitario: Number(i.precio_unitario),
					descuento_porcentaje: Number(i.descuento_porcentaje),
					tiempo_entrega_dias: Number(i.tiempo_entrega_dias)
				}))
			};
			if (cotizacionId) await api.patch(`/cotizaciones/${cotizacionId}`, payload);
			else await api.post('/cotizaciones', payload);
			await goto('/cotizaciones');
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'No se pudo guardar la cotización.';
		} finally {
			saving = false;
		}
	}
</script>

<PageHeader
	title={cotizacionId ? `Cotización ${folio}` : 'Nueva cotización'}
	subtitle="Servicios y materiales"
>
	{#snippet actions()}
		{#if calculoOrigen}
			<Button variant="secondary" href={`/calculos/${calculoOrigen}`}>Ver cálculo</Button>
		{/if}
		<Button variant="secondary" href="/cotizaciones">Volver</Button>
		<Button variant="primary" onclick={save} disabled={saving}
			>{saving ? 'Guardando…' : 'Guardar'}</Button
		>
	{/snippet}
</PageHeader>

{#if loading}
	<p class="mt-6 text-[14px] text-ink-3">Cargando…</p>
{:else}
	<div class="mt-6 flex flex-col gap-4">
		{#if error}<InlineAlert tone="error">{error}</InlineAlert>{/if}

		<div
			class="grid grid-cols-1 gap-3 rounded-brand border border-line bg-surface p-4 sm:grid-cols-2 lg:grid-cols-4"
		>
			<label class={labelClass}>
				<span class={labelTextClass}>Cliente</span>
				<select class={inputClass} bind:value={form.cliente_id}>
					<option value={0}>Selecciona…</option>
					{#each clientes as cliente (cliente.id)}
						<option value={cliente.id}>{cliente.rfc} · {cliente.nombre}</option>
					{/each}
				</select>
			</label>
			<label class={labelClass}>
				<span class={labelTextClass}>Fecha</span>
				<input class={inputClass} type="date" bind:value={form.fecha} />
			</label>
			<label class={labelClass}>
				<span class={labelTextClass}>Válida hasta</span>
				<input class={inputClass} type="date" bind:value={form.valida_hasta} />
			</label>
			<label class={labelClass}>
				<span class={labelTextClass}>IVA (%)</span>
				<input
					class={inputClass}
					type="number"
					step="0.01"
					min="0"
					max="100"
					bind:value={form.iva_porcentaje}
				/>
			</label>
			<label class={labelClass}>
				<span class={labelTextClass}>Estado</span>
				<select class={inputClass} bind:value={form.estado}>
					<option value="borrador">Borrador</option>
					<option value="enviada">Enviada</option>
					<option value="aceptada">Aceptada</option>
					<option value="rechazada">Rechazada</option>
					<option value="cancelada">Cancelada</option>
				</select>
			</label>
			<label class={labelClass}>
				<span class={labelTextClass}>Moneda</span>
				<select class={inputClass} bind:value={form.moneda}>
					<option value="MXN">MXN (pesos)</option>
					<option value="USD">USD (dólares)</option>
				</select>
			</label>
			<label class="{labelClass} sm:col-span-2 lg:col-span-3">
				<span class={labelTextClass}>Notas</span>
				<input class={inputClass} bind:value={form.notas} />
			</label>
		</div>

		{#if form.moneda === 'USD'}
			<InlineAlert tone="info">
				Moneda USD. Referencia: 1 USD = ${tipoCambio ? tipoCambio.toFixed(4) : '—'} MXN. Los importes
				se capturan en dólares.
			</InlineAlert>
		{/if}

		<div class="rounded-brand border border-line bg-surface p-4">
			<div class="flex flex-wrap items-center gap-2">
				<span class="text-[14px] font-medium">Partidas</span>
				<div class="ml-auto flex flex-wrap items-center gap-2">
					<select
						class="{inputClass} min-h-10 w-auto"
						onchange={(e) => {
							const value = Number((e.target as HTMLSelectElement).value);
							addFromCatalogo('servicio', value);
							(e.target as HTMLSelectElement).value = '';
						}}
					>
						<option value={0}>+ Servicio del catálogo</option>
						{#each servicios as s (s.id)}<option value={s.id}>{s.codigo} · {s.nombre}</option
							>{/each}
					</select>
					<select
						class="{inputClass} min-h-10 w-auto"
						onchange={(e) => {
							const value = Number((e.target as HTMLSelectElement).value);
							addFromCatalogo('material', value);
							(e.target as HTMLSelectElement).value = '';
						}}
					>
						<option value={0}>+ Material del catálogo</option>
						{#each materiales as m (m.id)}<option value={m.id}>{m.codigo} · {m.nombre}</option
							>{/each}
					</select>
					<Button variant="secondary" onclick={addItem}>
						<Plus size={16} aria-hidden="true" /> Línea
					</Button>
				</div>
			</div>

			<div class="mt-3 flex flex-col gap-3">
				{#each form.items as item, index (index)}
					<div class="rounded-brand border border-line bg-surface-2/40 p-3">
						<div class="flex items-center justify-between">
							<span class="text-[13px] font-semibold text-ink-2">Partida {index + 1}</span>
							<button
								class="inline-flex h-9 w-9 items-center justify-center rounded-[10px] text-danger hover:bg-surface-2"
								title="Quitar"
								onclick={() => removeItem(index)}
							>
								<Trash2 size={16} aria-hidden="true" />
							</button>
						</div>
						<label class="{labelClass} mt-2">
							<span class={labelTextClass}>DescripciÃ³n</span>
							<textarea
								class="{inputClass} min-h-[64px] py-2"
								rows="3"
								placeholder="Detalle de la partidaâ€¦"
								bind:value={item.descripcion}></textarea>
						</label>
						<div class="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
							<label class={labelClass}>
								<span class={labelTextClass}>Tipo</span>
								<select class={inputClass} bind:value={item.tipo}>
									<option value="servicio">Servicio</option>
									<option value="material">Material</option>
								</select>
							</label>
							<label class={labelClass}>
								<span class={labelTextClass}>Unidad</span>
								<input class={inputClass} bind:value={item.unidad} />
							</label>
							<label class={labelClass}>
								<span class={labelTextClass}>Cantidad</span>
								<input
									class={inputClass}
									type="number"
									step="0.001"
									min="0"
									bind:value={item.cantidad}
								/>
							</label>
							<label class={labelClass}>
								<span class={labelTextClass}>P. unitario</span>
								<input
									class={inputClass}
									type="number"
									step="0.01"
									min="0"
									bind:value={item.precio_unitario}
								/>
							</label>
							<label class={labelClass}>
								<span class={labelTextClass}>Desc. %</span>
								<input
									class={inputClass}
									type="number"
									step="0.01"
									min="0"
									max="100"
									bind:value={item.descuento_porcentaje}
								/>
							</label>
							<label class={labelClass}>
								<span class={labelTextClass}>Entrega (dÃ­as)</span>
								<input
									class={inputClass}
									type="number"
									step="1"
									min="0"
									bind:value={item.tiempo_entrega_dias}
								/>
							</label>
						</div>
						<div class="mt-3 flex justify-end border-t border-line pt-2 text-[14px]">
							<span class="text-ink-2">Importe:&nbsp;</span>
							<span class="font-semibold">
								{formatCurrency(
									item.cantidad * item.precio_unitario * (1 - item.descuento_porcentaje / 100),
									form.moneda
								)}
							</span>
						</div>
					</div>
				{/each}
				{#if form.items.length === 0}
					<p
						class="rounded-brand border border-dashed border-line px-4 py-6 text-center text-[14px] text-ink-3"
					>
						Sin partidas. Agrega una lÃ­nea o elige del catÃ¡logo.
					</p>
				{/if}
			</div>

			<div class="mt-4 flex justify-end">
				<dl class="w-64 space-y-1 text-[14px]">
					<div class="flex justify-between">
						<dt class="text-ink-2">Subtotal</dt>
						<dd>{formatCurrency(subtotal, form.moneda)}</dd>
					</div>
					<div class="flex justify-between">
						<dt class="text-ink-2">Descuento</dt>
						<dd>{formatCurrency(descuento, form.moneda)}</dd>
					</div>
					<div class="flex justify-between">
						<dt class="text-ink-2">IVA {form.iva_porcentaje}%</dt>
						<dd>{formatCurrency(ivaTotal, form.moneda)}</dd>
					</div>
					<div class="flex justify-between">
						<dt class="text-ink-2">Tiempo de entrega</dt>
						<dd>{tiempoEntrega} {tiempoEntrega === 1 ? 'día' : 'días'}</dd>
					</div>
					<div class="flex justify-between border-t border-line pt-1 text-[16px] font-semibold">
						<dt>Total</dt>
						<dd>{formatCurrency(total, form.moneda)}</dd>
					</div>
				</dl>
			</div>
		</div>
	</div>
{/if}
