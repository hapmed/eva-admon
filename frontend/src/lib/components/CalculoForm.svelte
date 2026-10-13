<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { FileText, Plus, Trash2 } from '@lucide/svelte';
	import { ApiError, api } from '../api/client';
	import { formatCurrency } from '../format';
	import type { Page } from '../types';
	import { inputClass, labelClass, labelTextClass } from '../ui';
	import Button from './Button.svelte';
	import InlineAlert from './InlineAlert.svelte';
	import Modal from './Modal.svelte';
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
		id?: number;
		partida: string;
		tipo: 'servicio' | 'material';
		descripcion: string;
		modelo: string;
		cantidad: number;
		precio_compra_unitario: number;
		porcentaje_aumento: number;
		precio_venta_unitario: number;
		proveedor: string;
		tiempo_entrega_dias: number;
	};
	type Calculo = {
		id: number;
		folio: string;
		cliente_id: number;
		fecha: string;
		moneda: string;
		notas: string;
		items: Item[];
	};

	let { calculoId = null }: { calculoId?: number | null } = $props();

	let clientes = $state<Cliente[]>([]);
	let servicios = $state<Catalogo[]>([]);
	let materiales = $state<Catalogo[]>([]);
	let folio = $state('');
	let loading = $state(true);
	let saving = $state(false);
	let error = $state('');

	let showGenerar = $state(false);
	let generating = $state(false);
	let generarError = $state('');
	let seleccion = $state<Record<number, boolean>>({});
	let cotizacionGenerada = $state<{ id: number; folio: string } | null>(null);

	let form = $state({
		cliente_id: 0,
		fecha: new Date().toISOString().slice(0, 10),
		moneda: 'MXN',
		notas: '',
		items: [] as Item[]
	});
	let tipoCambio = $state(0);

	function compraTotal(item: Item): number {
		return (Number(item.cantidad) || 0) * (Number(item.precio_compra_unitario) || 0);
	}
	function ventaUnitaria(item: Item): number {
		if (item.tipo === 'material') {
			return (
				(Number(item.precio_compra_unitario) || 0) *
				(1 + (Number(item.porcentaje_aumento) || 0) / 100)
			);
		}
		return Number(item.precio_venta_unitario) || 0;
	}
	function ventaTotal(item: Item): number {
		return ventaUnitaria(item) * (Number(item.cantidad) || 0);
	}

	const ventaTotalCalc = $derived(form.items.reduce((s, i) => s + ventaTotal(i), 0));
	const costoTotalCalc = $derived(form.items.reduce((s, i) => s + compraTotal(i), 0));
	const gananciaCalc = $derived(ventaTotalCalc - costoTotalCalc);

	function clienteNombre(): string {
		return clientes.find((c) => c.id === Number(form.cliente_id))?.nombre ?? '';
	}

	onMount(async () => {
		try {
			const [cs, ss, ms, config] = await Promise.all([
				api.get<Page<Cliente>>('/clientes?page_size=100&activo=true'),
				api.get<Page<Catalogo>>('/servicios?page_size=100&activo=true'),
				api.get<Page<Catalogo>>('/materiales?page_size=100&activo=true'),
				api.get<{ tipo_cambio_usd: number }>('/configuracion')
			]);
			clientes = cs.items;
			servicios = ss.items;
			materiales = ms.items;
			tipoCambio = Number(config.tipo_cambio_usd ?? 0);
			if (calculoId) {
				const c = await api.get<Calculo>(`/calculos/${calculoId}`);
				folio = c.folio;
				form = {
					cliente_id: c.cliente_id,
					fecha: c.fecha,
					moneda: c.moneda ?? 'MXN',
					notas: c.notas,
					items: c.items.map((i) => ({ ...i, tipo: i.tipo }))
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
				partida: String(form.items.length + 1),
				tipo: 'material',
				descripcion: '',
				modelo: '',
				cantidad: 1,
				precio_compra_unitario: 0,
				porcentaje_aumento: 25,
				precio_venta_unitario: 0,
				proveedor: '',
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
				partida: String(form.items.length + 1),
				tipo,
				descripcion: found.nombre,
				modelo: tipo === 'servicio' ? clienteNombre() : '',
				cantidad: 1,
				precio_compra_unitario: Number(found.precio_unitario),
				porcentaje_aumento: 25,
				precio_venta_unitario: tipo === 'servicio' ? Number(found.precio_unitario) : 0,
				proveedor: '',
				tiempo_entrega_dias: 0
			}
		];
	}

	function onTipoChange(item: Item) {
		if (item.tipo === 'servicio' && !item.modelo) item.modelo = clienteNombre();
	}

	async function save(): Promise<number | null> {
		error = '';
		if (!form.cliente_id) {
			error = 'Selecciona un cliente.';
			return null;
		}
		saving = true;
		try {
			const payload = {
				cliente_id: Number(form.cliente_id),
				fecha: form.fecha,
				moneda: form.moneda,
				notas: form.notas,
				items: form.items.map((i) => ({
					partida: i.partida,
					tipo: i.tipo,
					descripcion: i.descripcion,
					modelo: i.modelo,
					cantidad: Number(i.cantidad),
					precio_compra_unitario: Number(i.precio_compra_unitario),
					porcentaje_aumento: Number(i.porcentaje_aumento),
					precio_venta_unitario: Number(i.precio_venta_unitario),
					proveedor: i.proveedor,
					tiempo_entrega_dias: Number(i.tiempo_entrega_dias)
				}))
			};
			if (calculoId) {
				await api.patch(`/calculos/${calculoId}`, payload);
				await goto('/calculos');
				return calculoId;
			}
			const created = await api.post<Calculo>('/calculos', payload);
			await goto(`/calculos/${created.id}`);
			return created.id;
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'No se pudo guardar el cálculo.';
			return null;
		} finally {
			saving = false;
		}
	}

	function abrirGenerar() {
		seleccion = {};
		for (const item of form.items) if (item.id) seleccion[item.id] = true;
		generarError = '';
		cotizacionGenerada = null;
		showGenerar = true;
	}

	async function generar() {
		generarError = '';
		const ids = Object.entries(seleccion)
			.filter(([, v]) => v)
			.map(([k]) => Number(k));
		if (ids.length === 0) {
			generarError = 'Selecciona al menos una partida.';
			return;
		}
		if (!calculoId) {
			generarError = 'Guarda el cálculo antes de generar la cotización.';
			return;
		}
		generating = true;
		try {
			const cot = await api.post<{ id: number; folio: string }>(
				`/calculos/${calculoId}/cotizacion`,
				{ item_ids: ids }
			);
			cotizacionGenerada = { id: cot.id, folio: cot.folio };
		} catch (err) {
			generarError = err instanceof ApiError ? err.message : 'No se pudo generar la cotización.';
		} finally {
			generating = false;
		}
	}
</script>

<PageHeader
	title={calculoId ? `Cálculo ${folio}` : 'Nuevo cálculo'}
	subtitle="Estimación de costo y margen (interno)"
>
	{#snippet actions()}
		<Button variant="secondary" href="/calculos">Volver</Button>
		{#if calculoId}
			<Button variant="secondary" onclick={abrirGenerar}>
				<FileText size={16} aria-hidden="true" /> Generar cotización
			</Button>
		{/if}
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
		{#if cotizacionGenerada}
			<InlineAlert tone="success">
				Cotización generada: <a
					class="font-medium underline"
					href={`/cotizaciones/${cotizacionGenerada.id}`}>{cotizacionGenerada.folio}</a
				>
			</InlineAlert>
		{/if}

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
				<span class={labelTextClass}>Moneda</span>
				<select class={inputClass} bind:value={form.moneda}>
					<option value="MXN">MXN (pesos)</option>
					<option value="USD">USD (dólares)</option>
				</select>
			</label>
			<label class={labelClass}>
				<span class={labelTextClass}>Notas</span>
				<input class={inputClass} bind:value={form.notas} />
			</label>
		</div>

		{#if form.moneda === 'USD'}
			<InlineAlert tone="info">
				Moneda USD. Referencia: 1 USD = ${tipoCambio ? tipoCambio.toFixed(4) : '—'} MXN.
			</InlineAlert>
		{/if}

		<div class="rounded-brand border border-line bg-surface p-4">
			<div class="flex flex-wrap items-center gap-2">
				<span class="text-[14px] font-medium">Partidas</span>
				<div class="ml-auto flex flex-wrap items-center gap-2">
					<select
						class="{inputClass} min-h-10 w-auto"
						onchange={(e) => {
							const v = Number((e.target as HTMLSelectElement).value);
							addFromCatalogo('servicio', v);
							(e.target as HTMLSelectElement).value = '';
						}}
					>
						<option value={0}>+ Servicio</option>
						{#each servicios as s (s.id)}<option value={s.id}>{s.codigo} · {s.nombre}</option
							>{/each}
					</select>
					<select
						class="{inputClass} min-h-10 w-auto"
						onchange={(e) => {
							const v = Number((e.target as HTMLSelectElement).value);
							addFromCatalogo('material', v);
							(e.target as HTMLSelectElement).value = '';
						}}
					>
						<option value={0}>+ Material</option>
						{#each materiales as m (m.id)}<option value={m.id}>{m.codigo} · {m.nombre}</option
							>{/each}
					</select>
					<Button variant="secondary" onclick={addItem}>
						<Plus size={16} aria-hidden="true" /> Partida
					</Button>
				</div>
			</div>

			<div class="mt-3 overflow-x-auto">
				<table class="w-full border-collapse text-left text-[13px]">
					<thead>
						<tr class="border-b border-line text-ink-2">
							<th class="px-2 py-2 font-medium">Partida</th>
							<th class="px-2 py-2 font-medium">Tipo</th>
							<th class="px-2 py-2 font-medium">Cant.</th>
							<th class="px-2 py-2 font-medium">Descripción</th>
							<th class="px-2 py-2 font-medium">Modelo</th>
							<th class="px-2 py-2 font-medium">P. compra u.</th>
							<th class="px-2 py-2 font-medium">P. compra t.</th>
							<th class="px-2 py-2 font-medium">% aum.</th>
							<th class="px-2 py-2 font-medium">P. venta u.</th>
							<th class="px-2 py-2 font-medium">P. venta t.</th>
							<th class="px-2 py-2 font-medium">Proveedor</th>
							<th class="px-2 py-2 font-medium">Entrega (d)</th>
							<th></th>
						</tr>
					</thead>
					<tbody>
						{#each form.items as item, index (index)}
							<tr class="border-b border-line last:border-0 align-top">
								<td class="px-2 py-2"
									><input class="{inputClass} w-20" bind:value={item.partida} /></td
								>
								<td class="px-2 py-2">
									<select
										class="{inputClass} w-32"
										bind:value={item.tipo}
										onchange={() => onTipoChange(item)}
									>
										<option value="servicio">Servicio</option>
										<option value="material">Material</option>
									</select>
								</td>
								<td class="px-2 py-2"
									><input
										class="{inputClass} w-16"
										type="number"
										step="0.001"
										min="0"
										bind:value={item.cantidad}
									/></td
								>
								<td class="px-2 py-2">
									<textarea
										class="{inputClass} min-h-[44px] w-72 py-2"
										rows="2"
										bind:value={item.descripcion}></textarea>
								</td>
								<td class="px-2 py-2"
									><input class="{inputClass} w-40" bind:value={item.modelo} /></td
								>
								<td class="px-2 py-2"
									><input
										class="{inputClass} w-28"
										type="number"
										step="0.01"
										min="0"
										bind:value={item.precio_compra_unitario}
									/></td
								>
								<td class="px-2 py-2 text-right whitespace-nowrap"
									>{formatCurrency(compraTotal(item), form.moneda)}</td
								>
								<td class="px-2 py-2">
									{#if item.tipo === 'material'}
										<input
											class="{inputClass} w-20"
											type="number"
											step="0.01"
											min="0"
											bind:value={item.porcentaje_aumento}
										/>
									{:else}
										<span class="text-ink-3">—</span>
									{/if}
								</td>
								<td class="px-2 py-2">
									{#if item.tipo === 'material'}
										<span class="whitespace-nowrap"
											>{formatCurrency(ventaUnitaria(item), form.moneda)}</span
										>
									{:else}
										<input
											class="{inputClass} w-28"
											type="number"
											step="0.01"
											min="0"
											bind:value={item.precio_venta_unitario}
										/>
									{/if}
								</td>
								<td class="px-2 py-2 text-right whitespace-nowrap"
									>{formatCurrency(ventaTotal(item), form.moneda)}</td
								>
								<td class="px-2 py-2"
									><input class="{inputClass} w-36" bind:value={item.proveedor} /></td
								>
								<td class="px-2 py-2"
									><input
										class="{inputClass} w-20"
										type="number"
										step="1"
										min="0"
										bind:value={item.tiempo_entrega_dias}
									/></td
								>
								<td class="px-2 py-2 text-right">
									<button
										class="inline-flex h-9 w-9 items-center justify-center rounded-[10px] text-danger hover:bg-surface-2"
										title="Quitar"
										onclick={() => removeItem(index)}
									>
										<Trash2 size={16} aria-hidden="true" />
									</button>
								</td>
							</tr>
						{/each}
						{#if form.items.length === 0}
							<tr
								><td colspan="13" class="px-2 py-6 text-center text-ink-3"
									>Sin partidas. Agrega una o elige del catálogo.</td
								></tr
							>
						{/if}
					</tbody>
				</table>
			</div>

			<div class="mt-4 flex justify-end">
				<dl class="w-64 space-y-1 text-[14px]">
					<div class="flex justify-between">
						<dt class="text-ink-2">Costo total</dt>
						<dd>{formatCurrency(costoTotalCalc, form.moneda)}</dd>
					</div>
					<div class="flex justify-between">
						<dt class="text-ink-2">Venta total</dt>
						<dd>{formatCurrency(ventaTotalCalc, form.moneda)}</dd>
					</div>
					<div class="flex justify-between border-t border-line pt-1 text-[16px] font-semibold">
						<dt>Ganancia total</dt>
						<dd>{formatCurrency(gananciaCalc, form.moneda)}</dd>
					</div>
				</dl>
			</div>
		</div>
	</div>
{/if}

<Modal bind:open={showGenerar} title="Generar cotización desde el cálculo">
	<div class="flex flex-col gap-3 text-[14px]">
		<p class="text-ink-2">
			Elige qué partidas del cálculo se incluirán (mantienen el precio de venta).
		</p>
		<ul class="flex flex-col gap-1">
			{#each form.items as item, index (index)}
				{#if item.id}
					<li class="flex items-center gap-2">
						<label class="flex items-center gap-2">
							<input type="checkbox" bind:checked={seleccion[item.id]} />
							<span
								>{item.partida || index + 1} · {item.descripcion ||
									item.modelo ||
									'(sin descripción)'}</span
							>
						</label>
						<span class="ml-auto text-ink-2">{formatCurrency(ventaTotal(item), form.moneda)}</span>
					</li>
				{/if}
			{/each}
		</ul>
		{#if generarError}<InlineAlert tone="error">{generarError}</InlineAlert>{/if}
		{#if cotizacionGenerada}
			<InlineAlert tone="success">
				Cotización <a class="font-medium underline" href={`/cotizaciones/${cotizacionGenerada.id}`}
					>{cotizacionGenerada.folio}</a
				> creada.
			</InlineAlert>
		{/if}
	</div>
	{#snippet footer()}
		<Button variant="secondary" onclick={() => (showGenerar = false)}>Cerrar</Button>
		<Button variant="primary" onclick={generar} disabled={generating}>
			{generating ? 'Generando…' : 'Generar cotización'}
		</Button>
	{/snippet}
</Modal>
