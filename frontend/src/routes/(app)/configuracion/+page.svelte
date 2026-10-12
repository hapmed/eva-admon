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
		color_primary: string;
		color_secondary: string;
		smtp_activo: boolean;
		smtp_host: string;
		smtp_port: number;
		smtp_security: string;
		smtp_username: string;
		smtp_from_email: string;
		smtp_from_name: string;
		smtp_password_set: boolean;
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
		tiene_logo: false,
		color_primary: '',
		color_secondary: '',
		smtp_activo: false,
		smtp_host: '',
		smtp_port: 587,
		smtp_security: 'tls',
		smtp_username: '',
		smtp_from_email: '',
		smtp_from_name: '',
		smtp_password_set: false
	});
	let smtpPassword = $state('');
	let loading = $state(true);
	let saving = $state(false);
	let message = $state('');
	let error = $state('');
	let logoVersion = $state(Date.now());
	let testDestino = $state('');
	let testMessage = $state('');
	let testError = $state('');
	let testing = $state(false);

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
			const payload: Record<string, unknown> = {
				razon_social: form.razon_social,
				nombre_comercial: form.nombre_comercial,
				rfc: form.rfc,
				telefono: form.telefono,
				email: form.email,
				whatsapp: form.whatsapp,
				iva_porcentaje: Number(form.iva_porcentaje),
				moneda: form.moneda,
				color_primary: form.color_primary,
				color_secondary: form.color_secondary,
				smtp_activo: form.smtp_activo,
				smtp_host: form.smtp_host,
				smtp_port: Number(form.smtp_port),
				smtp_security: form.smtp_security,
				smtp_username: form.smtp_username,
				smtp_from_email: form.smtp_from_email,
				smtp_from_name: form.smtp_from_name
			};
			if (smtpPassword) payload.smtp_password = smtpPassword;
			form = await api.put<Empresa>('/configuracion', payload);
			smtpPassword = '';
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
			message = 'Logo actualizado (se extrajeron los colores).';
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'No se pudo subir el logo.';
		} finally {
			input.value = '';
		}
	}

	async function testSmtp() {
		testError = '';
		testMessage = '';
		if (!testDestino) {
			testError = 'Escribe un correo destino.';
			return;
		}
		testing = true;
		try {
			const res = await api.post<{ mensaje: string }>('/configuracion/smtp/test', {
				destino: testDestino
			});
			testMessage = res.mensaje;
		} catch (err) {
			testError = err instanceof ApiError ? err.message : 'No se pudo enviar la prueba.';
		} finally {
			testing = false;
		}
	}
</script>

{#if !isAdmin}
	<EmptyState
		title="Sin permisos"
		description="Solo los administradores pueden editar la configuración."
	/>
{:else}
	<PageHeader title="Configuración" subtitle="Datos de la empresa, marca y correo" />

	{#if loading}
		<p class="mt-6 text-[14px] text-ink-3">Cargando…</p>
	{:else}
		<div class="mt-6 flex max-w-2xl flex-col gap-4">
			{#if message}<InlineAlert tone="success">{message}</InlineAlert>{/if}
			{#if error}<InlineAlert tone="error">{error}</InlineAlert>{/if}

			<div class="rounded-brand border border-line bg-surface p-4">
				<p class="text-[14px] font-medium">Logo y colores</p>
				<p class="mt-1 text-[13px] text-ink-2">
					Al subir el logo se extraen automáticamente los colores para el PDF. Si no hay logo, se
					usa el de HAPMED.
				</p>
				<div class="mt-3 flex flex-wrap items-center gap-4">
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
					<label class="flex items-center gap-2 text-[14px]">
						<span class={labelTextClass}>Principal</span>
						<input
							type="color"
							class="h-10 w-14 rounded-[10px] border border-line"
							bind:value={form.color_primary}
						/>
					</label>
					<label class="flex items-center gap-2 text-[14px]">
						<span class={labelTextClass}>Secundario</span>
						<input
							type="color"
							class="h-10 w-14 rounded-[10px] border border-line"
							bind:value={form.color_secondary}
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

			<div class="rounded-brand border border-line bg-surface p-4">
				<div class="flex items-center justify-between">
					<p class="text-[14px] font-medium">Correo (SMTP)</p>
					<label class="flex items-center gap-2 text-[14px]">
						<input type="checkbox" bind:checked={form.smtp_activo} />
						<span>Activo</span>
					</label>
				</div>
				<div class="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
					<label class={labelClass}>
						<span class={labelTextClass}>Servidor</span>
						<input class={inputClass} bind:value={form.smtp_host} placeholder="smtp.ejemplo.com" />
					</label>
					<label class={labelClass}>
						<span class={labelTextClass}>Puerto</span>
						<input
							class={inputClass}
							type="number"
							min="1"
							max="65535"
							bind:value={form.smtp_port}
						/>
					</label>
					<label class={labelClass}>
						<span class={labelTextClass}>Seguridad</span>
						<select class={inputClass} bind:value={form.smtp_security}>
							<option value="tls">STARTTLS (587)</option>
							<option value="ssl">SSL (465)</option>
							<option value="none">Ninguna</option>
						</select>
					</label>
					<label class={labelClass}>
						<span class={labelTextClass}>Usuario</span>
						<input class={inputClass} bind:value={form.smtp_username} />
					</label>
					<label class={labelClass}>
						<span class={labelTextClass}>
							Contraseña {form.smtp_password_set ? '(guardada; deja vacío para no cambiar)' : ''}
						</span>
						<input
							class={inputClass}
							type="password"
							autocomplete="new-password"
							bind:value={smtpPassword}
						/>
					</label>
					<label class={labelClass}>
						<span class={labelTextClass}>Correo remitente</span>
						<input class={inputClass} type="email" bind:value={form.smtp_from_email} />
					</label>
					<label class={labelClass}>
						<span class={labelTextClass}>Nombre remitente</span>
						<input class={inputClass} bind:value={form.smtp_from_name} />
					</label>
				</div>

				<div class="mt-3 flex flex-wrap items-end gap-2">
					<label class={labelClass + ' flex-1'}>
						<span class={labelTextClass}>Enviar prueba a</span>
						<input
							class={inputClass}
							type="email"
							bind:value={testDestino}
							placeholder="tu@correo.com"
						/>
					</label>
					<Button variant="secondary" onclick={testSmtp} disabled={testing}>
						{testing ? 'Enviando…' : 'Probar'}
					</Button>
				</div>
				{#if testMessage}<div class="mt-2">
						<InlineAlert tone="success">{testMessage}</InlineAlert>
					</div>{/if}
				{#if testError}<div class="mt-2">
						<InlineAlert tone="error">{testError}</InlineAlert>
					</div>{/if}
			</div>

			<div class="flex justify-end">
				<Button variant="primary" onclick={save} disabled={saving}
					>{saving ? 'Guardando…' : 'Guardar cambios'}</Button
				>
			</div>
		</div>
	{/if}
{/if}
