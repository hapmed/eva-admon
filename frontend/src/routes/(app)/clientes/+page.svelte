<script lang="ts">
	import { onMount } from 'svelte';
	import { Pencil, Trash2 } from '@lucide/svelte';
	import { ApiError, api } from '../../../lib/api/client';
	import Button from '../../../lib/components/Button.svelte';
	import DataTable from '../../../lib/components/DataTable.svelte';
	import InlineAlert from '../../../lib/components/InlineAlert.svelte';
	import Modal from '../../../lib/components/Modal.svelte';
	import PageHeader from '../../../lib/components/PageHeader.svelte';
	import Paginator from '../../../lib/components/Paginator.svelte';
	import type { Page } from '../../../lib/types';
	import { inputClass, labelClass, labelTextClass } from '../../../lib/ui';

	type Contacto = { id?: number; nombre: string; email: string };
	type Cliente = {
		id: number;
		rfc: string;
		nombre: string;
		condiciones_pago: string;
		activo: boolean;
		contactos: Contacto[];
	};

	let clientes = $state<Cliente[]>([]);
	let total = $state(0);
	let pages = $state(0);
	let page = $state(1);
	let loading = $state(true);
	let error = $state('');
	let search = $state('');
	let activo = $state('true');

	let showForm = $state(false);
	let saving = $state(false);
	let formError = $state('');
	let editingId = $state<number | null>(null);
	let form = $state({
		nombre: '',
		rfc: '',
		condiciones_pago: '',
		activo: true,
		contactos: [] as Contacto[]
	});

	async function load(targetPage = 1) {
		loading = true;
		error = '';
		page = targetPage;
		try {
			const params = new URLSearchParams({
				page: String(targetPage),
				page_size: '20',
				activo
			});
			if (search) params.set('search', search);
			const data = await api.get<Page<Cliente>>(`/clientes?${params.toString()}`);
			clientes = data.items;
			total = data.total;
			pages = data.pages;
		} catch {
			error = 'No se pudieron cargar los clientes.';
		} finally {
			loading = false;
		}
	}

	onMount(() => load(1));

	function openCreate() {
		editingId = null;
		form = { nombre: '', rfc: '', condiciones_pago: '', activo: true, contactos: [] };
		formError = '';
		showForm = true;
	}

	function openEdit(cliente: Cliente) {
		editingId = cliente.id;
		form = {
			nombre: cliente.nombre,
			rfc: cliente.rfc,
			condiciones_pago: cliente.condiciones_pago,
			activo: cliente.activo,
			contactos: cliente.contactos.map((c) => ({ nombre: c.nombre, email: c.email }))
		};
		formError = '';
		showForm = true;
	}

	function addContacto() {
		form.contactos = [...form.contactos, { nombre: '', email: '' }];
	}

	function removeContacto(index: number) {
		form.contactos = form.contactos.filter((_, i) => i !== index);
	}

	async function save() {
		formError = '';
		saving = true;
		try {
			const payload = {
				nombre: form.nombre,
				rfc: form.rfc,
				condiciones_pago: form.condiciones_pago,
				activo: form.activo,
				contactos: form.contactos.filter((c) => c.nombre && c.email)
			};
			if (editingId) await api.patch(`/clientes/${editingId}`, payload);
			else await api.post('/clientes', payload);
			showForm = false;
			await load(page);
		} catch (err) {
			formError = err instanceof ApiError ? err.message : 'No se pudo guardar el cliente.';
		} finally {
			saving = false;
		}
	}

	async function desactivar(cliente: Cliente) {
		if (!confirm(`¿Desactivar al cliente ${cliente.nombre}?`)) return;
		await api.delete(`/clientes/${cliente.id}`);
		await load(page);
	}
</script>

