<script lang="ts">
	import { onMount } from 'svelte';
	import { ApiError, api } from '../../../lib/api/client';
	import { user } from '../../../lib/auth';
	import Button from '../../../lib/components/Button.svelte';
	import EmptyState from '../../../lib/components/EmptyState.svelte';
	import InlineAlert from '../../../lib/components/InlineAlert.svelte';
	import PageHeader from '../../../lib/components/PageHeader.svelte';
	import { inputClass, labelClass, labelTextClass } from '../../../lib/ui';

	type Empresa = {
		razon_social: string;
		nombre_comercial: string;
		rfc: string;
		telefono: string;
		email: string;
		whatsapp: string;
		iva_porcentaje: number;
		moneda: string;
		tiene_logo: boolean;
	};

	const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

	let form = $state<Empresa>({
		razon_social: '',
		nombre_comercial: '',
		rfc: '',
		telefono: '',
		email: '',
		whatsapp: '',
		iva_porcentaje: 16,
		moneda: 'MXN',
		tiene_logo: false
	});
	let loading = $state(true);
	let saving = $state(false);
	let message = $state('');
	let error = $state('');
	let logoVersion = $state(Date.now());

	const isAdmin = $derived($user?.rol === 'admin');

	async function load() {
		loading = true;
		try {
			form = await api.get<Empresa>('/configuracion');
		} catch {
			error = 'No se pudo cargar la configuración.';
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		if (isAdmin) load();
		else loading = false;
	});

	async function save() {
		error = '';
		message = '';
		saving = true;
		try {
			form = await api.put<Empresa>('/configuracion', {
				razon_social: form.razon_social,
				nombre_comercial: form.nombre_comercial,
				rfc: form.rfc,
				telefono: form.telefono,
				email: form.email,
				whatsapp: form.whatsapp,
				iva_porcentaje: Number(form.iva_porcentaje),
				moneda: form.moneda
			});
			message = 'Configuración guardada.';
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'No se pudo guardar.';
		} finally {
			saving = false;
		}
	}

	async function uploadLogo(event: Event) {
		const input = event.target as HTMLInputElement;
		if (!input.files?.length) return;
		const data = new FormData();
		data.append('file', input.files[0]);
		error = '';
		message = '';
		try {
			form = await api.upload<Empresa>('/configuracion/logo', data);
			logoVersion = Date.now();
			message = 'Logo actualizado.';
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'No se pudo subir el logo.';
		} finally {
			input.value = '';
		}
	}
</script>

{#if !isAdmin}
	<EmptyState
		title="Sin permisos"
		description="Solo los administradores pueden editar la configuración."
	/>
{:else}
	<PageHeader title="Configuración" subtitle="Datos de la empresa emisora" />

	{#if loading}
		<p class="mt-6 text-[14px] text-ink-3">Cargando…</p>
	{:else}
		<div class="mt-6 flex max-w-2xl flex-col gap-4">
			{#if message}<InlineAlert tone="success">{message}</InlineAlert>{/if}
			{#if error}<InlineAlert tone="error">{error}</InlineAlert>{/if}

			<div class="rounded-brand border border-line bg-surface p-4">
				<p class="text-[14px] font-medium">Logo</p>
				<div class="mt-3 flex items-center gap-4">
					{#if form.tiene_logo}
						<img
							src="{API_BASE}/configuracion/logo?v={logoVersion}"
							alt="Logo de la empresa"
							class="h-16 w-16 rounded-[12px] border border-line object-contain"
						/>
					{:else}
						<div
							class="flex h-16 w-16 items-center justify-center rounded-[12px] border border-dashed border-line text-[12px] text-ink-3"
						>
							Sin logo
						</div>
					{/if}
					<label
						class="cursor-pointer rounded-[12px] bg-surface-2 px-4 py-2 text-[14px] font-medium hover:bg-line"
					>
						Subir logo
						<input
							type="file"
							accept="image/png,image/jpeg,image/webp"
							class="hidden"
							onchange={uploadLogo}
						/>
					</label>
				</div>
			</div>

			<div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
				<label class={labelClass}>
					<span class={labelTextClass}>Razón social</span>
					<input class={inputClass} bind:value={form.razon_social} />
				</label>
				<label class={labelClass}>
					<span class={labelTextClass}>Nombre comercial</span>
					<input class={inputClass} bind:value={form.nombre_comercial} />
				</label>
				<label class={labelClass}>
					<span class={labelTextClass}>RFC</span>
					<input class={inputClass} bind:value={form.rfc} />
				</label>
				<label class={labelClass}>
					<span class={labelTextClass}>Teléfono</span>
					<input class={inputClass} bind:value={form.telefono} />
				</label>
				<label class={labelClass}>
					<span class={labelTextClass}>Correo electrónico</span>
					<input class={inputClass} type="email" bind:value={form.email} />
				</label>
				<label class={labelClass}>
					<span class={labelTextClass}>WhatsApp</span>
					<input class={inputClass} bind:value={form.whatsapp} />
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
					<span class={labelTextClass}>Moneda</span>
					<input class={inputClass} bind:value={form.moneda} />
				</label>
			</div>

			<div class="flex justify-end">
				<Button variant="primary" onclick={save} disabled={saving}
					>{saving ? 'Guardando…' : 'Guardar cambios'}</Button
				>
			</div>
		</div>
	{/if}
{/if}
