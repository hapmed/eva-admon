<script lang="ts">
	import { onMount } from 'svelte';
	import { Pencil, Trash2 } from '@lucide/svelte';
	import { ApiError, api } from '../../../lib/api/client';
	import { user } from '../../../lib/auth';
	import Button from '../../../lib/components/Button.svelte';
	import DataTable from '../../../lib/components/DataTable.svelte';
	import EmptyState from '../../../lib/components/EmptyState.svelte';
	import InlineAlert from '../../../lib/components/InlineAlert.svelte';
	import Modal from '../../../lib/components/Modal.svelte';
	import PageHeader from '../../../lib/components/PageHeader.svelte';
	import Paginator from '../../../lib/components/Paginator.svelte';
	import StatusBadge from '../../../lib/components/StatusBadge.svelte';
	import type { Page } from '../../../lib/types';
	import { inputClass, labelClass, labelTextClass } from '../../../lib/ui';

	type Usuario = {
		id: number;
		email: string;
		nombre: string;
		rol: 'admin' | 'ventas' | 'consulta';
		activo: boolean;
	};

	let usuarios = $state<Usuario[]>([]);
	let total = $state(0);
	let pages = $state(0);
	let page = $state(1);
	let loading = $state(true);
	let error = $state('');
	let search = $state('');
	let rol = $state('');

	let showForm = $state(false);
	let saving = $state(false);
	let formError = $state('');
	let editingId = $state<number | null>(null);
	let form = $state({
		email: '',
		nombre: '',
		rol: 'consulta' as Usuario['rol'],
		activo: true,
		password: ''
	});

	const isAdmin = $derived($user?.rol === 'admin');

	async function load(targetPage = 1) {
		loading = true;
		error = '';
		page = targetPage;
		try {
			const params = new URLSearchParams({ page: String(targetPage), page_size: '20' });
			if (search) params.set('search', search);
			if (rol) params.set('rol', rol);
			const data = await api.get<Page<Usuario>>(`/usuarios?${params.toString()}`);
			usuarios = data.items;
			total = data.total;
			pages = data.pages;
		} catch {
			error = 'No se pudieron cargar los usuarios.';
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		if (isAdmin) load(1);
		else loading = false;
	});

	function openCreate() {
		editingId = null;
		form = { email: '', nombre: '', rol: 'consulta', activo: true, password: '' };
		formError = '';
		showForm = true;
	}

	function openEdit(usuario: Usuario) {
		editingId = usuario.id;
		form = {
			email: usuario.email,
			nombre: usuario.nombre,
			rol: usuario.rol,
			activo: usuario.activo,
			password: ''
		};
		formError = '';
		showForm = true;
	}

	async function save() {
		formError = '';
		saving = true;
		try {
			if (editingId) {
				const payload: Record<string, unknown> = {
					email: form.email,
					nombre: form.nombre,
					rol: form.rol,
					activo: form.activo
				};
				if (form.password) payload.password = form.password;
				await api.patch(`/usuarios/${editingId}`, payload);
			} else {
				await api.post('/usuarios', form);
			}
			showForm = false;
			await load(page);
		} catch (err) {
			formError = err instanceof ApiError ? err.message : 'No se pudo guardar el usuario.';
		} finally {
			saving = false;
		}
	}

	async function desactivar(usuario: Usuario) {
		if (!confirm(`¿Desactivar a ${usuario.nombre}?`)) return;
		try {
			await api.delete(`/usuarios/${usuario.id}`);
			await load(page);
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'No se pudo desactivar.';
		}
	}
</script>

{#if !isAdmin}
	<EmptyState
		title="Sin permisos"
		description="Solo los administradores pueden gestionar usuarios."
	/>
{:else}
	<PageHeader title="Usuarios" subtitle="Usuarios y roles del sistema">
		{#snippet actions()}
			<Button variant="primary" onclick={openCreate}>Nuevo usuario</Button>
		{/snippet}
	</PageHeader>

	<div class="mt-6 flex flex-col gap-4">
		<div class="flex flex-wrap items-end gap-3">
			<input
				class="{inputClass} max-w-sm"
				placeholder="Buscar por nombre o correo"
				bind:value={search}
				oninput={() => load(1)}
			/>
			<label class="flex flex-col gap-1 text-[14px]">
				<span class={labelTextClass}>Rol</span>
				<select class={inputClass} bind:value={rol} onchange={() => load(1)}>
					<option value="">Todos</option>
					<option value="admin">Administrador</option>
					<option value="ventas">Ventas</option>
					<option value="consulta">Consulta</option>
				</select>
			</label>
		</div>

		{#if error}<InlineAlert tone="error">{error}</InlineAlert>{/if}

		{#if loading}
			<p class="text-[14px] text-ink-3">Cargando…</p>
		{:else}
			<DataTable
				columns={[
					{ key: 'nombre', label: 'Nombre' },
					{ key: 'email', label: 'Correo' },
					{ key: 'rol', label: 'Rol' }
				]}
				rows={usuarios}
				emptyTitle="Sin usuarios"
				emptyDescription="Crea el primero con «Nuevo usuario»."
			>
				{#snippet actions(row)}
					{@const usuario = row as unknown as Usuario}
					<div class="flex items-center justify-end gap-1">
						<StatusBadge
							status={usuario.activo ? 'active' : 'unknown'}
							label={usuario.activo ? 'Activo' : 'Inactivo'}
						/>
						<button
							class="inline-flex h-9 w-9 items-center justify-center rounded-[10px] hover:bg-surface-2"
							title="Editar"
							onclick={() => openEdit(usuario)}
						>
							<Pencil size={16} aria-hidden="true" />
						</button>
						<button
							class="inline-flex h-9 w-9 items-center justify-center rounded-[10px] text-danger hover:bg-surface-2"
							title="Desactivar"
							onclick={() => desactivar(usuario)}
						>
							<Trash2 size={16} aria-hidden="true" />
						</button>
					</div>
				{/snippet}
			</DataTable>
			<Paginator {page} {pages} {total} onPage={load} />
		{/if}
	</div>

	<Modal bind:open={showForm} title={editingId ? 'Editar usuario' : 'Nuevo usuario'}>
		<div class="flex flex-col gap-3 text-[14px]">
			<label class={labelClass}>
				<span class={labelTextClass}>Nombre</span>
				<input class={inputClass} bind:value={form.nombre} />
			</label>
			<label class={labelClass}>
				<span class={labelTextClass}>Correo</span>
				<input class={inputClass} type="email" bind:value={form.email} />
			</label>
			<label class={labelClass}>
				<span class={labelTextClass}>Rol</span>
				<select class={inputClass} bind:value={form.rol}>
					<option value="admin">Administrador</option>
					<option value="ventas">Ventas</option>
					<option value="consulta">Consulta</option>
				</select>
			</label>
			<label class={labelClass}>
				<span class={labelTextClass}
					>{editingId ? 'Nueva contraseña (opcional)' : 'Contraseña'}</span
				>
				<input
					class={inputClass}
					type="password"
					autocomplete="new-password"
					bind:value={form.password}
				/>
			</label>
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
{/if}