<PageHeader title="Clientes" subtitle="Altas, bajas y cambios de clientes">
	{#snippet actions()}
		<Button variant="primary" onclick={openCreate}>Nuevo cliente</Button>
	{/snippet}
</PageHeader>

<div class="mt-6 flex flex-col gap-4">
	<div class="flex flex-wrap items-end gap-3">
		<input
			class="{inputClass} max-w-sm"
			placeholder="Buscar por nombre o RFC"
			bind:value={search}
			oninput={() => load(1)}
		/>
		<label class="flex flex-col gap-1 text-[14px]">
			<span class={labelTextClass}>Estado</span>
			<select class={inputClass} bind:value={activo} onchange={() => load(1)}>
				<option value="true">Activos</option>
				<option value="false">Inactivos</option>
			</select>
		</label>
	</div>

	{#if error}<InlineAlert tone="error">{error}</InlineAlert>{/if}

	{#if loading}
		<p class="text-[14px] text-ink-3">Cargando…</p>
	{:else}
		<DataTable
			columns={[
				{ key: 'rfc', label: 'RFC' },
				{ key: 'nombre', label: 'Nombre' },
				{ key: 'condiciones_pago', label: 'Condiciones de pago' }
			]}
			rows={clientes}
			emptyTitle="Sin clientes"
			emptyDescription="Crea el primer cliente con «Nuevo cliente»."
		>
			{#snippet actions(row)}
				{@const cliente = row as unknown as Cliente}
				<div class="flex justify-end gap-1">
					<button
						class="inline-flex h-9 w-9 items-center justify-center rounded-[10px] hover:bg-surface-2"
						title="Editar"
						onclick={() => openEdit(cliente)}
					>
						<Pencil size={16} aria-hidden="true" />
					</button>
					<button
						class="inline-flex h-9 w-9 items-center justify-center rounded-[10px] text-danger hover:bg-surface-2"
						title="Desactivar"
						onclick={() => desactivar(cliente)}
					>
						<Trash2 size={16} aria-hidden="true" />
					</button>
				</div>
			{/snippet}
		</DataTable>
		<Paginator {page} {pages} {total} onPage={load} />
	{/if}
</div>

<Modal bind:open={showForm} title={editingId ? 'Editar cliente' : 'Nuevo cliente'}>
	<div class="flex flex-col gap-3 text-[14px]">
		<label class={labelClass}>
			<span class={labelTextClass}>Nombre</span>
			<input class={inputClass} bind:value={form.nombre} />
		</label>
		<label class={labelClass}>
			<span class={labelTextClass}>RFC</span>
			<input class={inputClass} bind:value={form.rfc} />
		</label>
		<label class={labelClass}>
			<span class={labelTextClass}>Condiciones de pago</span>
			<textarea class="{inputClass} py-2" rows="2" bind:value={form.condiciones_pago}></textarea>
		</label>
		<label class="flex items-center gap-2">
			<input type="checkbox" bind:checked={form.activo} />
			<span>Activo</span>
		</label>

		<div class="mt-2 flex items-center justify-between">
			<span class="font-medium">Contactos</span>
			<Button variant="ghost" onclick={addContacto}>Agregar contacto</Button>
		</div>
		{#each form.contactos as contacto, index (index)}
			<div class="flex items-end gap-2">
				<label class={labelClass + ' flex-1'}>
					<span class={labelTextClass}>Nombre</span>
					<input class={inputClass} bind:value={contacto.nombre} />
				</label>
				<label class={labelClass + ' flex-1'}>
					<span class={labelTextClass}>Correo</span>
					<input class={inputClass} type="email" bind:value={contacto.email} />
				</label>
				<button
					class="mb-1 inline-flex h-9 w-9 items-center justify-center rounded-[10px] text-danger hover:bg-surface-2"
					title="Quitar"
					onclick={() => removeContacto(index)}
				>
					<Trash2 size={16} aria-hidden="true" />
				</button>
			</div>
		{/each}

		{#if formError}<InlineAlert tone="error">{formError}</InlineAlert>{/if}
	</div>
	{#snippet footer()}
		<Button variant="secondary" onclick={() => (showForm = false)}>Cancelar</Button>
		<Button variant="primary" onclick={save} disabled={saving}
			>{saving ? 'Guardando…' : 'Guardar'}</Button
		>
	{/snippet}
</Modal>
