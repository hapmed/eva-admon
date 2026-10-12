<script lang="ts">
	import { onMount } from 'svelte';
	import { Pencil, Trash2 } from '@lucide/svelte';
	import { ApiError, api } from '../api/client';
	import { inputClass, labelClass, labelTextClass } from '../ui';
	import Button from './Button.svelte';
	import DataTable from './DataTable.svelte';
	import InlineAlert from './InlineAlert.svelte';
	import Modal from './Modal.svelte';
	import PageHeader from './PageHeader.svelte';

	type Item = {
		id: number;
		codigo: string;
		nombre: string;
		descripcion: string;
		unidad: string;
		precio_unitario: number;
		activo: boolean;
	};

	let {
		title,
		subtitle,
		endpoint,
		unidadDefault
	}: { title: string; subtitle: string; endpoint: string; unidadDefault: string } = $props();

	let items = $state<Item[]>([]);
	let loading = $state(true);
	let error = $state('');
	let search = $state('');

	let showForm = $state(false);
	let saving = $state(false);
	let formError = $state('');
	let editingId = $state<number | null>(null);
	let form = $state({
		codigo: '',
		nombre: '',
		descripcion: '',
		unidad: '',
		precio_unitario: 0,
		activo: true
	});

	async function load() {
		loading = true;
		error = '';
		try {
			const query = search ? `?search=${encodeURIComponent(search)}` : '';
			items = await api.get<Item[]>(`${endpoint}${query}`);
		} catch {
			error = `No se pudieron cargar los registros.`;
		} finally {
			loading = false;
		}
	}

	onMount(load);

	function openCreate() {
		editingId = null;
		form = {
			codigo: '',
			nombre: '',
			descripcion: '',
			unidad: unidadDefault,
			precio_unitario: 0,
			activo: true
		};
		formError = '';
		showForm = true;
	}

	function openEdit(item: Item) {
		editingId = item.id;
		form = {
			codigo: item.codigo,
			nombre: item.nombre,
			descripcion: item.descripcion,
			unidad: item.unidad,
			precio_unitario: Number(item.precio_unitario),
			activo: item.activo
		};
		formError = '';
		showForm = true;
	}

	async function save() {
		formError = '';
		saving = true;
		try {
			if (editingId) await api.patch(`${endpoint}/${editingId}`, form);
			else await api.post(endpoint, form);
			showForm = false;
			await load();
		} catch (err) {
			formError = err instanceof ApiError ? err.message : 'No se pudo guardar.';
		} finally {
			saving = false;
		}
	}

	async function desactivar(item: Item) {
		if (!confirm(`¿Desactivar «${item.nombre}»?`)) return;
		await api.delete(`${endpoint}/${item.id}`);
		await load();
	}
</script>

<PageHeader {title} {subtitle}>
	{#snippet actions()}
		<Button variant="primary" onclick={openCreate}>Nuevo</Button>
	{/snippet}
</PageHeader>

<div class="mt-6 flex flex-col gap-4">
	<input
		class="{inputClass} max-w-sm"
		placeholder="Buscar por nombre o código"
		bind:value={search}
		oninput={load}
	/>

	{#if error}<InlineAlert tone="error">{error}</InlineAlert>{/if}

	{#if loading}
		<p class="text-[14px] text-ink-3">Cargando…</p>
	{:else}
		<DataTable
			columns={[
				{ key: 'codigo', label: 'Código' },
				{ key: 'nombre', label: 'Nombre' },
				{ key: 'unidad', label: 'Unidad' },
				{ key: 'precio_unitario', label: 'Precio' }
			]}
			rows={items}
			emptyTitle="Sin registros"
			emptyDescription="Crea el primero con «Nuevo»."
		>
			{#snippet actions(row)}
				{@const item = row as unknown as Item}
				<div class="flex justify-end gap-1">
					<button
						class="inline-flex h-9 w-9 items-center justify-center rounded-[10px] hover:bg-surface-2"
						title="Editar"
						onclick={() => openEdit(item)}
					>
						<Pencil size={16} aria-hidden="true" />
					</button>
					<button
						class="inline-flex h-9 w-9 items-center justify-center rounded-[10px] text-danger hover:bg-surface-2"
						title="Desactivar"
						onclick={() => desactivar(item)}
					>
						<Trash2 size={16} aria-hidden="true" />
					</button>
				</div>
			{/snippet}
		</DataTable>
	{/if}
</div>

<Modal bind:open={showForm} title={editingId ? 'Editar' : 'Nuevo'}>
	<div class="flex flex-col gap-3 text-[14px]">
		<label class={labelClass}>
			<span class={labelTextClass}>Código</span>
			<input class={inputClass} bind:value={form.codigo} />
		</label>
		<label class={labelClass}>
			<span class={labelTextClass}>Nombre</span>
			<input class={inputClass} bind:value={form.nombre} />
		</label>
		<label class={labelClass}>
			<span class={labelTextClass}>Descripción</span>
			<textarea class="{inputClass} py-2" rows="2" bind:value={form.descripcion}></textarea>
		</label>
		<div class="grid grid-cols-2 gap-3">
			<label class={labelClass}>
				<span class={labelTextClass}>Unidad</span>
				<input class={inputClass} bind:value={form.unidad} />
			</label>
			<label class={labelClass}>
				<span class={labelTextClass}>Precio</span>
				<input
					class={inputClass}
					type="number"
					step="0.01"
					min="0"
					bind:value={form.precio_unitario}
				/>
			</label>
		</div>
		<label class="flex items-center gap-2">
			<input type="checkbox" bind:checked={form.activo} />
			<span>Activo</span>
		</label>
		{#if formError}<InlineAlert tone="error">{formError}</InlineAlert>{/if}
	</div>
	{#snippet footer()}
		<Button variant="secondary" onclick={() => (showForm = false)}>Cancelar</Button>
		<Button variant="primary" onclick={save} disabled={saving}
			>{saving ? 'Guardando…' : 'Guardar'}</Button
		>
	{/snippet}
</Modal>
